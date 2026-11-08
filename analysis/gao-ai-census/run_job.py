#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""One wave of the pre-registered GAO census (census 1.0.0).

Order enforced here:
1. wait until analysis/gao-ai-census/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance, and check that the census.py next to this file is
   identical (line endings aside) to the newest committed one;
2. read the published ledger (decisions.csv; absent before the first wave);
3. fetch GAO's legal RSS feed once, then each new bid-protest page, DELAY_S seconds apart.
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
DIR = "analysis/gao-ai-census"


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(8 * 1024 * 1024)


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url).decode("utf-8"))
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


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wave", required=True)
    ap.add_argument("--wait-minutes", type=int, default=240)
    args = ap.parse_args(argv)
    raw_dir = os.path.join(args.out_dir, "raw")  # private: never published
    os.makedirs(raw_dir, exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION, "wave": args.wave}

    plan, code_commit = wait_for_plan(args.wait_minutes)
    if not plan:
        status["result"] = "stopped: PLAN.md not public; GAO not contacted"
        return finish(args.out_dir, status, 3)
    committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py" % (REPO, code_commit["sha"], DIR))
    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local = fh.read()
    status.update({"plan_commit": plan, "census_commit": code_commit,
                   "census_sha256_committed": norm_sha(committed), "census_sha256_local": norm_sha(local)})
    if norm_sha(committed) != norm_sha(local):
        status["result"] = "stopped: local census.py differs from the committed one; GAO not contacted"
        return finish(args.out_dir, status, 4)

    try:
        ledger_text = get("https://raw.githubusercontent.com/%s/main/%s/decisions.csv" % (REPO, DIR)).decode("utf-8")
        status["ledger"] = "read"
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            status["result"] = "stopped: ledger read failed (%s); GAO not contacted" % exc.code
            return finish(args.out_dir, status, 5)
        ledger_text, status["ledger"] = "", "absent (first wave)"
    ledger = census.load_ledger(ledger_text)
    ledger_ids = {r.get("b_number", "") for r in ledger}
    status["ledger_rows"] = len(ledger)

    rss = get(census.RSS_URL)
    with open(os.path.join(args.out_dir, "rss.xml"), "wb") as fh:
        fh.write(rss)
    items = census.parse_rss(rss)
    fetch, skipped = census.plan_wave(items, ledger_ids)
    feed_dates = [it["pubdate"] for it in items]
    wave = {"wave": args.wave, "rss_fetched_at": census.now(), "rss_items": len(items),
            "rss_sha256": hashlib.sha256(rss).hexdigest(),
            "feed_oldest": min([d for d in feed_dates if d] or [""]),
            "feed_newest": max([d for d in feed_dates if d] or [""]),
            "ledger_newest": max([r.get("rss_pubdate", "") for r in ledger] or [""]),
            "gap_possible": census.gap_possible(feed_dates, [r.get("rss_pubdate", "") for r in ledger]),
            "to_fetch": len(fetch), "skipped": skipped, "errors": []}
    print(census.now(), "rss items", len(items), "to fetch", len(fetch), flush=True)

    new_rows = []
    for it in fetch:
        time.sleep(census.DELAY_S)
        row = {"b_number": it["b_number"], "b_numbers": it["b_numbers"], "url": it["link"],
               "rss_pubdate": it["pubdate"], "wave": args.wave, "fetched_at": census.now()}
        try:
            page = get(it["link"]).decode("utf-8", errors="replace")
        except Exception as exc:
            wave["errors"].append({"b_number": it["b_number"], "error": str(exc)[:200]})
            print(census.now(), it["b_number"], "error", exc, flush=True)
            continue  # not added to the ledger, so the next wave retries it if still in the feed
        with open(os.path.join(raw_dir, it["b_number"] + ".html"), "w", encoding="utf-8") as fh:
            fh.write(page)
        d = census.parse_decision(page)
        d.pop("protester_full", None)
        row.update(d)
        new_rows.append(row)
        print(census.now(), it["b_number"], row.get("category"), flush=True)

    with open(os.path.join(args.out_dir, "decisions.csv"), "w", encoding="utf-8", newline="") as fh:
        fh.write(census.ledger_csv(ledger + new_rows))
    cats = {}
    for r in new_rows:
        cats[str(r.get("category", "unparsed"))] = cats.get(str(r.get("category", "unparsed")), 0) + 1
    wave.update({"new_rows": len(new_rows), "new_by_category": cats, "finished": census.now()})
    with open(os.path.join(args.out_dir, "wave.json"), "w", encoding="utf-8") as fh:
        json.dump(wave, fh, indent=1)
    status.update({"result": "wave done", "new_rows": len(new_rows), "new_by_category": cats,
                   "gap_possible": wave["gap_possible"], "errors": len(wave["errors"])})
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
