#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered analysis (version 1.0.0): AI-fabricated authority at US federal
procurement tribunals (GAO bid protests, the Court of Federal Claims, the ASBCA and the
CBCA) in the AI Hallucination Cases Database.

Data: AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0), CSV export.

This file is frozen in analysis/procurement-ai/PLAN.md before any data row is read.
Standard library only. Information only, not legal advice.

Usage: python analyze.py --csv download.csv --out-dir out/ [--source-json source.json]
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys

VERSION = "1.0.0"

REQUIRED = ("case_id", "Case Name", "Court", "Date", "Party(ies)", "Monetary Penalty",
            "Professional Sanction")

# Forum detection on the free-text "Court" column. Long names case-insensitive,
# abbreviations case-sensitive and whole-word.
FORUMS = (  # order matters: an appeal court's text may name the tribunal below
    ("FEDCIR", re.compile(r"Court of Appeals for the Federal Circuit|\bFederal Circuit\b", re.I),
     re.compile(r"\bCAFC\b|\bFed\.\s?Cir\.")),
    ("COFC", re.compile(r"Court of Federal Claims", re.I), re.compile(r"\bCOFC\b|\bFed\.\s?Cl\.")),
    ("ASBCA", re.compile(r"Armed Services Board of Contract Appeals", re.I), re.compile(r"\bASBCA\b")),
    ("CBCA", re.compile(r"Civilian Board of Contract Appeals", re.I), re.compile(r"\bCBCA\b")),
    ("GAO", re.compile(r"Government Accountability Office|General Accounting Office|Comptroller General", re.I),
     re.compile(r"\bGAO\b")),
)
CORE = ("GAO", "ASBCA", "CBCA", "COFC")
# A COFC or Federal Circuit row counts as procurement only if this matches its legal-field
# labels, case name or details (the COFC also hears vaccine, tax, takings and pay cases).
PROC_TEXT = re.compile(r"\bprotest|procure|solicitation|contract|\bbid\b|bidder|offeror|award", re.I)
# Secondary detection (sensitivity S2 only) from case name and source text.
S2_HINTS = (
    ("GAO", re.compile(r"\bB-\d{6}(?:\.\d+)?\b")),
    ("ASBCA", re.compile(r"\bASBCA\b|Armed Services Board", re.I)),
    ("CBCA", re.compile(r"\bCBCA\b|Civilian Board of Contract", re.I)),
)
NEAR_MISS = re.compile(r"board|contract|claims|accountability|federal circuit|protest|procure", re.I)

WIN_2025 = ("2025-01-01", "2025-12-31")
WIN_2026_JUL = ("2026-01-01", "2026-07-31")   # Timm's table: "current through the end of July, 2026"
WIN_2026_OCT = ("2026-01-01", "2026-10-31")
WIN_2025_2026 = ("2025-01-01", "2026-10-31")

TIMM_2026_JUL = {"GAO": 12, "COFC": 2, "ASBCA": 4, "CBCA": 1, "FEDCIR": 1}
TIMM_2025_TOTAL = 23

A1_MIN = 15
A2_MIN = 17
A3_MIN_N = 8
A4_SHARE = 0.60
A4_MIN_N = 10
A5_MAX = 1
A5_MIN_N = 10
A6_SHARE = 0.25
A6_MIN_N = 10

_AMOUNT = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*([A-Za-z]{3}))?$")
_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})")
_ENTITY = re.compile(r"\b(llc|l\.l\.c\.|inc|incorporated|corp|corporation|company|co|ltd|lp|llp|jv|"
                     r"joint venture|group|services|solutions|technologies|enterprises|associates)\b\.?", re.I)


# ---------------------------------------------------------------- parsing

def split_tokens(raw, seps=";"):
    parts = re.split("[" + re.escape(seps) + "]", raw or "")
    return [p.strip() for p in parts if p.strip()]


def parse_date(raw):
    m = _DATE.match((raw or "").strip())
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return "%04d-%02d-%02d" % (y, mo, d)


def half_year(iso):
    if not iso:
        return None
    return "%sH%d" % (iso[:4], 1 if int(iso[5:7]) <= 6 else 2)


def in_window(iso, win):
    return iso is not None and win[0] <= iso <= win[1]


def parse_amount(raw):
    s = (raw or "").strip().replace(",", "")
    if s in ("", "-", "—", "–"):
        return "none", None, None
    m = _AMOUNT.match(s)
    if not m:
        return "unparsed", None, None
    return "ok", float(m.group(1)), (m.group(2) or "").upper() or None


def parse_flag(raw):
    s = (raw or "").strip().lower()
    return True if s == "yes" else False if s == "no" else None


def detect_forum(court):
    """Return the first forum whose long name or abbreviation appears in the Court text."""
    c = court or ""
    for name, long_re, abbr_re in FORUMS:
        if long_re.search(c) or abbr_re.search(c):
            return name
    return None


def detect_forum_s2(row):
    f = detect_forum(row.get("Court"))
    if f:
        return f
    text = " ".join((row.get("Case Name") or "", row.get("Source") or ""))
    for name, rx in S2_HINTS:
        if rx.search(text):
            return name
    return None


def proc_text_match(row):
    text = " ".join((row.get("Legal Field Primary") or "", row.get("Legal Field Secondary") or "",
                     row.get("Case Name") or "", row.get("Details") or ""))
    return bool(PROC_TEXT.search(text))


def protester_key(case_name):
    """Normalise a case name to a protester/appellant key (lower case, no suffixes)."""
    s = (case_name or "").strip()
    s = re.sub(r"^(?:matter of|in the matter of|in re|appeal of)\s*:?\s*", "", s, flags=re.I)
    s = re.split(r"\s*(?:--|—|–| - |,|\(|\bd/b/a\b|\bv\.\s|\bvs\.?\s)", s, maxsplit=1)[0]
    s = re.sub(r"\bB-\d{6}(?:\.\d+)?\b", "", s)
    s = _ENTITY.sub("", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def classify(row, cofc_all=False):
    forum = detect_forum(row.get("Court"))
    return _record(row, forum, cofc_all)


def classify_s2(row):
    return _record(row, detect_forum_s2(row), False)


def _record(row, forum, cofc_all):
    parties = split_tokens(row.get("Party(ies)"))
    status, amount, cur = parse_amount(row.get("Monetary Penalty"))
    iso = parse_date(row.get("Date"))
    proc = proc_text_match(row)
    if forum in ("GAO", "ASBCA", "CBCA"):
        procurement = True
    elif forum == "COFC":
        procurement = True if cofc_all else proc
    elif forum == "FEDCIR":
        procurement = proc
    else:
        procurement = False
    name = (row.get("Case Name") or "").strip()
    return {
        "case_id": (row.get("case_id") or "").strip(),
        "forum": forum,
        "core": bool(forum in CORE and procurement),
        "fedcir_proc": bool(forum == "FEDCIR" and procurement),
        "court_raw": (row.get("Court") or "").strip(),
        "date": iso,
        "half": half_year(iso),
        "parties": parties,
        "lawyer": "Lawyer" in parties,
        "pro_se": "Pro Se Litigant" in parties,
        "penalty_raw": (row.get("Monetary Penalty") or "").strip(),
        "money": bool((status == "ok" and amount is not None and amount > 1) or status == "unparsed"),
        "prof": parse_flag(row.get("Professional Sanction")) is True,
        "alleged": parse_flag(row.get("Alleged")),
        "ai_tool_named": bool((row.get("AI Tool") or "").strip()),
        "key": protester_key(name),
        "key_is_entity": bool(_ENTITY.search(re.split(r"\s*(?:--|—|–)", name, maxsplit=1)[0])),
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
            if None in r or not (r.get("case_id") or "").strip():
                bad += 1
                continue
            rows.append(r)
    return header, rows, bad


# ---------------------------------------------------------------- predictions

def _share(k, n):
    return round(k / n, 4) if n else None


def evaluate(recs):
    core = [r for r in recs if r["core"]]
    gao = [r for r in core if r["forum"] == "GAO"]
    res = {}

    n1 = sum(1 for r in core if in_window(r["date"], WIN_2026_JUL))
    res["A1"] = {"n": n1, "threshold": A1_MIN, "timm": sum(TIMM_2026_JUL[f] for f in CORE),
                 "verdict": "held" if n1 >= A1_MIN else "failed"}

    n2 = sum(1 for r in core if in_window(r["date"], WIN_2025))
    res["A2"] = {"n": n2, "threshold": A2_MIN, "timm": TIMM_2025_TOTAL,
                 "verdict": "held" if n2 >= A2_MIN else "failed"}

    c25 = [r for r in core if in_window(r["date"], WIN_2025)]
    c26 = [r for r in core if in_window(r["date"], WIN_2026_OCT)]
    l25, l26 = sum(1 for r in c25 if r["lawyer"]), sum(1 for r in c26 if r["lawyer"])
    if len(c25) >= A3_MIN_N and len(c26) >= A3_MIN_N:
        s25, s26 = _share(l25, len(c25)), _share(l26, len(c26))
        res["A3"] = {"share_2025": s25, "share_2026": s26, "lawyer_2025": l25, "n_2025": len(c25),
                     "lawyer_2026": l26, "n_2026": len(c26), "verdict": "held" if s26 > s25 else "failed"}
    else:
        res["A3"] = {"n_2025": len(c25), "n_2026": len(c26), "verdict": "not testable"}

    g = [r for r in gao if in_window(r["date"], WIN_2025_2026)]
    gp = sum(1 for r in g if r["pro_se"])
    if len(g) >= A4_MIN_N:
        res["A4"] = {"pro_se": gp, "n": len(g), "share": _share(gp, len(g)), "threshold": A4_SHARE,
                     "lawyer": sum(1 for r in g if r["lawyer"]),
                     "verdict": "held" if gp / len(g) >= A4_SHARE else "failed"}
    else:
        res["A4"] = {"n": len(g), "verdict": "not testable"}

    c = [r for r in core if in_window(r["date"], WIN_2025_2026)]
    nm = sum(1 for r in c if r["money"])
    if len(c) >= A5_MIN_N:
        res["A5"] = {"n_money": nm, "n": len(c), "max_allowed": A5_MAX,
                     "verdict": "held" if nm <= A5_MAX else "failed"}
    else:
        res["A5"] = {"n": len(c), "verdict": "not testable"}

    keys = collections.Counter(r["key"] for r in g if r["key"])
    if len(g) >= A6_MIN_N and keys:
        top, cnt = keys.most_common(1)[0]
        ent = any(r["key_is_entity"] for r in g if r["key"] == top)
        res["A6"] = {"top_count": cnt, "n": len(g), "share": _share(cnt, len(g)), "threshold": A6_SHARE,
                     "top_key": top if ent else "(not an entity name; withheld)",
                     "n_distinct_keys": len(keys),
                     "verdict": "held" if cnt / len(g) >= A6_SHARE else "failed"}
    else:
        res["A6"] = {"n": len(g), "verdict": "not testable"}
    return res


# ---------------------------------------------------------------- descriptives

def describe(recs):
    core = [r for r in recs if r["core"]]
    halves = ("2025H1", "2025H2", "2026H1", "2026H2")
    table = {}
    for f in CORE:
        rs = [r for r in core if r["forum"] == f]
        table[f] = {h: {"n": sum(1 for r in rs if r["half"] == h),
                        "lawyer": sum(1 for r in rs if r["half"] == h and r["lawyer"]),
                        "pro_se": sum(1 for r in rs if r["half"] == h and r["pro_se"]),
                        "money": sum(1 for r in rs if r["half"] == h and r["money"]),
                        "prof": sum(1 for r in rs if r["half"] == h and r["prof"])} for h in halves}
        table[f]["before_2025"] = sum(1 for r in rs if r["date"] and r["date"] < "2025-01-01")
        table[f]["no_date"] = sum(1 for r in rs if not r["date"])
    timm = {f: {"timm_2026_jan_jul": TIMM_2026_JUL[f],
                "database_2026_jan_jul": sum(1 for r in core if r["forum"] == f and in_window(r["date"], WIN_2026_JUL))}
            for f in CORE}
    timm["FEDCIR"] = {"timm_2026_jan_jul": TIMM_2026_JUL["FEDCIR"],
                      "database_2026_jan_jul": sum(1 for r in recs if r["fedcir_proc"] and in_window(r["date"], WIN_2026_JUL))}
    court_strings = collections.Counter((r["forum"], r["court_raw"]) for r in recs if r["forum"])
    near = collections.Counter(r["court_raw"] for r in recs if not r["forum"] and NEAR_MISS.search(r["court_raw"]))
    cofc_excluded = sum(1 for r in recs if r["forum"] == "COFC" and not r["core"])
    fed = [r for r in recs if r["forum"] == "FEDCIR"]
    return {
        "by_forum_half_year": table,
        "timm_comparison": timm,
        "matched_court_strings": [{"forum": f, "court": c, "rows": n} for (f, c), n in sorted(court_strings.items())],
        "near_miss_court_strings": [{"court": c, "rows": n} for c, n in near.most_common(40)],
        "cofc_rows_excluded_as_non_procurement": cofc_excluded,
        "fedcir_rows": len(fed), "fedcir_rows_procurement_text": sum(1 for r in fed if r["fedcir_proc"]),
        "core_2025_2026_ai_tool_named": sum(1 for r in core if in_window(r["date"], WIN_2025_2026) and r["ai_tool_named"]),
        "core_2025_2026": sum(1 for r in core if in_window(r["date"], WIN_2025_2026)),
        "core_2025_2026_prof_sanction": sum(1 for r in core if in_window(r["date"], WIN_2025_2026) and r["prof"]),
    }


def analyze(header, raw_rows, n_bad, source=None):
    recs = [classify(r) for r in raw_rows]
    res = {
        "version": VERSION,
        "source": source or {},
        "header": header,
        "n_rows_read": len(raw_rows),
        "n_rows_skipped_malformed": n_bad,
        "n_core": sum(1 for r in recs if r["core"]),
        "primary": evaluate(recs),
        "sensitivity": {
            "S1_cofc_all_rows": evaluate([classify(r, cofc_all=True) for r in raw_rows]),
            "S2_forum_also_from_case_name_or_source": evaluate([classify_s2(r) for r in raw_rows]),
            "S3_exclude_alleged": evaluate([r for r in recs if r["alleged"] is not True]),
        },
        "descriptive": describe(recs),
    }
    return recs, res


# ---------------------------------------------------------------- output

PRED_TEXT = {
    "A1": "Jan-Jul 2026 rows at GAO/COFC/ASBCA/CBCA >= 15 (Timm: 19)",
    "A2": "2025 rows at these forums >= 17 (Timm: 23 in all)",
    "A3": "lawyer share higher in Jan-Oct 2026 than in 2025",
    "A4": "pro se share of GAO rows (2025 to Oct 2026) >= 60%",
    "A5": "at most 1 row (2025 to Oct 2026) with a monetary penalty",
    "A6": "one protester accounts for >= 25% of GAO rows (2025 to Oct 2026)",
}


def render_md(res):
    out = ["# AI-fabricated authority at US procurement tribunals: graded result (analysis %s)" % res["version"], ""]
    src = res.get("source") or {}
    if src:
        out.append("Source: AI Hallucination Cases Database, Damien Charlotin, https://www.damiencharlotin.com/hallucinations/ "
                   "(CC BY 4.0). CSV fetched %s, SHA-256 %s, %s bytes." % (src.get("fetched_at", "?"),
                                                                             src.get("sha256", "?"), src.get("bytes", "?")))
        out.append("")
    out.append("Rows read %d (malformed skipped %d); procurement rows at GAO/COFC/ASBCA/CBCA %d."
               % (res["n_rows_read"], res["n_rows_skipped_malformed"], res["n_core"]))
    out.append("")
    out.append("## Predictions (primary)")
    out.append("")
    for k, v in res["primary"].items():
        detail = {x: y for x, y in v.items() if x != "verdict"}
        out.append("- **%s: %s**. %s. %s" % (k, v["verdict"], PRED_TEXT[k], json.dumps(detail)))
    out.append("")
    out.append("## Sensitivity")
    out.append("")
    out.append("| analysis | A1 | A2 | A3 | A4 | A5 | A6 |")
    out.append("|---|---|---|---|---|---|---|")
    for name, ev in res["sensitivity"].items():
        out.append("| %s | %s |" % (name, " | ".join(ev[k]["verdict"] for k in sorted(ev))))
    d = res["descriptive"]
    out.append("")
    out.append("## Rows by forum and half-year (procurement rows)")
    out.append("")
    out.append("| forum | half | rows | lawyer | pro se | money penalty | prof. sanction |")
    out.append("|---|---|---|---|---|---|---|")
    for f, t in d["by_forum_half_year"].items():
        for h in ("2025H1", "2025H2", "2026H1", "2026H2"):
            c = t[h]
            out.append("| %s | %s | %d | %d | %d | %d | %d |" % (f, h, c["n"], c["lawyer"], c["pro_se"], c["money"], c["prof"]))
    out.append("")
    out.append("## Against Timm (Burr & Forman, 11 Sep 2026), January-July 2026")
    out.append("")
    out.append("| forum | Timm | database |")
    out.append("|---|---|---|")
    for f, t in d["timm_comparison"].items():
        out.append("| %s | %d | %d |" % (f, t["timm_2026_jan_jul"], t["database_2026_jan_jul"]))
    out.append("")
    out.append("Made with AI agents working in MV2's name. Information only, not legal advice.")
    return "\n".join(out) + "\n"


ROW_FIELDS = ("case_id", "forum", "date", "half", "parties", "lawyer", "pro_se", "penalty_raw", "money", "prof",
              "alleged", "ai_tool_named")


def write_outputs(out_dir, recs, res):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False, default=str)
        fh.write("\n")
    with open(os.path.join(out_dir, "results.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(res))
    with open(os.path.join(out_dir, "procurement_rows.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(ROW_FIELDS)
        for r in recs:
            if r["core"] or r["fedcir_proc"]:
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
