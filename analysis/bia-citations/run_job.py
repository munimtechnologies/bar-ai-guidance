#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered BIA / A.G. precedent fabricated-citation census (census 1.0.0).

Order enforced here:
1. wait until analysis/bia-citations/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. download the AI Hallucination Cases Database CSV (for P7, P8);
3. read EOIR's listing pages for volumes 28-30 and build the frame; stop before any decision is
   fetched if a page failed, if the frame holds fewer than MIN_FRAME or more than MAX_FRAME
   decisions, or if more than MAX_UNPARSED entries have no citation or no link;
4. fetch each decision (one request at a time, DELAY_S seconds apart, as justice.gov's
   robots.txt asks), extract text, classify, grade. Stop politely after
   MAX_CONSECUTIVE_FAILURES failed decisions in a row.

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
DIR = "analysis/bia-citations"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
DELAY_S = 10                    # justice.gov robots.txt: Crawl-delay: 10
MAX_BYTES = 60 * 1024 * 1024
MAX_CONSECUTIVE_FAILURES = 15
MAX_UNPARSED = 15


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


def build_frame(log, fetch=None):
    """(docs, listing table, failed pages)."""
    fetch = fetch or (lambda u: get_retry(u, timeout=180, accept="text/html")[0])
    docs, table, failed, seen = [], [], 0, set()
    for i, vol in enumerate(census.VOLUMES):
        if i:
            time.sleep(DELAY_S)
        url = census.PAGE_URL % vol
        row = {"volume": vol, "url": url}
        try:
            body = fetch(url)
            row["bytes"] = len(body)
            row["sha256"] = hashlib.sha256(body).hexdigest()
            entries = census.parse_listing(body, vol, url)
            row.update({"entries": len(entries), "no_cite": sum(1 for e in entries if not e["cite"]),
                        "no_link": sum(1 for e in entries if not e["links"]), "gaps": census.id_gaps(entries)})
            for e in entries:
                if e["id"] not in seen:
                    seen.add(e["id"])
                    docs.append(e)
        except Exception as exc:
            row["error"] = str(exc)[:200]
            failed += 1
            log.append("listing failed: %s: %s" % (url, row["error"]))
        table.append(row)
    log.append("%d pages, %d failed, %d decisions in frame" % (len(table), failed, len(docs)))
    return docs, table, failed


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
    """(pdf bytes or None, status, url). Tries the entry's links in order until one is a PDF."""
    last = "no_link"
    for i, url in enumerate(d.get("links") or []):
        if i:
            time.sleep(DELAY_S)
        try:
            body = get_retry(url, timeout=180)[0]
        except urllib.error.HTTPError as exc:
            last = "http_%s" % exc.code
            continue
        except Exception:
            last = "error"
            continue
        if body.lstrip()[:5] == b"%PDF-":
            return body, "ok", url
        last = "not_pdf"
    return None, last, ""


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

    docs, table, failed = build_frame(status["log"])
    docs.sort(key=lambda d: d["id"])
    sources["eoir"] = {"pages": [census.PAGE_URL % v for v in census.VOLUMES], "failed": failed,
                       "in_frame": len(docs), "built_at": census.now()}
    with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
        json.dump(sources, fh, indent=1)
    with open(os.path.join(args.out_dir, "listing.json"), "w", encoding="utf-8") as fh:
        json.dump(table, fh, indent=1)
    cites_seen, unparsed = set(), 0
    for d in docs:
        if not d["cite"] or not d["links"] or d["cite"] in cites_seen:   # a repeated citation means a mis-paired entry
            unparsed += 1
        cites_seen.add(d["cite"])
    if failed:
        status["result"] = "stopped: %d listing page(s) failed; no decision fetched" % failed
        return finish(args.out_dir, status, 5)
    if len(docs) < census.MIN_FRAME:
        status["result"] = "stopped: frame holds %d decisions; no decision fetched" % len(docs)
        return finish(args.out_dir, status, 6)
    if len(docs) > census.MAX_FRAME:
        status["result"] = "stopped: frame holds %d decisions (over %d); no decision fetched" % (len(docs), census.MAX_FRAME)
        return finish(args.out_dir, status, 8)
    if unparsed > MAX_UNPARSED:
        status["result"] = "stopped: %d entries lack a citation or a link; no decision fetched" % unparsed
        return finish(args.out_dir, status, 7)
    status["in_frame"] = len(docs)
    status["unparsed"] = unparsed
    print(census.now(), "frame:", len(docs), "unparsed:", unparsed, flush=True)

    excerpts, fails, shas = [], 0, {}
    prog = open(os.path.join(priv, "progress.jsonl"), "w", encoding="utf-8")
    for i, d in enumerate(docs):
        time.sleep(DELAY_S)
        body, d["doc_status"], d["url"] = fetch_document(d)
        d["readable"] = False
        if body is None:
            if d["doc_status"] != "no_link":
                fails += 1
            prog.write(json.dumps({"id": d["id"], "doc_status": d["doc_status"]}) + "\n")
            if fails >= MAX_CONSECUTIVE_FAILURES:
                prog.close()
                status["result"] = "stopped: %d decisions failed in a row at %d of %d" % (fails, i + 1, len(docs))
                return finish(args.out_dir, status, 9)
            continue
        fails = 0
        d["pdf_sha256"] = hashlib.sha256(body).hexdigest()
        shas.setdefault(d["pdf_sha256"], []).append(d["id"])
        try:
            text = pdf_text(body)
        except Exception as exc:
            text, d["doc_status"] = "", "extract_error"
            print("extract error", d["id"], exc, flush=True)
        d.update(census.classify(text))
        d["readable"] = d["doc_status"] == "ok" and d["chars"] >= census.READABLE_CHARS
        if d.get("fake_cite") or d.get("ai_mention") or d.get("pm2540") or d.get("discipline"):
            with open(os.path.join(priv, "texts", "%d.txt" % d["id"]), "w", encoding="utf-8") as fh:
                fh.write(text)
        for key, ex in sorted(d.pop("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s | %s\n%s\n" % (d["id"], d["cite"], d.get("year"), key, ex))
        prog.write(json.dumps({k: d.get(k) for k in ("id", "cite", "doc_status", "chars") + census.FLAG_KEYS}) + "\n")
        prog.flush()
        if d.get("fake_cite") or d.get("ai_mention") or i % 50 == 0:
            print(census.now(), i + 1, "/", len(docs), d["cite"], d["doc_status"], d.get("chars"),
                  sorted(k for k in census.FLAG_KEYS if d.get(k)), flush=True)
    prog.close()

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    res = census.grade(docs, db, table)
    res["sources"] = sources
    res["counts"]["same_pdf_for_several_ids"] = {k[:12]: v for k, v in shas.items() if len(v) > 1}
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
