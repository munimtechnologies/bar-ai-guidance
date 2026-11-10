#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered MSPB fabricated-citation census (census 1.0.0).

Order enforced here:
1. wait until analysis/mspb-citations/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. download the AI Hallucination Cases Database CSV (for P8 only);
3. read the MSPB decision-listing manifests and build the frame; stop before any PDF is
   fetched if a main manifest failed, or if the frame holds fewer than MIN_FRAME or more
   than MAX_FRAME decisions;
4. fetch each decision PDF (one request at a time, DELAY_S seconds apart), extract text,
   classify, grade. Stop politely after MAX_CONSECUTIVE_FAILURES failed fetches in a row
   (a 404 neither counts nor resets the run of failures).

Texts and excerpts stay in out/private/ and are never published.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/mspb-citations"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
DELAY_S = 3
MAX_BYTES = 60 * 1024 * 1024
MAX_CONSECUTIVE_FAILURES = 25


def get(url, timeout=120, limit=MAX_BYTES, accept="*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit), r.headers.get("Content-Type", "")


def get_retry(url, tries=3, timeout=120, accept="*/*"):
    err = None
    for i in range(tries):
        try:
            return get(url, timeout=timeout, accept=accept)
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 403, 404, 410):
                raise
            err = exc
        except Exception as exc:
            err = exc
        time.sleep(20 * (i + 1))
    raise err


def norm_sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url)[0].decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def wait_for_plan(max_minutes, local_sha, step_minutes=5):
    """(plan, code, committed_sha) once both are public and census.py matches; else Nones."""
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            plan = commits_for(DIR + "/PLAN.md")
            code = commits_for(DIR + "/census.py")
            if plan and code:
                committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py" % (REPO, code[0]["sha"], DIR))[0]
                if norm_sha(committed) == local_sha:
                    return plan[-1], code[0], norm_sha(committed)
                print(census.now(), "newest committed census.py differs from local; waiting", flush=True)
            else:
                print(census.now(), "plan or census.py not public yet", flush=True)
        except Exception as exc:
            print(census.now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None, None
        time.sleep(step_minutes * 60)


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def build_frame(priv, log):
    """(frame dict, manifest table, main_failed). Main manifests first, then the extra ones."""
    frame, table, main_failed = {}, [], 0
    for i, path in enumerate(census.MAIN_MANIFESTS + census.EXTRA_MANIFESTS):
        if i:
            time.sleep(DELAY_S)
        main = path in census.MAIN_MANIFESTS
        row = {"manifest": path, "main": main}
        try:
            body = get_retry(census.BASE + path, timeout=300, accept="application/json")[0]
            row["bytes"] = len(body)
            row["sha256"] = hashlib.sha256(body).hexdigest()
            rows, stats = census.parse_manifest(body, path)
            row.update(stats)
            row["in_window"] = census.merge(frame, rows, path)
        except Exception as exc:
            row["error"] = str(exc)[:200]
            log.append("manifest failed: %s: %s" % (path, row["error"]))
            if main:
                main_failed += 1
        table.append(row)
    log.append("%d manifests, %d main failed, %d decisions in frame" % (len(table), main_failed, len(frame)))
    return frame, table, main_failed


def pdf_text(data):
    from pypdf import PdfReader  # installed by the job's setup step
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages[:300]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def fetch_document(d):
    """(pdf bytes or None, status) for one frame decision."""
    try:
        body = get_retry(census.pdf_url(d["collection"], d["file_name"]), timeout=180)[0]
    except urllib.error.HTTPError as exc:
        return None, "pdf_http_%s" % exc.code
    except Exception:
        return None, "pdf_error"
    if not body.lstrip()[:5] == b"%PDF-":
        return None, "not_pdf"
    return body, "ok"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=120)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "texts"), exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION, "log": []}

    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local_sha = norm_sha(fh.read())
    plan, code, committed_sha = wait_for_plan(args.wait_minutes, local_sha)
    status["census_sha256_local"] = local_sha
    if not plan:
        status["result"] = "stopped: PLAN.md and a matching census.py not public; nothing downloaded"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "census_commit": code, "census_sha256_committed": committed_sha})

    sources = {"plan_commit": plan, "census_commit": code}
    db = None
    try:
        data = get_retry(CSV_URL, timeout=300)[0]
        with open(os.path.join(priv, "download.csv"), "wb") as fh:
            fh.write(data)
        sources["database"] = {"url": CSV_URL, "fetched_at": census.now(), "bytes": len(data),
                               "sha256": hashlib.sha256(data).hexdigest(),
                               "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}
        db = census.db_check(data.decode("utf-8-sig", "replace"))
        status["db_court_rows"] = len(db["court_rows"])
    except Exception as exc:
        status["log"].append("database CSV failed: %s" % exc)
        sources["database"] = {"url": CSV_URL, "error": str(exc)}

    frame, table, main_failed = build_frame(priv, status["log"])
    docs = sorted(frame.values(), key=lambda d: (d["date"] or "", d["row_id"]))
    sources["mspb"] = {"base": census.BASE, "manifests": len(table), "main_failed": main_failed,
                       "in_frame": len(docs), "built_at": census.now()}
    with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
        json.dump(sources, fh, indent=1)
    with open(os.path.join(args.out_dir, "manifests.json"), "w", encoding="utf-8") as fh:
        json.dump(table, fh, indent=1)
    if main_failed:
        status["result"] = "stopped: %d main manifest(s) failed; no PDF fetched" % main_failed
        return finish(args.out_dir, status, 5)
    if len(docs) < census.MIN_FRAME:
        status["result"] = "stopped: frame holds %d decisions; no PDF fetched" % len(docs)
        return finish(args.out_dir, status, 6)
    if len(docs) > census.MAX_FRAME:
        status["result"] = "stopped: frame holds %d decisions (over %d); no PDF fetched" % (len(docs), census.MAX_FRAME)
        return finish(args.out_dir, status, 8)
    status["in_frame"] = len(docs)
    print(census.now(), "frame:", len(docs), flush=True)

    excerpts, fails = [], 0
    prog = open(os.path.join(priv, "progress.jsonl"), "w", encoding="utf-8")
    for i, d in enumerate(docs):
        time.sleep(DELAY_S)
        body, d["doc_status"] = fetch_document(d)
        d["readable"] = False
        if body is None:
            if d["doc_status"] != "pdf_http_404":  # a missing file is a listing error, not a block
                fails += 1
            prog.write(json.dumps({"row_id": d["row_id"], "doc_status": d["doc_status"]}) + "\n")
            if fails >= MAX_CONSECUTIVE_FAILURES:
                prog.close()
                status["result"] = "stopped: %d PDF fetches failed in a row at decision %d of %d" % (fails, i + 1, len(docs))
                return finish(args.out_dir, status, 9)
            continue
        fails = 0
        d["pdf_sha256"] = hashlib.sha256(body).hexdigest()
        try:
            text = pdf_text(body)
        except Exception as exc:
            text, d["doc_status"] = "", "extract_error"
            print("extract error", d["row_id"], exc, flush=True)
        d.update(census.classify(text))
        d["readable"] = d["doc_status"] == "ok" and d["chars"] >= census.READABLE_CHARS
        if d.get("fake_cite") or d.get("ai_mention"):
            with open(os.path.join(priv, "texts", "%s.txt" % d["row_id"]), "w", encoding="utf-8") as fh:
                fh.write(text)
        for key, ex in sorted(d.pop("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s | %s | %s\n%s\n" % (d["row_id"], d["docket"], d.get("date"), d["kind"], key, ex))
        prog.write(json.dumps({k: d.get(k) for k in ("row_id", "date", "kind", "doc_status", "chars")
                               + census.FLAG_KEYS}) + "\n")
        prog.flush()
        if d.get("fake_cite") or d.get("ai_mention") or i % 100 == 0:
            print(census.now(), i + 1, "/", len(docs), d["docket"], d.get("date"), d["doc_status"], d.get("chars"),
                  sorted(k for k in census.FLAG_KEYS if d.get(k)), flush=True)
    prog.close()

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(priv, "file_names.json"), "w", encoding="utf-8") as fh:
        json.dump({d["row_id"]: d["file_name"] for d in docs if d.get("fake_cite") or d.get("ai_mention")}, fh, indent=1)
    res = census.grade(docs, db, table)
    res["sources"] = sources
    for fname, payload in (("results.json", json.dumps(res, indent=1, default=str)),
                           ("results.md", census.results_md(res, sources)),
                           ("rows.csv", census.rows_csv(docs))):
        with open(os.path.join(args.out_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(payload)
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    status["counts"] = {k: v for k, v in res["counts"].items() if k != "by_year"}
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
