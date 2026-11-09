#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered CFR AI-terms census (census 1.0.1).

Order enforced here:
1. wait until analysis/cfr-ai-census/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance AND the newest committed census.py is identical (line
   endings aside) to the census.py next to this file (1.0.1 waits for its own commit);
2. only then query the eCFR search API: every term without a date (all versions since
   2017) and at every census date, every page, DELAY_S seconds apart;
3. build the provision list, the timeline and the summaries.

Everything written to the output folder is public U.S. government data or derived from it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/cfr-ai-census"


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url).decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def wait_for_plan(local_sha, max_minutes, step_minutes=5):
    """Return (oldest PLAN commit, newest census.py commit, sha of that committed census.py)."""
    deadline = time.time() + max_minutes * 60
    last = (None, None, None)
    while True:
        try:
            plan = commits_for(DIR + "/PLAN.md")
            code = commits_for(DIR + "/census.py")
            if plan and code:
                committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py"
                                % (REPO, code[0]["sha"], DIR))
                last = (plan[-1], code[0], norm_sha(committed))
                if last[2] == local_sha:
                    return last
                print(census.now(), "newest committed census.py differs from local; waiting", flush=True)
            else:
                print(census.now(), "plan not public yet", flush=True)
        except Exception as exc:
            print(census.now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return last
        time.sleep(step_minutes * 60)


def query(term, date):
    """All pages for one term (and date). Returns (hits, log)."""
    hits, log = [], {"term": term, "date": date, "pages_fetched": 0, "error": None}
    page = 1
    while True:
        params = [("query", '"%s"' % term), ("per_page", census.PER_PAGE), ("page", page)]
        if date:
            params.append(("date", date))
        url = census.API + "?" + urllib.parse.urlencode(params)
        data, err = None, None
        for attempt in range(3):
            try:
                time.sleep(census.DELAY_S)
                data = json.loads(get(url).decode("utf-8"))
                break
            except Exception as exc:
                err = str(exc)
                time.sleep(20 * (attempt + 1))
        if data is None:
            log["error"] = err
            break
        meta = data.get("meta") or {}
        log["total_count"] = meta.get("total_count")
        log["total_pages"] = meta.get("total_pages")
        hits.extend(data.get("results") or [])
        log["pages_fetched"] = page
        if page >= (meta.get("total_pages") or 0) or page >= census.MAX_PAGES:
            break
        page += 1
    log["hits"] = len(hits)
    log["complete"] = (log["error"] is None and log.get("total_count") is not None
                       and len(hits) == log["total_count"])
    return hits, log


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
    os.makedirs(args.out_dir, exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION}

    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local_sha = norm_sha(fh.read())
    plan, code, committed_sha = wait_for_plan(local_sha, args.wait_minutes)
    if not plan:
        status["result"] = "stopped: PLAN.md not public; nothing queried"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "census_commit": code,
                   "census_sha256_committed": committed_sha, "census_sha256_local": local_sha})
    if committed_sha != local_sha:
        status["result"] = "stopped: local census.py differs from the committed one; nothing queried"
        return finish(args.out_dir, status, 4)

    # The census date must be one the eCFR covers for every title.
    try:
        titles = json.loads(get("https://www.ecfr.gov/api/versioner/v1/titles.json").decode("utf-8"))
        status["ecfr_up_to_date_as_of"] = (titles.get("meta") or {}).get("date")
    except Exception as exc:
        status["ecfr_up_to_date_as_of"] = "check failed: %s" % exc

    status["queries_started"] = census.now()
    dated, undated, logs, raw = {}, {}, [], []
    for term in census.TERMS:
        hits, log = query(term, None)
        undated[term] = hits
        logs.append(log)
        raw.append({"term": term, "date": None, "results": hits})
        print(census.now(), term, "all versions:", log, flush=True)
        for d in census.DATES:
            hits, log = query(term, d)
            dated[(term, d)] = hits
            logs.append(log)
            raw.append({"term": term, "date": d, "results": hits})
            print(census.now(), term, d, log["hits"], log["complete"], flush=True)
    status["queries_finished"] = census.now()
    queries_ok = all(l["complete"] for l in logs)

    with open(os.path.join(args.out_dir, "raw_results.json"), "w", encoding="utf-8") as fh:
        json.dump(raw, fh)
    with open(os.path.join(args.out_dir, "queries.json"), "w", encoding="utf-8") as fh:
        json.dump(logs, fh, indent=1)

    prov, timeline, anomalies = census.build(dated, undated)
    rows = census.rows(prov)
    summary = census.summarize(prov, timeline, anomalies)
    summary["queries_complete"] = queries_ok
    summary["source"] = {"api": census.API, "queried_from": status["queries_started"],
                         "queried_to": status["queries_finished"],
                         "ecfr_up_to_date_as_of": status.get("ecfr_up_to_date_as_of"),
                         "plan_commit": plan, "census_commit": code}
    with open(os.path.join(args.out_dir, "provisions.csv"), "w", encoding="utf-8", newline="") as fh:
        fh.write(census.to_csv(rows, census.ROW_FIELDS))
    with open(os.path.join(args.out_dir, "timeline.csv"), "w", encoding="utf-8", newline="") as fh:
        fh.write(census.to_csv(timeline, ["date", "any_term"] + census.TERMS))
    with open(os.path.join(args.out_dir, "anomalies.json"), "w", encoding="utf-8") as fh:
        json.dump(anomalies, fh, indent=1)
    with open(os.path.join(args.out_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.out_dir, "results.md"), "w", encoding="utf-8") as fh:
        fh.write(census.results_md(summary, rows, queries_ok))

    status["provisions_in_force"] = summary["provisions_in_force_on_census_date"]
    status["provisions_ever"] = summary["provisions_ever"]
    status["rules_of_practice_in_force"] = summary["rules_of_practice_in_force"]
    status["queries_complete"] = queries_ok
    if not queries_ok:
        status["result"] = "incomplete: some queries failed or returned fewer hits than total_count"
        return finish(args.out_dir, status, 5)
    status["result"] = "done"
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
