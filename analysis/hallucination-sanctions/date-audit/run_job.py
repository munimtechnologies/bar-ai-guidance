#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the hallucination-sanctions date audit (audit 1.0.0).

Order is enforced here:
1. wait until date-audit/PLAN.md and date-audit/audit.py are public in
   munimtechnologies/bar-ai-guidance, and check that the local audit.py is byte-identical
   (line endings aside) to the committed one;
2. fetch the frozen analyze.py (PREREG commit 65bd693) and check its SHA-256;
3. fetch the published us_rows.csv and results.json, and check that a regrade with the
   recorded dates reproduces the published primary verdicts and numbers;
4. only then fetch the database CSV (for document paths) and the decision documents,
   one request per second, and grade D1-D4.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/hallucination-sanctions"
ADIR = DIR + "/date-audit"
PREREG_SHA = "65bd6931337409d6ce5f34c30fe0d56de1f0a159"
ANALYZE_SHA256 = "c74d51a31e1b7d5657778f88793ed2d44115f431569508535abf833e561083fd"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
PAUSE_S = 1.0
MAX_BYTES = 40 * 1024 * 1024


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("document larger than %d bytes" % MAX_BYTES)
    return data


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url).decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def raw(sha_or_branch, path):
    return get("https://raw.githubusercontent.com/%s/%s/%s" % (REPO, sha_or_branch, path))


def finish(out_dir, status, rc):
    status["finished"] = now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def wait_for_plan(max_minutes, step_minutes=5):
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            plan = commits_for(ADIR + "/PLAN.md")
            code = commits_for(ADIR + "/audit.py")
            if plan and code:
                return plan[-1], code[0]
            print(now(), "plan not public yet", flush=True)
        except Exception as exc:
            print(now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None
        time.sleep(step_minutes * 60)


def load_module(name, data, tmp_dir):
    path = os.path.join(tmp_dir, name + ".py")
    with open(path, "wb") as fh:
        fh.write(data)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verdicts(ev):
    return {k: ev[k]["verdict"] for k in ("P1", "P2", "P3", "P4", "P5")}


def compact(ev):
    keep = ("a", "b", "n_a", "n_b", "diff", "perm_p_rise", "verdict")
    out = {}
    for k in ("P1", "P2", "P3", "P5"):
        out[k] = {x: ev[k][x] for x in keep if x in ev[k]}
    out["P4"] = ev["P4"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=150)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    tmp = os.path.join(args.out_dir, "_frozen")
    os.makedirs(tmp, exist_ok=True)
    status = {"started": now(), "audit_version": audit.VERSION}

    # 1. plan gate
    plan, code = wait_for_plan(args.wait_minutes)
    if not plan:
        status["result"] = "stopped: PLAN.md not public; no document fetched"
        return finish(args.out_dir, status, 3)
    committed = raw(code["sha"], ADIR + "/audit.py")
    with open(os.path.join(HERE, "audit.py"), "rb") as fh:
        local = fh.read()
    status.update({"plan_commit": plan, "audit_commit": code, "audit_sha256_committed": norm_sha(committed),
                   "audit_sha256_local": norm_sha(local)})
    if norm_sha(committed) != norm_sha(local):
        status["result"] = "stopped: local audit.py differs from the committed one; no document fetched"
        return finish(args.out_dir, status, 4)

    # 2. frozen analysis code
    ana_bytes = raw(PREREG_SHA, DIR + "/analyze.py")
    status["analyze_sha256"] = norm_sha(ana_bytes)
    if norm_sha(ana_bytes) != ANALYZE_SHA256:
        status["result"] = "stopped: frozen analyze.py hash mismatch"
        return finish(args.out_dir, status, 5)
    analyze = load_module("analyze_frozen", ana_bytes, tmp)

    # 3. published graded rows and the sanity regrade
    us_bytes = raw("main", DIR + "/results/us_rows.csv")
    pub = json.loads(raw("main", DIR + "/results/results.json").decode("utf-8"))
    status["us_rows_sha256"] = hashlib.sha256(us_bytes).hexdigest()
    us_rows = list(csv.DictReader(io.StringIO(us_bytes.decode("utf-8"))))
    base = [analyze.classify(audit.pseudo_raw(r)) for r in us_rows]
    ev0 = analyze.evaluate(base)
    sanity = {k: (ev0[k].get("a"), ev0[k].get("b"), ev0[k]["verdict"]) ==
              (pub["primary"][k].get("a"), pub["primary"][k].get("b"), pub["primary"][k]["verdict"])
              for k in ("P1", "P2", "P3", "P4", "P5")}
    status["sanity_reproduces_published"] = sanity
    if not all(sanity.values()):
        status["result"] = "stopped: regrade with recorded dates does not reproduce the published result"
        status["regrade_recorded"] = compact(ev0)
        return finish(args.out_dir, status, 6)

    # 4. database CSV for document paths
    csv_bytes = get(CSV_URL, timeout=300)
    status["csv"] = {"url": CSV_URL, "fetched_at": now(), "bytes": len(csv_bytes),
                     "sha256": hashlib.sha256(csv_bytes).hexdigest(),
                     "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}
    csv.field_size_limit(10 ** 8)
    db = {}
    for r in csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig", errors="replace"))):
        cid = (r.get("case_id") or "").strip()
        if cid:
            db[cid] = {"source": (r.get("Source") or "").strip(), "date_now": (r.get("Date") or "").strip()}

    targets = [r for r in us_rows if "Lawyer" in [p.strip() for p in r["parties"].split(";")]]
    status["n_targets"] = len(targets)
    last = [0.0]

    def fetch(url):
        wait = PAUSE_S - (time.time() - last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            return get(url, timeout=90)
        except Exception:
            time.sleep(5)
            return get(url, timeout=90)
        finally:
            last[0] = time.time()

    rows = []
    for i, r in enumerate(targets):
        info = db.get(r["case_id"], {"source": "", "date_now": ""})
        a = audit.audit_row(r["case_id"], r["date"], info["source"], fetch)
        a["date_now"] = info["date_now"] if r["case_id"] in db else "(not in current CSV)"
        rows.append(a)
        if i % 50 == 0:
            print(now(), "audited", i + 1, "of", len(targets), a["status"], flush=True)

    summary = audit.summarise(rows)
    status["summary"] = summary

    # 5. regrades under C1 and C2 (pro se rows keep their recorded dates)
    by_id = {a["case_id"]: a for a in rows}
    regr = {"recorded": compact(ev0)}
    for key in ("c1", "c2"):
        recs = []
        for r in us_rows:
            a = by_id.get(r["case_id"])
            override = a[key + "_date"] if a is not None else None
            recs.append(analyze.classify(audit.pseudo_raw(r, override)))
        regr[key] = compact(analyze.evaluate(recs))
    status["regrade"] = regr
    status["verdicts"] = {k: {p: v[p]["verdict"] for p in ("P1", "P2", "P3", "P4", "P5")} for k, v in regr.items()}

    audit.write_rows(os.path.join(args.out_dir, "date_audit_rows.csv"), rows)
    audit.write_review(os.path.join(args.out_dir, "review.md"), rows)
    with open(os.path.join(args.out_dir, "date_audit.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "regrade": regr, "verdicts": status["verdicts"]}, fh, indent=1, default=str)
    status["result"] = "audited"
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
