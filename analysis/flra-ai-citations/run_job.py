#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered FLRA archive AI-citation census (census 1.0.1).

Order enforced here:
1. wait until analysis/flra-ai-citations/PLAN.md, AMENDMENT-1.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. download the AI Hallucination Cases Database CSV (for the coverage check only);
3. build the frame from the FLRA's own decision list; stop before any decision text is
   fetched if it holds fewer than 20 decisions or if the list never reached the frame's
   start date (AMENDMENT-1);
4. fetch each decision page, DELAY_S seconds apart, extract its main text, classify, grade.

Texts and excerpts stay in out/private/ and are never published.
"""
from __future__ import annotations

import argparse
import hashlib
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
DIR = "analysis/flra-ai-citations"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
DELAY_S = 3
EMPTY_RETRY_S = 60
MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 150


def get(url, timeout=120, limit=MAX_BYTES):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit), r.headers.get("Content-Type", "")


def get_retry(url, tries=3, timeout=120):
    err = None
    for i in range(tries):
        try:
            return get(url, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404, 410):
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
    """(plan, amendment, code, committed_sha) once all are public and census.py matches; else Nones."""
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            plan = commits_for(DIR + "/PLAN.md")
            amend = commits_for(DIR + "/AMENDMENT-1.md")
            code = commits_for(DIR + "/census.py")
            if plan and amend and code:
                committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py" % (REPO, code[0]["sha"], DIR))[0]
                if norm_sha(committed) == local_sha:
                    return plan[-1], amend[-1], code[0], norm_sha(committed)
                print(census.now(), "newest committed census.py differs from local; waiting", flush=True)
            else:
                print(census.now(), "plan or amendment not public yet", flush=True)
        except Exception as exc:
            print(census.now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None, None, None
        time.sleep(step_minutes * 60)


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def listing_page(page):
    """(rows, body) for one listing page; an empty or failed page is tried once more."""
    body, rows, err = b"", [], None
    for attempt in range(2):
        if attempt:
            time.sleep(EMPTY_RETRY_S)
        try:
            body = get_retry(census.FLRA_LIST % page)[0]
            err = None
        except Exception as exc:
            body, err = b"", exc
            continue
        rows = census.parse_flra_listing(body.decode("utf-8", "replace"))
        if rows:
            break
    return rows, body, err


def build_frame(priv, log, max_pages=MAX_PAGES):
    """(frame, pages, undated, reached_start). Two empty pages in a row end the listing."""
    frame, seen, pages, undated, empty_run, reached = [], set(), 0, 0, 0, False
    for page in range(max_pages):
        if page:
            time.sleep(DELAY_S)
        rows, body, err = listing_page(page)
        pages += 1
        if page == 0 and body:
            with open(os.path.join(priv, "listing_page0.html"), "wb") as fh:
                fh.write(body)
        if not rows:
            empty_run += 1
            log.append("listing page %d: no rows parsed%s" % (page, (" (%s)" % err) if err else ""))
            if body:
                with open(os.path.join(priv, "listing_empty_%d.html" % page), "wb") as fh:
                    fh.write(body)
            if empty_run >= 2:
                log.append("two empty listing pages in a row; listing stopped")
                break
            continue
        empty_run = 0
        dated = [r for r in rows if r["date"]]
        undated += len(rows) - len(dated)
        for r in rows:
            if r["citation"] in seen:
                continue
            seen.add(r["citation"])
            if census.in_window(r["date"]):
                frame.append(r)
        if dated and all(r["date"] < census.START for r in dated):
            reached = True
            log.append("reached %s on page %d" % (census.START, page))
            break
    no_html = sum(1 for r in frame if not r["url"])
    log.append("%d listing pages, %d in frame (%d without an HTML link), %d undated listing rows"
               % (pages, len(frame), no_html, undated))
    return frame, pages, undated, reached


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
    plan, amend, code, committed_sha = wait_for_plan(args.wait_minutes, local_sha)
    status["census_sha256_local"] = local_sha
    if not plan:
        status["result"] = "stopped: PLAN.md, AMENDMENT-1.md and a matching census.py not public; nothing downloaded"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "amendment_commit": amend, "census_commit": code,
                   "census_sha256_committed": committed_sha})

    sources = {"plan_commit": plan, "amendment_commit": amend, "census_commit": code}
    dbrows = None
    try:
        data = get_retry(CSV_URL, timeout=300)[0]
        with open(os.path.join(priv, "download.csv"), "wb") as fh:
            fh.write(data)
        sources["database"] = {"url": CSV_URL, "fetched_at": census.now(), "bytes": len(data),
                               "sha256": hashlib.sha256(data).hexdigest(),
                               "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}
        dbrows = census.db_rows(data.decode("utf-8-sig", "replace"))
        status["db_flra_rows"] = len(dbrows)
    except Exception as exc:
        status["log"].append("database CSV failed: %s" % exc)
        sources["database"] = {"url": CSV_URL, "error": str(exc)}

    rows, pages, undated, reached = build_frame(priv, status["log"])
    sources["flra"] = {"listing": census.FLRA_LIST % 0, "listing_pages": pages, "in_frame": len(rows),
                       "without_html_link": sum(1 for r in rows if not r["url"]),
                       "undated_listing_rows": undated, "reached_start": reached, "built_at": census.now()}
    with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
        json.dump(sources, fh, indent=1)
    if len(rows) < 20:
        status["result"] = "stopped: frame holds %d decisions (listing parser); no decision text fetched" % len(rows)
        return finish(args.out_dir, status, 6)
    if not reached:
        status["result"] = "stopped: listing never reached %s, frame incomplete; no decision text fetched" % census.START
        return finish(args.out_dir, status, 7)
    status["in_frame"] = len(rows)
    print(census.now(), "frame:", len(rows), flush=True)

    excerpts = []
    prog = open(os.path.join(priv, "progress.jsonl"), "w", encoding="utf-8")
    for i, r in enumerate(rows):
        if not r["url"]:
            r["doc_status"], r["readable"] = "no_html_link", False
            continue
        time.sleep(DELAY_S)
        try:
            body, _ = get_retry(r["url"], timeout=120)
        except urllib.error.HTTPError as exc:
            r["doc_status"] = "http_%s" % exc.code
            continue
        except Exception as exc:
            r["doc_status"] = "fetch_error"
            print("fetch error", r["url"], exc, flush=True)
            continue
        r["doc_sha256"] = hashlib.sha256(body).hexdigest()
        try:
            text = census.main_text(body.decode("utf-8", "replace"))
            r["doc_status"] = "ok"
        except Exception as exc:
            text, r["doc_status"] = "", "extract_error"
            print("extract error", r["url"], exc, flush=True)
        r.update(census.classify(text))
        r["readable"] = r["doc_status"] == "ok" and r["chars"] >= 1500
        if r.get("ai_mention"):
            with open(os.path.join(priv, "texts", "v%d_%d.txt" % (r["volume"], r["number"])), "w", encoding="utf-8") as fh:
                fh.write(text)
        for key, ex in sorted(r.pop("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s\n%s\n" % (r["citation"], r.get("date"), key, ex))
        prog.write(json.dumps({k: r.get(k) for k in ("citation", "date", "doc_status", "chars") + census.FLAG_KEYS}) + "\n")
        prog.flush()
        if r.get("ai_mention") or i % 50 == 0:
            print(census.now(), i + 1, "/", len(rows), r["citation"], r.get("date"), r["doc_status"], r.get("chars"),
                  sorted(k for k in census.FLAG_KEYS if r.get(k)), flush=True)
    prog.close()

    if dbrows is not None:
        census.match_db(rows, dbrows)
    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    res = census.grade(rows)
    if dbrows is None:
        res["predictions"]["P2"].update({"verdict": "not testable", "detail": {"reason": "database CSV not downloaded"}})
    res["sources"] = sources
    for fname, payload in (("results.json", json.dumps(res, indent=1)),
                           ("results.md", census.results_md(res, sources)),
                           ("rows.csv", census.rows_csv(rows))):
        with open(os.path.join(args.out_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(payload)
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    status["counts"] = {k: v for k, v in res["counts"].items() if k != "by_year"}
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
