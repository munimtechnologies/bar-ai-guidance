#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered NLRB fabricated-citation census (census 1.0.0).

Order enforced here:
1. wait until analysis/nlrb-citations/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. download the AI Hallucination Cases Database CSV (for P5);
3. read the NLRB's public Board-decisions listing (www.nlrb.gov, newest first) until a page holds
   only decisions dated before FRAME_START, and build the frame; stop before any decision is
   fetched if the listing failed or was not completed, if the frame holds fewer than MIN_FRAME or
   more than MAX_FRAME decisions, or if too many rows lack a document id;
4. for each decision: fetch its PDF from nlrbresearch.com's mirror of the NLRB document (one
   request at a time, DELAY_S seconds apart), classify it, grade. Stop politely after
   MAX_CONSECUTIVE_FAILURES failures in a row.

Names, texts and excerpts stay in out/private/.
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
DIR = "analysis/nlrb-citations"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
DELAY_S = 5
MAX_BYTES = 60 * 1024 * 1024
MAX_CONSECUTIVE_FAILURES = 15
MAX_PAGES = 30


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
        time.sleep(30 * (i + 1))
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
    """(decisions in the frame, listing info, failed: 0 or 1). A citation seen before is skipped."""
    fetch = fetch or (lambda u: get_retry(u, timeout=180, accept="text/html")[0])
    info = {"listing": census.LISTING, "frame_start": census.FRAME_START, "pages": 0, "complete": False,
            "page_sha256": []}
    items = []
    for page in range(MAX_PAGES):
        if page > 0:
            time.sleep(DELAY_S)
        url = census.listing_url(page)
        try:
            body = fetch(url)
        except Exception as exc:
            log.append("listing page %d failed: %s" % (page, str(exc)[:200]))
            info["error"] = "page %d: %s" % (page, str(exc)[:200])
            return [], info, 1
        got = census.parse_rows(body)
        info["pages"] += 1
        info["page_sha256"].append(hashlib.sha256(body if isinstance(body, bytes) else body.encode("utf-8"))
                                   .hexdigest())
        if not got and page == 0:
            log.append("listing page 0 has no rows")
            info["error"] = "page 0 has no rows"
            return [], info, 1
        items.extend(got)
        if census.page_done(got):
            info["complete"] = True
            break
    info["fetched_at"] = census.now()
    docs, seen, dup = [], set(), 0
    for e in items:
        if e["key"] in seen:
            dup += 1
            continue
        seen.add(e["key"])
        if not census.in_window(e):
            continue
        e["known"] = e["key"] in census.KNOWN
        docs.append(e)
    by_year, by_volume = {}, {}
    for d in docs:
        y, v = d["date"][:4], str(d["volume"])
        by_year[y] = by_year.get(y, 0) + 1
        by_volume[v] = by_volume.get(v, 0) + 1
    info.update({"rows_read": len(items), "same_citation_skipped": dup, "in_frame": len(docs),
                 "outside_window": len(seen) - len(docs),
                 "no_doc_in_frame": sum(1 for d in docs if not d["doc"]),
                 "no_case_in_frame": sum(1 for d in docs if not d["case"]),
                 "known_in_frame": sum(1 for d in docs if d["known"]),
                 "in_frame_by_year": dict(sorted(by_year.items())),
                 "in_frame_by_volume": dict(sorted(by_volume.items()))})
    log.append("listing: %d rows read on %d pages, %d in frame" % (len(items), info["pages"], len(docs)))
    return docs, info, 0


def pdf_text(data):
    """(pages, text)."""
    from pypdf import PdfReader  # installed by the job's setup step
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages[:300]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return len(reader.pages), "\n".join(parts)


def fetch_pdf(url):
    """(pdf bytes or None, status)."""
    if not url:
        return None, "no_doc"
    try:
        body = get_retry(url, timeout=180)[0]
    except urllib.error.HTTPError as exc:
        return None, "http_%s" % exc.code
    except Exception:
        return None, "error"
    if body.lstrip()[:5] != b"%PDF-":
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
        status["db_nlrb_rows"] = len(db["nlrb_rows"])
    except Exception as exc:
        status["log"].append("database CSV failed: %s" % exc)
        sources["database"] = {"url": CSV_URL, "error": str(exc)}

    docs, info, failed = build_frame(status["log"])
    sources["nlrb"] = {"listing": census.LISTING, "mirror": census.MIRROR, "failed": failed, "in_frame": len(docs),
                       "built_at": census.now()}
    with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
        json.dump(sources, fh, indent=1)
    with open(os.path.join(args.out_dir, "listing.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
    with open(os.path.join(priv, "frame.json"), "w", encoding="utf-8") as fh:
        json.dump(docs, fh, indent=1)
    if failed:
        status["result"] = "stopped: the listing failed; no decision fetched"
        return finish(args.out_dir, status, 5)
    if not info["complete"]:
        status["result"] = "stopped: the listing did not reach %s within %d pages; no decision fetched" % (
            census.FRAME_START, MAX_PAGES)
        return finish(args.out_dir, status, 4)
    if len(docs) < census.MIN_FRAME:
        status["result"] = "stopped: frame holds %d decisions; no decision fetched" % len(docs)
        return finish(args.out_dir, status, 6)
    if len(docs) > census.MAX_FRAME:
        status["result"] = "stopped: frame holds %d decisions (over %d); no decision fetched" % (
            len(docs), census.MAX_FRAME)
        return finish(args.out_dir, status, 8)
    if info["no_doc_in_frame"] > census.MAX_NO_DOC:
        status["result"] = "stopped: %d frame decisions lack a document id; no decision fetched" % (
            info["no_doc_in_frame"])
        return finish(args.out_dir, status, 7)
    status["in_frame"] = len(docs)
    print(census.now(), "frame:", len(docs), flush=True)

    excerpts, fails = [], 0
    prog = open(os.path.join(priv, "progress.jsonl"), "w", encoding="utf-8")
    for i, d in enumerate(docs):
        url = census.mirror_url(d.get("doc"))
        if url:
            time.sleep(DELAY_S)
        data, d["pdf_status"] = fetch_pdf(url)
        text = ""
        if data is None:
            fails += 1
            if fails >= MAX_CONSECUTIVE_FAILURES:
                prog.close()
                status["result"] = "stopped: %d decisions failed in a row at %d of %d" % (fails, i + 1, len(docs))
                return finish(args.out_dir, status, 9)
        else:
            fails = 0
            d["pdf_sha256"] = hashlib.sha256(data).hexdigest()
            try:
                d["pages"], raw = pdf_text(data)
                text = census.normalize(raw)
            except Exception as exc:
                text, d["pdf_status"] = "", "extract_error"
                print("extract error", d["key"], exc, flush=True)
        res = census.classify(text)
        d["chars"] = res["chars"]
        d["readable"] = d["pdf_status"] == "ok" and res["chars"] >= census.READABLE_CHARS
        for k in census.FLAG_KEYS + census.RECORD_KEYS:
            d[k] = res[k]
        d["in_db"] = census.in_db(db, d)
        flagged = any(d.get(k) for k in census.FLAG_KEYS)
        if flagged:
            with open(os.path.join(priv, "texts", "%s.txt" % d["key"]), "w", encoding="utf-8") as fh:
                fh.write("NAME: %s\nCASE: %s\n\nTEXT:\n%s\n" % (d.get("name", ""), d.get("case", ""), text))
        for key, ex in sorted(res["excerpts"].items()):
            excerpts.append("== %s | %s | %s\n%s\n" % (d["key"], d.get("date"), key, ex))
        prog.write(json.dumps({k: d.get(k) for k in ("key", "pdf_status", "chars") + census.FLAG_KEYS}) + "\n")
        prog.flush()
        if flagged or i % 50 == 0:
            print(census.now(), i + 1, "/", len(docs), d["key"], d["pdf_status"],
                  sorted(k for k in census.FLAG_KEYS if d.get(k)), flush=True)
    prog.close()

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(priv, "frame.json"), "w", encoding="utf-8") as fh:
        json.dump(docs, fh, indent=1)
    res = census.grade(docs, db, info)
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
