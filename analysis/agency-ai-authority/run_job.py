#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered agency AI-authority census (census 1.0.0).

Order enforced here:
1. wait until analysis/agency-ai-authority/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance, and check that the census.py next to this file is
   identical (line endings aside) to the newest committed one;
2. only then download the database CSV (SHA-256 and time recorded) and select the rows;
3. fetch each linked decision document, DELAY_S seconds apart, extract its text and grade.

Raw CSV, documents, texts and excerpts stay in out/private/ and are never published.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/agency-ai-authority"
CSV_URL = census.SITE + "/hallucinations/hallucinations/download.csv"
DELAY_S = 5
MAX_BYTES = 20 * 1024 * 1024


def get(url, timeout=120, limit=MAX_BYTES):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit), r.headers.get("Content-Type", "")


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url)[0].decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def wait_for_plan(max_minutes, step_minutes=5):
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            plan = commits_for(DIR + "/PLAN.md")
            code = commits_for(DIR + "/census.py")
            if plan and code:
                return plan[-1], code[0]
            print(census.now(), "plan not public yet", flush=True)
        except Exception as exc:
            print(census.now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None
        time.sleep(step_minutes * 60)


def pdf_text(data):
    from pypdf import PdfReader  # pinned in the job's setup step
    import io
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception as exc:  # one bad page must not lose the document
            parts.append("")
            print("page extract failed:", exc, flush=True)
    return "\n".join(parts)


def html_text(data):
    s = data.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return html.unescape(s)


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=240)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(priv, exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION}

    plan, code = wait_for_plan(args.wait_minutes)
    if not plan:
        status["result"] = "stopped: PLAN.md not public; data NOT downloaded"
        return finish(args.out_dir, status, 3)
    committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py" % (REPO, code["sha"], DIR))[0]
    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local = fh.read()
    status.update({"plan_commit": plan, "census_commit": code,
                   "census_sha256_committed": norm_sha(committed), "census_sha256_local": norm_sha(local)})
    if norm_sha(committed) != norm_sha(local):
        status["result"] = "stopped: local census.py differs from the committed one; data NOT downloaded"
        return finish(args.out_dir, status, 4)

    data, err = None, None
    for _ in range(3):
        try:
            data = get(CSV_URL, timeout=300)[0]
            break
        except Exception as exc:
            err = str(exc)
            time.sleep(30)
    if data is None:
        status["result"] = "stopped: CSV download failed: %s" % err
        return finish(args.out_dir, status, 5)
    with open(os.path.join(priv, "download.csv"), "wb") as fh:
        fh.write(data)
    source = {"url": CSV_URL, "fetched_at": census.now(), "bytes": len(data),
              "sha256": hashlib.sha256(data).hexdigest(),
              "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin",
              "plan_commit": plan, "census_commit": code}
    with open(os.path.join(args.out_dir, "source.json"), "w", encoding="utf-8") as fh:
        json.dump(source, fh, indent=1)

    rows, courts = census.select_rows(data.decode("utf-8-sig", "replace"))
    with open(os.path.join(args.out_dir, "court_values.json"), "w", encoding="utf-8") as fh:
        json.dump(courts, fh, indent=1)
    status["rows_in_scope"] = len(rows)
    print(census.now(), "rows in scope:", len(rows), flush=True)

    excerpts = []
    for i, r in enumerate(rows):
        if not r["url"]:
            r["doc_status"] = "no_document"
            continue
        if i:
            time.sleep(DELAY_S)
        try:
            body, ctype = get(r["url"], timeout=90)
        except urllib.error.HTTPError as exc:
            r["doc_status"] = "http_%s" % exc.code
            continue
        except Exception as exc:
            r["doc_status"] = "fetch_error"
            print("fetch error", r["case_id"], exc, flush=True)
            continue
        r["doc_sha256"] = hashlib.sha256(body).hexdigest()
        try:
            if body[:5] == b"%PDF-":
                text = pdf_text(body)
            elif b"<html" in body[:2000].lower() or "html" in ctype:
                text = html_text(body)
            else:
                text = ""
            r["doc_status"] = "ok"
        except Exception as exc:
            text = ""
            r["doc_status"] = "extract_error"
            print("extract error", r["case_id"], exc, flush=True)
        with open(os.path.join(priv, "%s.txt" % r["case_id"]), "w", encoding="utf-8") as fh:
            fh.write(text)
        r.update(census.classify_text(r["forum"], text))
        for key, ex in sorted(r.get("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s | %s | %s | %s\n%s\n" % (
                r["case_id"], r["forum"], r["date"], key, r["court"], r["case_name"], ex))
        print(census.now(), i + 1, "/", len(rows), r["case_id"], r["forum"], r["doc_status"],
              r.get("chars"), sorted(k for k in census.FLAG_KEYS if r.get(k)), flush=True)

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(priv, "rows_named.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)
    res = census.grade(rows)
    res["source"] = source
    with open(os.path.join(args.out_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    with open(os.path.join(args.out_dir, "results.md"), "w", encoding="utf-8") as fh:
        fh.write(census.results_md(res, source))
    with open(os.path.join(args.out_dir, "rows.csv"), "w", encoding="utf-8") as fh:
        fh.write(census.rows_csv(rows))
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
