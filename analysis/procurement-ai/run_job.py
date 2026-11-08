#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered procurement-tribunal analysis (1.0.0).

Order is enforced here:
1. wait until analysis/procurement-ai/PLAN.md and analyze.py are public in
   munimtechnologies/bar-ai-guidance;
2. check that the analyze.py next to this file is byte-identical (line endings aside)
   to the committed one;
3. only then download the database CSV, record its SHA-256 and time, and grade.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/procurement-ai"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
SNAPSHOT_2026_11_07 = "9201eecd5ea30ac3eda884062a6421f84882abf2f58415aa4391e283ef297c87"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


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
            ana = commits_for(DIR + "/analyze.py")
            if plan and ana:
                return plan[-1], ana[0]
            print(now(), "plan not public yet", flush=True)
        except Exception as exc:  # network hiccup: keep waiting
            print(now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None
        time.sleep(step_minutes * 60)


def finish(out_dir, status, rc):
    status["finished"] = now()
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
    status = {"started": now(), "analysis_version": analyze.VERSION}

    plan, ana_commit = wait_for_plan(args.wait_minutes)
    if not plan:
        status["result"] = "stopped: PLAN.md not public; data NOT downloaded"
        return finish(args.out_dir, status, 3)

    committed = get("https://raw.githubusercontent.com/%s/%s/%s/analyze.py" % (REPO, ana_commit["sha"], DIR))
    with open(os.path.join(HERE, "analyze.py"), "rb") as fh:
        local = fh.read()
    status.update({"plan_commit": plan, "analyze_commit": ana_commit,
                   "analyze_sha256_committed": norm_sha(committed), "analyze_sha256_local": norm_sha(local)})
    if norm_sha(committed) != norm_sha(local):
        status["result"] = "stopped: local analyze.py differs from the committed one; data NOT downloaded"
        return finish(args.out_dir, status, 4)

    data, err = None, None
    for _ in range(3):
        try:
            data = get(CSV_URL, timeout=300)
            break
        except Exception as exc:
            err = str(exc)
            time.sleep(30)
    if data is None:
        status["result"] = "stopped: CSV download failed: %s" % err
        return finish(args.out_dir, status, 5)

    csv_path = os.path.join(args.out_dir, "download.csv")  # kept for review; never published
    with open(csv_path, "wb") as fh:
        fh.write(data)
    sha = hashlib.sha256(data).hexdigest()
    source = {"url": CSV_URL, "fetched_at": now(), "bytes": len(data), "sha256": sha,
              "same_as_2026_11_07_snapshot": sha == SNAPSHOT_2026_11_07,
              "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin",
              "plan_commit": plan, "analyze_commit": ana_commit}
    src_path = os.path.join(args.out_dir, "source.json")
    with open(src_path, "w", encoding="utf-8") as fh:
        json.dump(source, fh, indent=1)
    status["source"] = source
    rc = analyze.main(["--csv", csv_path, "--out-dir", args.out_dir, "--source-json", src_path])
    status["result"] = "graded" if rc == 0 else "analyze exited %s" % rc
    return finish(args.out_dir, status, rc)


if __name__ == "__main__":
    sys.exit(main())
