#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered analysis (version 1.0.0): are US courts "ratcheting up" sanctions
in AI-hallucination decisions?

Data: AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0), CSV export.

This file is frozen in analysis/hallucination-sanctions/PREREG.md before any data row
is read. Standard library only.

Usage: python analyze.py --csv download.csv --out-dir out/ [--source-json source.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import statistics
import sys

VERSION = "1.0.0"
SEED = 20261106
N_PERM = 10000
MIN_N = 30          # minimum decisions per group and period for a share prediction
MIN_AMT = 10        # minimum decisions with a USD amount per period for a median prediction
PERIOD_A = "2025H1"
PERIOD_B = "2026H1"
P4_PERIODS = ("2025H1", "2025H2", "2026H1")
P1_MARGIN = 0.05
BIG_FINE = 10000.0
TABLE_PERIODS = ("2023H1", "2023H2", "2024H1", "2024H2", "2025H1", "2025H2", "2026H1", "2026H2")
BUCKETS = ((0, 1000, "<1k"), (1000, 5000, "1k-<5k"), (5000, 10000, "5k-<10k"), (10000, float("inf"), ">=10k"))

REQUIRED = ("case_id", "State(s)", "Date", "Party(ies)", "Monetary Penalty", "Professional Sanction")

_AMOUNT = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*([A-Za-z]{3}))?$")
_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})")


# ---------------------------------------------------------------- parsing

def parse_amount(raw):
    """Return (status, amount, currency); status is 'none', 'ok' or 'unparsed'."""
    s = (raw or "").strip().replace(",", "")
    if s in ("", "-", "—", "–"):
        return "none", None, None
    m = _AMOUNT.match(s)
    if not m:
        return "unparsed", None, None
    cur = (m.group(2) or "").upper() or None
    return "ok", float(m.group(1)), cur


def parse_period(raw):
    m = _DATE.match((raw or "").strip())
    if not m:
        return None, None
    year, month = int(m.group(1)), int(m.group(2))
    if not 1 <= month <= 12:
        return None, None
    return "%dH%d" % (year, 1 if month <= 6 else 2), str(year)


def parse_flag(raw):
    s = (raw or "").strip().lower()
    if s == "yes":
        return True
    if s == "no":
        return False
    return None


def split_tokens(raw, seps=";"):
    parts = re.split("[" + re.escape(seps) + "]", raw or "")
    return [p.strip() for p in parts if p.strip()]


def is_us_token(t):
    """'USA' (the database's label), also 'USA (...)' or 'United States' should it appear."""
    return t == "USA" or t.startswith("USA ") or t.startswith("USA(") or t.lower() == "united states"


def classify(row):
    """Turn one CSV row (dict) into the analysis record."""
    parties = split_tokens(row.get("Party(ies)"))
    states = split_tokens(row.get("State(s)"), ";,")
    status, amount, cur = parse_amount(row.get("Monetary Penalty"))
    period, year = parse_period(row.get("Date"))
    fined = (status == "ok" and amount >= 1) or status == "unparsed"
    placeholder = status == "ok" and amount == 1
    usd = None
    if status == "ok" and amount > 1 and cur in (None, "USD"):
        usd = amount
    prof = parse_flag(row.get("Professional Sanction"))
    return {
        "case_id": (row.get("case_id") or "").strip(),
        "date": (row.get("Date") or "").strip(),
        "period": period,
        "year": year,
        "us": any(is_us_token(t) for t in states),
        "parties": parties,
        "lawyer": "Lawyer" in parties,
        "lawyer_broad": any("lawyer" in p.lower() for p in parties),
        "pro_se": "Pro Se Litigant" in parties,
        "penalty_raw": (row.get("Monetary Penalty") or "").strip(),
        "penalty_status": status,
        "amount": amount,
        "currency": cur,
        "fined": bool(fined),
        "fined_strict": bool(status == "ok" and amount > 1),
        "placeholder": placeholder,
        "usd_amount": usd,
        "prof": prof is True,
        "alleged": parse_flag(row.get("Alleged")),
    }


def read_csv(path):
    csv.field_size_limit(10 ** 8)
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip() for h in (reader.fieldnames or [])]
        reader.fieldnames = header
        missing = [c for c in REQUIRED if c not in header]
        if missing:
            raise SystemExit("CSV header lacks required columns %s; header was %s" % (missing, header))
        rows, bad = [], 0
        for r in reader:
            if None in r or not (r.get("case_id") or "").strip() or r.get("Date") is None:
                bad += 1
                continue
            rows.append(r)
    return header, rows, bad


# ---------------------------------------------------------------- statistics

def wilson(k, n, z=1.959964):
    if n == 0:
        return None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return round(centre - half, 4), round(centre + half, 4)


def _mean(xs):
    return sum(xs) / len(xs)


def perm_p(a, b, stat, n_perm=N_PERM, seed=SEED):
    """One-sided permutation p-value for stat(b) - stat(a) > 0."""
    if not a or not b:
        return None, None
    obs = stat(b) - stat(a)
    pooled = list(a) + list(b)
    rng = random.Random(seed)
    na = len(a)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        if stat(pooled[na:]) - stat(pooled[:na]) >= obs - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n_perm + 1)


def group_stats(recs, fined_key="fined"):
    n = len(recs)
    nf = sum(1 for r in recs if r[fined_key])
    amts = sorted(r["usd_amount"] for r in recs if r["usd_amount"] is not None)
    nprof = sum(1 for r in recs if r["prof"])
    nmp = sum(1 for r in recs if r[fined_key] or r["prof"])
    out = {
        "n": n,
        "n_fined": nf,
        "share_fined": round(nf / n, 4) if n else None,
        "share_fined_ci95": wilson(nf, n),
        "n_placeholder_1": sum(1 for r in recs if r["placeholder"]),
        "n_unparsed_penalty": sum(1 for r in recs if r["penalty_status"] == "unparsed"),
        "n_non_usd": sum(1 for r in recs if r["penalty_status"] == "ok" and r["currency"] not in (None, "USD")),
        "n_usd_amounts": len(amts),
        "median_usd": statistics.median(amts) if amts else None,
        "mean_usd": round(_mean(amts), 2) if amts else None,
        "p25_usd": statistics.quantiles(amts, n=4, method="inclusive")[0] if len(amts) >= 2 else None,
        "p75_usd": statistics.quantiles(amts, n=4, method="inclusive")[2] if len(amts) >= 2 else None,
        "max_usd": amts[-1] if amts else None,
        "share_amounts_ge_10k": round(sum(1 for x in amts if x >= BIG_FINE) / len(amts), 4) if amts else None,
        "buckets": {lab: sum(1 for x in amts if lo <= x < hi) for lo, hi, lab in BUCKETS},
        "n_prof": nprof,
        "share_prof": round(nprof / n, 4) if n else None,
        "share_prof_ci95": wilson(nprof, n),
        "n_money_or_prof": nmp,
        "share_money_or_prof": round(nmp / n, 4) if n else None,
    }
    return out


# ---------------------------------------------------------------- predictions

def evaluate(recs, who="lawyer", fined_key="fined", pkey="period", a=PERIOD_A, b=PERIOD_B,
             p4_periods=P4_PERIODS):
    """Grade P1-P5 on US records. Returns dict of prediction results."""
    us = [r for r in recs if r["us"]]
    law = [r for r in us if r[who]]
    pro = [r for r in us if r["pro_se"]]

    def at(rs, p):
        return [r for r in rs if r[pkey] == p]

    la, lb = at(law, a), at(law, b)
    sa, sb = group_stats(la, fined_key), group_stats(lb, fined_key)
    res = {}

    # P1: share of lawyer decisions with a monetary penalty does not rise by more than 5 points.
    if len(la) >= MIN_N and len(lb) >= MIN_N:
        diff, p = perm_p([1 if r[fined_key] else 0 for r in la], [1 if r[fined_key] else 0 for r in lb], _mean)
        res["P1"] = {"a": sa["share_fined"], "b": sb["share_fined"], "diff": round(diff, 4), "perm_p_rise": round(p, 4),
                     "verdict": "held" if diff <= P1_MARGIN + 1e-12 else "failed"}
    else:
        res["P1"] = {"verdict": "not testable", "n_a": len(la), "n_b": len(lb)}

    # P2: median USD amount among fined lawyer decisions is higher in B than in A.
    xa = [r["usd_amount"] for r in la if r["usd_amount"] is not None]
    xb = [r["usd_amount"] for r in lb if r["usd_amount"] is not None]
    if len(xa) >= MIN_AMT and len(xb) >= MIN_AMT:
        diff, p = perm_p(xa, xb, statistics.median)
        res["P2"] = {"a": statistics.median(xa), "b": statistics.median(xb), "n_a": len(xa), "n_b": len(xb),
                     "diff": diff, "perm_p_rise": round(p, 4), "verdict": "held" if diff > 0 else "failed"}
    else:
        res["P2"] = {"verdict": "not testable", "n_a": len(xa), "n_b": len(xb)}

    # P3: share of lawyer decisions with a professional sanction is higher in B than in A.
    if len(la) >= MIN_N and len(lb) >= MIN_N:
        diff, p = perm_p([1 if r["prof"] else 0 for r in la], [1 if r["prof"] else 0 for r in lb], _mean)
        res["P3"] = {"a": sa["share_prof"], "b": sb["share_prof"], "diff": round(diff, 4), "perm_p_rise": round(p, 4),
                     "verdict": "held" if diff > 0 else "failed"}
    else:
        res["P3"] = {"verdict": "not testable", "n_a": len(la), "n_b": len(lb)}

    # P4: in each listed period, pro se decisions carry a monetary penalty less often than lawyer decisions.
    rows4, ok4, testable4 = [], True, True
    for per in p4_periods:
        lp, pp = at(law, per), at(pro, per)
        if len(lp) < MIN_N or len(pp) < MIN_N:
            testable4 = False
        ls_, ps_ = group_stats(lp, fined_key), group_stats(pp, fined_key)
        less = (ps_["share_fined"] is not None and ls_["share_fined"] is not None
                and ps_["share_fined"] < ls_["share_fined"])
        ok4 = ok4 and less
        rows4.append({"period": per, "lawyer": ls_["share_fined"], "pro_se": ps_["share_fined"],
                      "n_lawyer": len(lp), "n_pro_se": len(pp), "pro_se_lower": less})
    res["P4"] = {"by_period": rows4, "verdict": ("held" if ok4 else "failed") if testable4 else "not testable"}

    # P5: in B, fewer than half of lawyer decisions carry a monetary penalty or a professional sanction.
    if len(lb) >= MIN_N:
        res["P5"] = {"b": sb["share_money_or_prof"], "n_b": len(lb),
                     "verdict": "held" if sb["share_money_or_prof"] < 0.5 else "failed"}
    else:
        res["P5"] = {"verdict": "not testable", "n_b": len(lb)}
    return res


def period_table(recs, who):
    us = [r for r in recs if r["us"] and r[who]]
    return {p: group_stats([r for r in us if r["period"] == p]) for p in TABLE_PERIODS}


def analyze(header, raw_rows, n_bad, source=None):
    recs = [classify(r) for r in raw_rows]
    us = [r for r in recs if r["us"]]
    results = {
        "version": VERSION,
        "source": source or {},
        "header": header,
        "n_rows_read": len(raw_rows),
        "n_rows_skipped_malformed": n_bad,
        "state_values_top": sorted(
            ((v, sum(1 for r in raw_rows if (r.get("State(s)") or "").strip() == v))
             for v in set((r.get("State(s)") or "").strip() for r in raw_rows)),
            key=lambda kv: (-kv[1], kv[0]))[:15],
        "party_values_top": sorted(
            ((v, sum(1 for r in recs if v in r["parties"]))
             for v in set(p for r in recs for p in r["parties"])),
            key=lambda kv: (-kv[1], kv[0]))[:15],
        "n_us": len(us),
        "n_us_no_date": sum(1 for r in us if r["period"] is None),
        "n_us_lawyer": sum(1 for r in us if r["lawyer"]),
        "n_us_pro_se": sum(1 for r in us if r["pro_se"]),
        "primary": evaluate(recs),
        "sensitivity": {
            "S1_exclude_alleged": evaluate([r for r in recs if r["alleged"] is not True]),
            "S2_lawyer_broad": evaluate(recs, who="lawyer_broad"),
            "S3_fined_strict": evaluate(recs, fined_key="fined_strict"),
            "S4_years_2025_vs_2026": evaluate(recs, pkey="year", a="2025", b="2026", p4_periods=("2025", "2026")),
        },
        "table_lawyer": period_table(recs, "lawyer"),
        "table_pro_se": period_table(recs, "pro_se"),
    }
    return recs, results


# ---------------------------------------------------------------- output

def _fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        if x.is_integer():
            return "{:,}".format(int(x))
        return "%.3f" % x if abs(x) < 1 else "{:,.0f}".format(x)
    return str(x)


def render_md(res):
    out = ["# AI-hallucination sanctions over time: graded result (analysis %s)" % res["version"], ""]
    src = res.get("source") or {}
    if src:
        out.append("Source: AI Hallucination Cases Database, Damien Charlotin, "
                   "https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0). CSV fetched %s, SHA-256 %s, %s bytes."
                   % (src.get("fetched_at", "?"), src.get("sha256", "?"), src.get("bytes", "?")))
        out.append("")
    out.append("Rows read %d (malformed skipped %d); US %d (no date %d); US with a lawyer %d; US with a pro se litigant %d."
               % (res["n_rows_read"], res["n_rows_skipped_malformed"], res["n_us"], res["n_us_no_date"],
                  res["n_us_lawyer"], res["n_us_pro_se"]))
    out.append("")
    out.append("## Predictions (primary)")
    out.append("")
    for k, v in res["primary"].items():
        out.append("- **%s: %s** %s" % (k, v["verdict"], json.dumps({x: y for x, y in v.items() if x != "verdict"})))
    out.append("")
    out.append("## Sensitivity")
    out.append("")
    out.append("| analysis | P1 | P2 | P3 | P4 | P5 |")
    out.append("|---|---|---|---|---|---|")
    for name, ev in res["sensitivity"].items():
        out.append("| %s | %s |" % (name, " | ".join(ev[k]["verdict"] for k in ("P1", "P2", "P3", "P4", "P5"))))
    for label, key in (("US decisions involving a lawyer", "table_lawyer"), ("US decisions involving a pro se litigant", "table_pro_se")):
        out.append("")
        out.append("## %s, by half-year of decision" % label)
        out.append("")
        out.append("| period | n | share with money penalty | USD amounts | median USD | p75 USD | max USD | share >= $10k | share prof. sanction |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for p, s in res[key].items():
            out.append("| %s | %d | %s | %d | %s | %s | %s | %s | %s |" % (
                p, s["n"], _fmt(s["share_fined"]), s["n_usd_amounts"], _fmt(s["median_usd"]), _fmt(s["p75_usd"]),
                _fmt(s["max_usd"]), _fmt(s["share_amounts_ge_10k"]), _fmt(s["share_prof"])))
    out.append("")
    out.append("Amounts are as the database records them; they can include fee awards as well as penalties. "
               "Made with AI agents working in MV2's name. Information only, not legal advice.")
    return "\n".join(out) + "\n"


ROW_FIELDS = ("case_id", "date", "period", "parties", "penalty_raw", "penalty_status", "amount", "currency",
              "fined", "usd_amount", "prof", "alleged")


def write_outputs(out_dir, recs, res):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False, default=str)
        fh.write("\n")
    with open(os.path.join(out_dir, "results.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(res))
    with open(os.path.join(out_dir, "us_rows.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(ROW_FIELDS)
        for r in recs:
            if r["us"]:
                w.writerow(["; ".join(r[f]) if f == "parties" else ("" if r[f] is None else r[f]) for f in ROW_FIELDS])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--source-json")
    args = ap.parse_args(argv)
    source = None
    if args.source_json:
        with open(args.source_json, encoding="utf-8") as fh:
            source = json.load(fh)
    header, rows, bad = read_csv(args.csv)
    recs, res = analyze(header, rows, bad, source)
    write_outputs(args.out_dir, recs, res)
    print(json.dumps({k: v["verdict"] for k, v in res["primary"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
