#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered EO 14434 terminology census (census 1.0.0).

Order enforced here:
1. wait until analysis/si-rename-census/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. run the Federal Register full-text searches for every term and window of the wave and build
   the frame; stop before any document text is fetched if a search failed or the frame is too
   small or too large;
3. fetch each document's plain text (one request at a time, DELAY_S seconds apart), classify,
   take the eCFR snapshot, grade. Stop politely after MAX_CONSECUTIVE_FAILURES failures in a row.

Federal Register documents are public; short excerpts stay in out/private/ only because they are
working notes for the hand review.
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
DIR = "analysis/si-rename-census"
MAX_BYTES = 80 * 1024 * 1024
MAX_CONSECUTIVE_FAILURES = 15
W2_EARLIEST_RUN = "2026-12-12"


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


def get_json(url):
    return json.loads(get_retry(url, accept="application/json")[0].decode("utf-8"))


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


def _default(o):
    return sorted(o) if isinstance(o, set) else str(o)


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=_default)
    print(json.dumps(status, default=_default)[:4000])
    return rc


def search_all(windows, log, fetch=None, sleep=time.sleep):
    """({document_number: doc}, query info, failed searches, truncated searches)."""
    fetch = fetch or get_json
    docs, queries, failed, truncated = {}, [], 0, 0
    first = True
    for w in windows:
        a, b = census.WINDOWS[w]
        for term in census.TERMS:
            page, pages, count, rows = 1, 1, None, 0
            while page <= pages:
                if page > census.MAX_PAGES:
                    truncated += 1
                    log.append("search truncated: %s %s" % (w, term))
                    break
                if not first:
                    sleep(census.DELAY_S)
                first = False
                try:
                    obj = fetch(census.search_url(term, a, b, page))
                except Exception as exc:
                    failed += 1
                    log.append("search failed: %s %s page %d: %s" % (w, term, page, str(exc)[:200]))
                    break
                count, pages, results = census.parse_page(obj)
                for r in results:
                    dn = r.get("document_number")
                    if not dn:
                        continue
                    d = docs.get(dn)
                    if d is None:
                        d = dict(r)
                        d["terms_matched"] = set()
                        d["window"] = census.window_of(str(r.get("publication_date") or "")) or w
                        d["agency_class"] = census.agency_class(d)
                        d["top_agency"] = census.top_agency(d)
                        docs[dn] = d
                    d["terms_matched"].add(term.strip('"'))
                    rows += 1
                page += 1
            queries.append({"window": w, "term": term, "count": count, "rows": rows, "pages": pages})
    return docs, queries, failed, truncated


def fetch_texts(ordered, excerpts, fetch=None, sleep=time.sleep):
    """Fetch, classify. Returns None when done, or the index at which it stopped."""
    fetch = fetch or (lambda u: get_retry(u, timeout=300, accept="text/plain,text/html")[0])
    fails = 0
    for i, d in enumerate(ordered):
        sleep(census.DELAY_S)
        d["readable"] = False
        url = d.get("raw_text_url")
        if not url:
            d["fetch_status"] = "no_url"
            continue
        try:
            body = fetch(url)
        except urllib.error.HTTPError as exc:
            d["fetch_status"] = "http_%s" % exc.code
            fails += 1
        except Exception:
            d["fetch_status"] = "error"
            fails += 1
        else:
            fails = 0
            d["fetch_status"] = "ok"
            d["text_sha256"] = hashlib.sha256(body).hexdigest()
            r = census.classify(census.normalize(body.decode("utf-8", "replace")))
            d.update({"counts": r["counts"], "category": r["category"], "chars": r["chars"]})
            d["readable"] = r["chars"] >= census.READABLE_CHARS
            for key, ex in sorted(r["excerpts"].items()):
                excerpts.append("== %s | %s | %s | %s | %s\n%s\n" % (d["document_number"], d.get("publication_date"),
                                                                    d.get("top_agency"), d["category"], key, ex))
            if i % 10 == 0 or r["category"] in ("both", "si_only"):
                print(census.now(), i + 1, "/", len(ordered), d["document_number"], d["category"],
                      d["counts"].get("si"), d["counts"].get("ai"), flush=True)
        if fails >= MAX_CONSECUTIVE_FAILURES:
            return i
    return None


def ecfr_snapshot(fetch=None, sleep=time.sleep):
    fetch = fetch or get_json
    out = {"fetched_at": census.now(), "note": "eCFR search hits, all section versions since 2017"}
    for t in census.ECFR_TERMS:
        sleep(census.ECFR_DELAY_S)
        try:
            out[t] = census.ecfr_total(fetch(census.ecfr_url(t)))
        except Exception as exc:
            out[t] = "error: %s" % str(exc)[:200]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wave", default="w01", choices=sorted(census.WAVES))
    ap.add_argument("--wait-minutes", type=int, default=120)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(priv, exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION, "wave": args.wave, "log": []}
    windows = census.WAVES[args.wave]
    if "W2" in windows and census.now()[:10] < W2_EARLIEST_RUN:
        status["result"] = "stopped: wave w02 may not run before %s; nothing downloaded" % W2_EARLIEST_RUN
        return finish(args.out_dir, status, 4)

    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local_sha = norm_sha(fh.read())
    plan, code, committed_sha = wait_for_plan(args.wait_minutes, local_sha)
    status["census_sha256_local"] = local_sha
    if not plan:
        status["result"] = "stopped: PLAN.md and a matching census.py not public; nothing downloaded"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "census_commit": code, "census_sha256_committed": committed_sha})

    docs, queries, failed, truncated = search_all(windows, status["log"])
    with open(os.path.join(args.out_dir, "queries.json"), "w", encoding="utf-8") as fh:
        json.dump(queries, fh, indent=1)
    n_w1 = sum(1 for d in docs.values() if d["window"] == "W1")
    status.update({"frame": len(docs), "frame_w1": n_w1})
    if failed:
        status["result"] = "stopped: %d search request(s) failed; no document text fetched" % failed
        return finish(args.out_dir, status, 5)
    if n_w1 < census.MIN_FRAME_W1:
        status["result"] = "stopped: W1 frame holds %d documents; no document text fetched" % n_w1
        return finish(args.out_dir, status, 6)
    if truncated or len(docs) > census.MAX_FRAME:
        status["result"] = "stopped: frame holds %d documents (%d searches truncated); no text fetched" % (
            len(docs), truncated)
        return finish(args.out_dir, status, 8)

    ordered = sorted(docs.values(), key=lambda d: (str(d.get("publication_date")), str(d.get("document_number"))))
    excerpts = []
    stop = fetch_texts(ordered, excerpts)
    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(args.out_dir, "rows.csv"), "w", encoding="utf-8") as fh:
        fh.write(census.rows_csv(ordered))
    if stop is not None:
        status["result"] = "stopped: %d document fetches failed in a row at %d of %d" % (
            MAX_CONSECUTIVE_FAILURES, stop + 1, len(ordered))
        return finish(args.out_dir, status, 9)

    ecfr = ecfr_snapshot()
    res = census.grade(ordered, ecfr, args.wave)
    res["sources"] = {"plan_commit": plan, "census_commit": code, "api": census.API, "queries": queries}
    with open(os.path.join(args.out_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=_default)
    with open(os.path.join(args.out_dir, "results.md"), "w", encoding="utf-8") as fh:
        fh.write(census.results_md(res))
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    status["shares"] = {w: (c["si_share_nonpresidential"], c["si_share_other_agencies"])
                        for w, c in res["counts"].items()}
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
