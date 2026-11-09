#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered census (version 1.0.0): which provisions of the in-force Code of Federal
Regulations use AI terms, since when, from which agencies, and does any agency's rules of
practice or procedure for its own proceedings mention AI?

Source: the eCFR search API of the Office of the Federal Register
(https://www.ecfr.gov/api/search/v1/results), which searches every version of every CFR
section since 2017 and accepts a point-in-time "date". eCFR robots.txt does not disallow
/api/search/. This file holds the term list, the dates, how a search hit becomes a
provision, the category rules and the summaries; run_job.py does the requests.

Frozen in analysis/cfr-ai-census/PLAN.md before the full download.
Standard library only. Information about public regulations, not legal advice.
"""
from __future__ import annotations

import csv
import datetime
import html
import io
import re

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
API = "https://www.ecfr.gov/api/search/v1/results"
PER_PAGE = 50
MAX_PAGES = 60
DELAY_S = 2

# Exact phrases, each sent in double quotes.
TERMS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "large language model",
    "generative artificial intelligence",
    "generative AI",
    "chatbot",
    "natural language processing",
]
CENSUS_DATE = "2026-11-06"
DATES = ["%d-01-01" % y for y in range(2017, 2027)] + ["2026-07-01", CENSUS_DATE]

# Parts whose own headings (subchapter, part or subpart) say they govern practice or
# procedure in the agency's own proceedings.
PRACTICE = re.compile(r"rules? of (?:practice|procedure)|practice and procedure|practice before|"
                      r"procedural rules|adjudicat|administrative hearings?", re.I)

TAG = re.compile(r"<[^>]+>")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", html.unescape(TAG.sub("", str(s)))).strip()


def provision_key(hit):
    h = hit.get("hierarchy") or {}
    title = str(h.get("title") or "")
    part = str(h.get("part") or "")
    if h.get("section"):
        return "%s CFR %s" % (title, h["section"])
    appx = clean(h.get("appendix"))
    if appx:
        sub = (" Subpart %s" % h["subpart"]) if h.get("subpart") else ""
        return "%s CFR Part %s%s, %s" % (title, part, sub, appx)
    return "%s CFR Part %s [%s]" % (title, part, clean(hit.get("type")) or "?")


def _int(s):
    m = re.match(r"\d+", str(s or ""))
    return int(m.group()) if m else -1


def category(hit):
    h = hit.get("hierarchy") or {}
    title, part = _int(h.get("title")), _int(h.get("part"))
    if title == 15 and 730 <= part <= 774:
        return "export controls (BIS)"
    if title == 15 and part in (7, 791):
        return "ICT supply chain (Commerce)"
    if title == 31 and part == 850:
        return "outbound investment (Treasury)"
    if title == 28 and part == 202:
        return "bulk sensitive data (DOJ)"
    if title == 21 and 800 <= part <= 898:
        return "medical devices (FDA)"
    if title == 42 and 400 <= part <= 699:
        return "Medicare and Medicaid (CMS)"
    if title == 48:
        return "federal procurement (FAR and supplements)"
    return "other"


def rules_of_practice(hit):
    hd = hit.get("headings") or {}
    text = " ".join(clean(hd.get(k)) for k in ("subchapter", "part", "subpart"))
    return bool(PRACTICE.search(text))


def in_force_on(hit, date):
    s = hit.get("starts_on") or ""
    e = hit.get("ends_on") or ""
    return (not s or s <= date) and (not e or e >= date)


def build(dated, undated):
    """dated: {(term, date): [hit]}, undated: {term: [hit]} -> (provisions, timeline, anomalies)."""
    prov = {}
    anomalies = []

    def touch(hit, term):
        k = provision_key(hit)
        p = prov.get(k)
        if p is None:
            h = hit.get("hierarchy") or {}
            hd = hit.get("headings") or {}
            p = prov[k] = {
                "provision": k, "title": str(h.get("title") or ""),
                "agency": clean(hd.get("chapter")), "part": str(h.get("part") or ""),
                "part_heading": clean(hd.get("part")),
                "heading": clean(hd.get("section") or hd.get("appendix")),
                "category": category(hit), "rules_of_practice": rules_of_practice(hit),
                "terms": set(), "first_starts_on": "", "in_force": set(), "excerpt": "",
            }
        p["terms"].add(term)
        s = hit.get("starts_on") or ""
        if s and (not p["first_starts_on"] or s < p["first_starts_on"]):
            p["first_starts_on"] = s
        if not p["excerpt"]:
            p["excerpt"] = clean(hit.get("full_text_excerpt"))[:240]
        return p

    for term in TERMS:
        for hit in undated.get(term, []):
            touch(hit, term)
    per_term = {}
    for (term, date), hits in sorted(dated.items()):
        keys = per_term.setdefault((term, date), set())
        for hit in hits:
            p = touch(hit, term)
            if in_force_on(hit, date):
                p["in_force"].add(date)
                keys.add(p["provision"])
            else:
                anomalies.append({"term": term, "date": date, "provision": p["provision"],
                                  "starts_on": hit.get("starts_on"), "ends_on": hit.get("ends_on")})
    timeline = []
    for d in DATES:
        row = {"date": d, "any_term": sum(1 for p in prov.values() if d in p["in_force"])}
        for t in TERMS:
            row[t] = len(per_term.get((t, d), ()))
        timeline.append(row)
    return prov, timeline, anomalies


ROW_FIELDS = ["provision", "title", "agency", "part", "part_heading", "heading", "category",
              "rules_of_practice", "terms", "first_starts_on", "in_force_on_census_date", "excerpt"]


def rows(prov):
    out = []
    for p in sorted(prov.values(), key=lambda p: (p["first_starts_on"], p["provision"])):
        out.append({
            "provision": p["provision"], "title": p["title"], "agency": p["agency"],
            "part": p["part"], "part_heading": p["part_heading"], "heading": p["heading"],
            "category": p["category"], "rules_of_practice": "yes" if p["rules_of_practice"] else "no",
            "terms": "; ".join(t for t in TERMS if t in p["terms"]),
            "first_starts_on": p["first_starts_on"],
            "in_force_on_census_date": "yes" if CENSUS_DATE in p["in_force"] else "no",
            "excerpt": p["excerpt"],
        })
    return out


def to_csv(dict_rows, fields):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in dict_rows:
        w.writerow(r)
    return buf.getvalue()


def summarize(prov, timeline, anomalies):
    live = [p for p in prov.values() if CENSUS_DATE in p["in_force"]]
    by_cat, by_title, by_agency = {}, {}, {}
    for p in live:
        by_cat[p["category"]] = by_cat.get(p["category"], 0) + 1
        by_title[p["title"]] = by_title.get(p["title"], 0) + 1
        by_agency[p["agency"]] = by_agency.get(p["agency"], 0) + 1
    since_2025 = sum(1 for p in live if p["first_starts_on"] >= "2025-01-01")
    never = [t for t in TERMS if not any(t in p["terms"] for p in prov.values())]
    absent_now = [t for t in TERMS if not any(t in p["terms"] for p in live)]
    return {
        "census_version": VERSION, "census_date": CENSUS_DATE, "terms": TERMS,
        "provisions_ever": len(prov),
        "provisions_in_force_on_census_date": len(live),
        "in_force_first_effective_2025_or_later": since_2025,
        "by_category": dict(sorted(by_cat.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_title": dict(sorted(by_title.items(), key=lambda kv: (-kv[1], _int(kv[0])))),
        "by_agency": dict(sorted(by_agency.items(), key=lambda kv: (-kv[1], kv[0]))),
        "rules_of_practice_in_force": sorted(p["provision"] for p in live if p["rules_of_practice"]),
        "rules_of_practice_ever": sorted(p["provision"] for p in prov.values() if p["rules_of_practice"]),
        "terms_never_matched": never,
        "terms_not_in_force_on_census_date": absent_now,
        "timeline": timeline,
        "date_filter_anomalies": len(anomalies),
    }


def results_md(summary, rows_, queries_ok):
    L = ["# AI terms in the in-force Code of Federal Regulations: census %s results" % VERSION, "",
         "Generated by run_job.py from the eCFR search API. Plan: PLAN.md (frozen before the full "
         "download). Information about public regulations, not legal advice. Made with AI agents "
         "working in MV2's (Munim, Inc.) name.", "",
         "- Census date: %s" % summary["census_date"],
         "- Every query complete: %s" % ("yes" if queries_ok else "NO (see queries.json)"),
         "- Hits outside their query date (excluded): %d" % summary["date_filter_anomalies"],
         "- Distinct provisions that ever used a term (2017 on): %d" % summary["provisions_ever"],
         "- In force on the census date: %d" % summary["provisions_in_force_on_census_date"],
         "- Of those, first in force in 2025 or later: %d" % summary["in_force_first_effective_2025_or_later"],
         "- In an agency's own rules of practice or procedure (in force): %d" % len(summary["rules_of_practice_in_force"]),
         "- Terms never matched: %s" % (", ".join(summary["terms_never_matched"]) or "none"), "",
         "## Provisions in force on each date", "",
         "| date | any term | " + " | ".join(TERMS) + " |",
         "|---|---|" + "---|" * len(TERMS)]
    for r in summary["timeline"]:
        L.append("| %s | %d | " % (r["date"], r["any_term"]) + " | ".join(str(r[t]) for t in TERMS) + " |")
    L += ["", "## In force on the census date, by category", "", "| category | provisions |", "|---|---|"]
    for k, v in summary["by_category"].items():
        L.append("| %s | %d |" % (k, v))
    L += ["", "## In force on the census date, by agency (CFR chapter)", "", "| agency | provisions |", "|---|---|"]
    for k, v in summary["by_agency"].items():
        L.append("| %s | %d |" % (k or "(none)", v))
    L += ["", "## Every provision", "", "| provision | heading | category | terms | first in force | in force on census date |",
          "|---|---|---|---|---|---|"]
    for r in rows_:
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            r["provision"], r["heading"].replace("|", "/"), r["category"], r["terms"],
            r["first_starts_on"], r["in_force_on_census_date"]))
    return "\n".join(L) + "\n"
