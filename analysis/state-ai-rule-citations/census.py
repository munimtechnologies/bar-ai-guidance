#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered census (version 1.0.0): do state-court decisions about AI-fabricated
citations cite the state's new AI verification rule?

Rules: New York 22 NYCRR Part 161, Florida Rule of General Practice and Judicial
Administration 2.515 (as amended, subdivision (d)(2)(D)), Connecticut Practice Book
Section 4-9, Indiana Trial Rule 11 (as amended, with new Rules 11.1 and 11.2).

Rows: AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0), CSV export. The decision
texts are the documents the database links. This file holds the row filter, the
citation patterns and the grading; run_job.py does the downloads.

Frozen in analysis/state-ai-rule-citations/PLAN.md before any decision text is read.
Standard library only. Information about public court decisions, not legal advice.
"""
from __future__ import annotations

import collections
import csv
import datetime
import io
import json
import re
import sys

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
SITE = "https://www.damiencharlotin.com"
CUTOFF = "2026-11-08"          # last decision date counted
PRE_START = "2025-11-01"       # first decision date of the pre period
PLACEBO_END = "2026-03-24"     # H6: before New York adopted Part 161 (25 March 2026)
MIN_CHARS = 1500               # a document with less extracted text is "unreadable"

# Effective dates, from the entries of data/guidance.json (index 0.16.1).
RULES = {
    "NY": {"rule": "22 NYCRR Part 161", "effective": "2026-06-01", "entry": "ny-ucs-part-161"},
    "FL": {"rule": "Fla. R. Gen. Prac. & Jud. Admin. 2.515", "effective": "2026-06-15",
           "entry": "fl-sc2026-0673-rule-2-515"},
    "CT": {"rule": "Connecticut Practice Book Section 4-9", "effective": "2026-06-23",
           "entry": "ct-practice-book-4-9-2026"},
    "IN": {"rule": "Indiana Trial Rule 11 (and 11.1, 11.2)", "effective": "2026-08-01",
           "entry": "in-trial-rule-11-2026"},
}

STATE_NAMES = {
    "NY": re.compile(r"\bNew York\b|\bNY\b|\bN\.Y\."),
    "FL": re.compile(r"\bFlorida\b|\bFla\."),
    "CT": re.compile(r"\bConnecticut\b|\bConn\."),
    "IN": re.compile(r"\bIndiana\b|\bInd\."),
}
# A Court value naming one of the four states is a STATE court unless this matches.
FEDERAL = re.compile(r"^(?:[NSEWMC]\.\s?D\.|D\.)\s|Bankruptcy|\bCir\b|\bCir\.|Circuit|Federal|"
                     r"\bU\.\s?S\.|\bBIA\b|International Trade", re.I)

# Primary measure: the decision cites the state's new rule.
NEW_RULE = {
    "NY": re.compile(r"\b[Pp]art\s?161\b|NYCRR\s?(?:[Pp]art\s?|§+\s?)?161\b|§+\s?161\.\d+"),
    "FL": re.compile(r"(?<![\d.$])2\.515(?!\d)"),
    "CT": re.compile(r"(?:Practice Book|P\.\s?B\.)\s?(?:§+|[Ss]ec(?:tion|s?\.)|[Ss]ections)?\s?4-9\b|"
                     r"§+\s?4-9\b|Practice Book\s?(?:§§|[Ss]ections)[^.;]{0,40}?\b4-9\b"),
    "IN": re.compile(r"\bTrial\s?Rules?\s?11(?:\.[12])?\b|\bT\.\s?R\.\s?11(?:\.[12])?\b"),
}
# Reported, not part of the primary measure.
SECONDARY = {
    "ny_part_130": ("NY", re.compile(r"\b[Pp]art\s?130\b|\b130-1\.1a?\b|NYCRR\s?(?:[Pp]art\s?|§+\s?)?130\b")),
    "fl_2515_d2": ("FL", re.compile(r"2\.515\s?\(d\)\s?\(2\)")),
    "fl_57105": ("FL", re.compile(r"(?<![\d.])57\.105(?!\d)")),
    "ct_85_2_or_62_6": ("CT", re.compile(r"(?:Practice Book|P\.\s?B\.|§+)\s?(?:§+\s?)?(?:85-2|62-6)\b")),
    "in_11_1_or_11_2": ("IN", re.compile(r"\b(?:Trial\s?Rule|T\.\s?R\.)\s?11\.[12]\b")),
}
AI_WORDS = re.compile(r"artificial intelligence|generative|\bAI\b|ChatGPT|hallucinat", re.I)

# Grading thresholds (fixed in PLAN.md).
H1_MIN_N, H1_SHARE = 10, 0.5
H2_MIN_N = 8
H34_MIN_N = 4
H5_MIN_N = 5
H6_MAX = 1


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})")


def parse_date(raw):
    m = _DATE.match((raw or "").strip())
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return "%04d-%02d-%02d" % (y, mo, d)


def state_of(court):
    """Return (state, reason). state is None unless exactly one of the four states is
    named and the court is not federal."""
    court = (court or "").strip()
    hits = [s for s, rx in STATE_NAMES.items() if rx.search(court)]
    if not hits:
        return None, "other state"
    if FEDERAL.search(court):
        return None, "federal"
    if len(hits) > 1:
        return None, "ambiguous"
    return hits[0], "state court"


def period_of(state, iso):
    if iso is None:
        return None
    eff = RULES[state]["effective"]
    if eff <= iso <= CUTOFF:
        return "post"
    if PRE_START <= iso < eff:
        return "pre"
    return None


def party_of(raw):
    raw = raw or ""
    if "Lawyer" in raw:
        return "lawyer"
    if "Pro Se" in raw:
        return "pro_se"
    return "other"


def doc_url(source, pointer=""):
    from urllib.parse import quote
    s = (source or "").strip()
    if s.startswith("/documents/"):
        return SITE + quote(s, safe="/%:@()',;=&+$!*~-._")
    for cand in (s, (pointer or "").strip()):
        if cand.startswith("https://") or cand.startswith("http://"):
            return cand
    return None


def select_rows(csv_text):
    """Rows of the database in scope, plus a table of every Court value seen for the
    four states with how it was classified (for auditing the filter)."""
    csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
    reader = csv.DictReader(io.StringIO(csv_text))
    missing = [c for c in ("case_id", "Court", "State(s)", "Date", "Party(ies)", "Source")
               if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError("missing columns: %s" % ", ".join(missing))
    rows, courts = [], collections.Counter()
    for r in reader:
        if "USA" not in (r.get("State(s)") or ""):
            continue
        st, why = state_of(r.get("Court"))
        if why != "other state":
            courts[(r.get("Court") or "").strip(), why] += 1
        if st is None:
            continue
        iso = parse_date(r.get("Date"))
        per = period_of(st, iso)
        if per is None:
            continue
        rows.append({
            "case_id": (r.get("case_id") or "").strip(),
            "case_name": (r.get("Case Name") or "").strip(),
            "court": (r.get("Court") or "").strip(),
            "state": st,
            "date": iso,
            "period": per,
            "party": party_of(r.get("Party(ies)")),
            "url": doc_url(r.get("Source"), r.get("Pointer")),
        })
    rows.sort(key=lambda x: (x["state"], x["date"], x["case_id"]))
    court_table = [{"court": c, "classified": w, "rows": n} for (c, w), n in sorted(courts.items())]
    return rows, court_table


def normalize(text):
    text = (text or "").replace("­", "").replace(" ", " ").replace("‑", "-")
    text = re.sub(r"(\d)\s*[-‐–]\s*\n\s*(\d)", r"\1-\2", text)
    return re.sub(r"\s+", " ", text).strip()


def classify_text(state, text):
    """Matches in one decision's extracted text. `excerpt` is for private review only."""
    t = normalize(text)
    out = {"chars": len(t), "readable": len(t) >= MIN_CHARS, "cites_new_rule": False,
           "ai_words": bool(AI_WORDS.search(t)), "excerpt": ""}
    for key, (st, rx) in SECONDARY.items():
        out[key] = bool(st == state and rx.search(t))
    if not out["readable"]:
        return out
    m = NEW_RULE[state].search(t)
    if m:
        out["cites_new_rule"] = True
        out["excerpt"] = t[max(0, m.start() - 200): m.end() + 200]
    return out


def _share(rows):
    n = len(rows)
    k = sum(1 for r in rows if r["cites_new_rule"])
    return {"n": n, "cites": k, "share": round(k / n, 3) if n else None}


def grade(rows):
    """rows: dicts from select_rows() updated with classify_text() output and doc_status."""
    read = [r for r in rows if r.get("doc_status") == "ok" and r.get("readable")]
    post = [r for r in read if r["period"] == "post"]
    pre = [r for r in read if r["period"] == "pre"]
    res = {"version": VERSION, "cutoff": CUTOFF, "pre_start": PRE_START, "rules": RULES}

    res["counts"] = {
        "rows_in_scope": len(rows),
        "by_doc_status": dict(collections.Counter(r.get("doc_status") for r in rows)),
        "unreadable": sum(1 for r in rows if r.get("doc_status") == "ok" and not r.get("readable")),
        "readable": len(read),
    }
    table = {}
    for st in RULES:
        table[st] = {"post": _share([r for r in post if r["state"] == st]),
                     "pre": _share([r for r in pre if r["state"] == st])}
    res["by_state"] = table
    res["post_by_party"] = {p: _share([r for r in post if r["party"] == p])
                            for p in ("lawyer", "pro_se", "other")}
    res["secondary_post"] = {k: sum(1 for r in post if r.get(k)) for k in SECONDARY}
    res["secondary_pre"] = {k: sum(1 for r in pre if r.get(k)) for k in SECONDARY}

    h = {}
    s = _share(post)
    h["H1"] = ("not testable" if s["n"] < H1_MIN_N else
               "held" if s["share"] < H1_SHARE else "failed", s)
    ny = [r for r in post if r["state"] == "NY"]
    n130 = sum(1 for r in ny if r.get("ny_part_130"))
    n161 = sum(1 for r in ny if r["cites_new_rule"])
    h["H2"] = ("not testable" if len(ny) < H2_MIN_N else "held" if n130 > n161 else "failed",
               {"n": len(ny), "part_130": n130, "part_161": n161})
    for key, st in (("H3", "FL"), ("H4", "IN")):
        a, b = table[st]["post"], table[st]["pre"]
        if a["n"] < H34_MIN_N or b["n"] < H34_MIN_N:
            v = "not testable"
        else:
            v = "held" if a["share"] > b["share"] else "failed"
        h[key] = (v, {"post": a, "pre": b})
    lw, ps = res["post_by_party"]["lawyer"], res["post_by_party"]["pro_se"]
    if lw["n"] < H5_MIN_N or ps["n"] < H5_MIN_N:
        v = "not testable"
    else:
        v = "held" if lw["share"] > ps["share"] else "failed"
    h["H5"] = (v, {"lawyer": lw, "pro_se": ps})
    plac = [r for r in pre if r["state"] in ("NY", "CT") and r["date"] <= PLACEBO_END]
    k = sum(1 for r in plac if r["cites_new_rule"])
    h["H6"] = ("held" if k <= H6_MAX else "failed", {"n": len(plac), "matches": k})
    res["predictions"] = {k2: {"verdict": v2, "detail": d2} for k2, (v2, d2) in h.items()}
    return res


PUBLIC_COLUMNS = ("case_id", "state", "court", "date", "period", "party", "doc_status", "chars",
                  "readable", "cites_new_rule", "ai_words") + tuple(SECONDARY) + ("doc_sha256",)


def rows_csv(rows):
    """Public per-decision table: no case names, no excerpts (read those at the source)."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(PUBLIC_COLUMNS)
    for r in rows:
        w.writerow([("" if r.get(c) is None else r.get(c)) for c in PUBLIC_COLUMNS])
    return buf.getvalue()


def results_md(res, source):
    L = ["# State AI rule citation census %s: results" % VERSION, "",
         "Data: AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0), CSV SHA-256 `%s`, "
         "fetched %s. Decision texts: the documents the database links. Information about public "
         "decisions, not legal advice. Made with AI agents working in MV2's name." %
         (source.get("sha256", "?"), source.get("fetched_at", "?")), "",
         "Counts: %s" % json.dumps(res["counts"]), "",
         "| state | rule | effective | post: cite / readable | pre: cite / readable |",
         "|---|---|---|---|---|"]
    for st, info in RULES.items():
        a, b = res["by_state"][st]["post"], res["by_state"][st]["pre"]
        L.append("| %s | %s | %s | %d / %d | %d / %d |" % (st, info["rule"], info["effective"],
                                                         a["cites"], a["n"], b["cites"], b["n"]))
    L += ["", "| prediction | verdict | detail |", "|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | `%s` |" % (k, v["verdict"], json.dumps(v["detail"])))
    L += ["", "Secondary (post period): `%s`" % json.dumps(res["secondary_post"]),
          "", "Secondary (pre period): `%s`" % json.dumps(res["secondary_pre"]), ""]
    return "\n".join(L)
