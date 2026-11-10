#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered census (version 1.0.0): when US federal agency tribunals (and the two
Article I courts that hear agency-type cases) rule on AI-fabricated or AI-garbled
authority, which authority do their decisions cite?

MV2's CFR AI-terms census (analysis/cfr-ai-census.md) found that no agency rules of practice
or procedure in the Code of Federal Regulations mention AI. So an agency tribunal that meets
a fabricated citation has to reach for something else: its general signature, sanctions or
practitioner-conduct regulation, Federal Rule of Civil Procedure 11 by analogy, inherent
authority, the ABA Model Rules, or one of the two named AI instruments that exist outside
the CFR (the USPTO's April 2024 guidance, 89 FR 25609, and EOIR Policy Memorandum 25-40 of
8 August 2025).

Rows: AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0), CSV export. Texts: the
documents the database links. This file holds the row filter, the citation patterns and the
grading; run_job.py does the downloads.

Frozen in analysis/agency-ai-authority/PLAN.md before any data row is read.
Standard library only. Information about public decisions, not legal advice.
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
CUTOFF = "2026-11-09"          # last decision date counted
USPTO_GUIDANCE_DATE = "2024-04-11"
MIN_CHARS = 1500               # a document with less extracted text is "unreadable"

_STATES = ("Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|"
           "Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|"
           "Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|"
           "New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|"
           "Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|"
           "Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|District of Columbia|"
           "Puerto Rico")
STATE_NAME = re.compile(r"\b(?:%s)\b" % _STATES)

# Forums, tried in this order on the free-text Court column. Stratum "article_i" = the two
# Article I courts; stratum "agency" = federal agency adjudicators.
ARTICLE_I = (
    ("CAVC", re.compile(r"Court of Appeals for Veterans Claims|\bCAVC\b|\bVet\.\s?App\.")),
    ("TAXCT", re.compile(r"(?:United States|U\.\s?S\.|\bUS)\s+Tax Court|^\s*Tax Court\b|\bUSTC\b")),
)
# A Court value naming one of these is a court reviewing an agency, not the agency itself.
REVIEW_COURT = re.compile(r"District Court|\bDistrict of\b|Circuit|\bCir\b|\bCir\.|Court of Appeals|"
                          r"Supreme Court|Bankruptcy|Court of Federal Claims|"
                          r"^(?:[NSEWMC]\.\s?D\.|D\.)\s?[A-Z]", re.I)
PROCUREMENT = re.compile(r"Government Accountability Office|\bGAO\b|Comptroller General|"
                         r"Board of Contract Appeals|\bASBCA\b|\bCBCA\b", re.I)
AGENCY = (
    ("USPTO", re.compile(r"Trademark Trial and Appeal Board|\bTTAB\b|Patent Trial and Appeal Board|"
                         r"\bPTAB\b|\bUSPTO\b|Patent and Trademark Office|Office of Enrollment and "
                         r"Discipline|\bOED\b|Board of Patent Appeals"), False),
    ("EOIR", re.compile(r"Board of Immigration Appeals|\bBIA\b|Immigration Court|Immigration Judge|"
                        r"\bEOIR\b|Executive Office for Immigration Review"), False),
    ("MSPB", re.compile(r"Merit Systems Protection Board|\bMSPB\b"), False),
    ("BVA", re.compile(r"Board of Veterans'?\s?Appeals|\bBVA\b"), False),
    ("NLRB", re.compile(r"National Labor Relations Board|\bNLRB\b"), False),
    ("SEC", re.compile(r"Securities and Exchange Commission|\bSEC\b"), True),
    ("DOL", re.compile(r"(?:U\.\s?S\.\s|United States\s|\bUS\s)?Department of Labor|Administrative Review "
                       r"Board|Benefits Review Board|Office of Administrative Law Judges|\bOALJ\b|"
                       r"\bDOL\b"), True),
    ("OTHER_FED", re.compile(r"Federal Labor Relations Authority|\bFLRA\b|Equal Employment Opportunity "
                             r"Commission|\bEEOC\b|Federal Communications Commission|\bFCC\b|Federal "
                             r"Energy Regulatory Commission|\bFERC\b|Occupational Safety and Health "
                             r"Review Commission|\bOSHRC\b|Social Security|Federal Trade Commission|"
                             r"\bFTC\b|International Trade Commission|\bUSITC\b|Copyright Claims Board|"
                             r"Copyright Royalty|Administrative Appeals Office|\bAAO\b|Federal Mine "
                             r"Safety|Surface Transportation Board|National Transportation Safety Board|"
                             r"\bNTSB\b|Federal Maritime Commission|Departmental Appeals Board|"
                             r"Office of Medicare Hearings|Civilian Personnel Appeals"), True),
)
# Court values that look like tribunals but matched nothing: printed for auditing the filter.
NEAR_MISS = re.compile(r"Board|Commission|Administrative|Agency|Office|Department|Judge|Tribunal|"
                       r"Authority|Hearing", re.I)

# --- citation patterns (applied to the normalized decision text) -------------------------
CFR = r"(?:C\.\s?F\.\s?R\.|CFR|§+|[Rr]ule|[Ss]ection)\s?(?:§+\s?)?"
AI_INSTRUMENTS = {
    "uspto_ai_guidance_2024": re.compile(r"89\s?(?:FR|Fed\.?\s?Reg\.?)\s?25,?6(?:09|1\d)|Guidance on "
                                         r"(?:the\s)?Use of Artificial Intelligence[- ]Based Tools", re.I),
    "eoir_pm_25_40": re.compile(r"\bPM\s?(?:No\.\s?)?25-40\b|Policy Memorandum\s?(?:No\.\s?)?25-40\b|"
                                r"Use of Generative Artificial Intelligence in EOIR Proceedings", re.I),
}
# Each forum's own signature, sanctions or practitioner-conduct provisions.
FORUM_RULE = {
    "USPTO": re.compile(CFR + r"(?:11\.18|2\.193|42\.1[12]|41\.128|11\.101|11\.303|11\.804)(?!\d)"),
    "EOIR": re.compile(CFR + r"(?:1003\.10[1-9]|1292\.3|1003\.1\s?\(d\)\s?\(2\))(?!\d)"),
    "MSPB": re.compile(r"(?<![\d.])1201\.43(?!\d)"),
    "BVA": re.compile(CFR + r"(?:14\.632|14\.633)(?!\d)"),
    "NLRB": re.compile(r"(?<![\d.])102\.177(?!\d)"),
    "SEC": re.compile(r"(?<![\d.])201\.(?:180|102)(?!\d)"),
    "DOL": re.compile(r"29\s?C\.?\s?F\.?\s?R\.?\s?(?:§+\s?)?18\.(?:35|12|57)(?!\d)"),
    "OTHER_FED": None,
    "TAXCT": re.compile(r"\bRule\s?33\s?\(b\)|\bRule\s?201\s?\(a\)|(?<![\d.])6673(?!\d)"),
    "CAVC": re.compile(r"\bRule\s?(?:38|46)\b"),
}
USPTO_1118 = re.compile(r"(?<![\d.])11\.18(?!\d)")
TAX_6673 = re.compile(r"(?<![\d.])6673(?!\d)")
GENERAL = {
    "frcp_11": re.compile(r"Fed(?:eral)?\.?\s?R(?:ules?)?\.?\s?(?:of\s)?Civ(?:il)?\.?\s?P(?:roc(?:edure)?)?\.?"
                          r"\s?11\b|\bRule 11\b(?!\.\d)"),
    "inherent": re.compile(r"inherent (?:authority|power)", re.I),
    "model_rules": re.compile(r"Model Rules? of Professional Conduct|\bRule\s?3\.3\b|(?<![\d.])3\.3\s?\(a\)"),
    "usc_1001": re.compile(r"18\s?U\.?\s?S\.?\s?C\.?\s?(?:§+\s?)?1001\b"),
    "mata": re.compile(r"Mata v\.?\s?Avianca"),
}
AI_WORDS = re.compile(r"artificial intelligence|generative|\bAI\b|ChatGPT|hallucinat", re.I)

# Grading thresholds (fixed in PLAN.md).
Q1_MIN_N, Q1_SHARE = 10, 0.25
Q2_MIN_N, Q2_SHARE = 10, 0.40
Q3_MIN_N = 10
Q4_MIN_N, Q4_SHARE = 5, 0.50
Q5_MIN_N, Q5_SHARE = 5, 0.50
Q6_MIN_N, Q6_SHARE = 5, 0.50
Q7_MAX = 1
Q8_MIN_N, Q8_SHARE = 10, 0.15


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


def forum_of(court):
    """Return (forum, stratum, reason) for a Court value. forum is None when out of scope."""
    c = (court or "").strip()
    for name, rx in ARTICLE_I:
        if rx.search(c):
            if name == "TAXCT" and STATE_NAME.search(c):
                return None, None, "state tax court"
            return name, "article_i", "matched"
    if PROCUREMENT.search(c):
        return None, None, "procurement (other study)"
    hit = None
    for name, rx, state_sensitive in AGENCY:
        if rx.search(c):
            hit = (name, state_sensitive)
            break
    if hit is None:
        return None, None, ("near miss" if NEAR_MISS.search(c) else "other")
    if REVIEW_COURT.search(c):
        return None, None, "review court"
    if hit[1] and STATE_NAME.search(c):
        return None, None, "state agency"
    return hit[0], "agency", "matched"


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
    """Rows in scope, plus a table of every Court value that matched, was excluded or
    looked like a tribunal, with how it was classified (for auditing the filter)."""
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
        court = (r.get("Court") or "").strip()
        forum, stratum, why = forum_of(court)
        if why != "other":
            courts[court, forum or "", why] += 1
        if forum is None:
            continue
        iso = parse_date(r.get("Date"))
        if iso is not None and iso > CUTOFF:
            continue
        rows.append({
            "case_id": (r.get("case_id") or "").strip(),
            "case_name": (r.get("Case Name") or "").strip(),
            "court": court,
            "forum": forum,
            "stratum": stratum,
            "date": iso,
            "party": party_of(r.get("Party(ies)")),
            "url": doc_url(r.get("Source"), r.get("Pointer")),
        })
    rows.sort(key=lambda x: (x["stratum"], x["forum"], x["date"] or "", x["case_id"]))
    court_table = [{"court": c, "forum": f, "classified": w, "rows": n}
                   for (c, f, w), n in sorted(courts.items())]
    return rows, court_table


def normalize(text):
    text = (text or "").replace("­", "").replace(" ", " ").replace("‑", "-")
    text = re.sub(r"(\d)\s*[-‐–]\s*\n\s*(\d)", r"\1-\2", text)
    return re.sub(r"\s+", " ", text).strip()


FLAG_KEYS = ("ai_instrument",) + tuple(AI_INSTRUMENTS) + ("forum_rule", "uspto_11_18", "tax_6673") + \
    tuple(GENERAL) + ("ai_words",)


def classify_text(forum, text):
    """Flags for one decision's text. `excerpts` (keyed by flag) are for private review only."""
    t = normalize(text)
    out = {"chars": len(t), "readable": len(t) >= MIN_CHARS, "excerpts": {}}
    for k in FLAG_KEYS:
        out[k] = False
    if not out["readable"]:
        return out

    def hit(key, rx):
        if rx is None:
            return False
        m = rx.search(t)
        if m:
            out["excerpts"][key] = t[max(0, m.start() - 200): m.end() + 200]
            return True
        return False

    for k, rx in AI_INSTRUMENTS.items():
        out[k] = hit(k, rx)
    out["ai_instrument"] = any(out[k] for k in AI_INSTRUMENTS)
    out["forum_rule"] = hit("forum_rule", FORUM_RULE.get(forum))
    out["uspto_11_18"] = forum == "USPTO" and hit("uspto_11_18", USPTO_1118)
    out["tax_6673"] = forum == "TAXCT" and hit("tax_6673", TAX_6673)
    for k, rx in GENERAL.items():
        out[k] = hit(k, rx)
    out["ai_words"] = bool(AI_WORDS.search(t))
    return out


def _share(rows, key):
    n = len(rows)
    k = sum(1 for r in rows if r.get(key))
    return {"n": n, "k": k, "share": round(k / n, 3) if n else None}


def _verdict(n, min_n, ok):
    return "not testable" if n < min_n else ("held" if ok else "failed")


def grade(rows):
    """rows: dicts from select_rows() updated with classify_text() output and doc_status."""
    read = [r for r in rows if r.get("doc_status") == "ok" and r.get("readable")]
    agency = [r for r in read if r["stratum"] == "agency"]
    art1 = [r for r in read if r["stratum"] == "article_i"]
    res = {"version": VERSION, "cutoff": CUTOFF}
    res["counts"] = {
        "rows_in_scope": len(rows),
        "by_forum": dict(collections.Counter(r["forum"] for r in rows)),
        "by_doc_status": dict(collections.Counter(r.get("doc_status") for r in rows)),
        "unreadable": sum(1 for r in rows if r.get("doc_status") == "ok" and not r.get("readable")),
        "readable": len(read),
        "readable_by_forum": dict(collections.Counter(r["forum"] for r in read)),
        "readable_by_year": dict(collections.Counter(r["date"][:4] if r["date"] else "undated" for r in read)),
        "readable_by_party": dict(collections.Counter(r["party"] for r in read)),
    }
    forums = sorted(set(r["forum"] for r in read))
    res["flags_by_forum"] = {f: {k: _share([r for r in read if r["forum"] == f], k)
                                 for k in FLAG_KEYS} for f in forums}
    res["flags_by_stratum"] = {"agency": {k: _share(agency, k) for k in FLAG_KEYS},
                               "article_i": {k: _share(art1, k) for k in FLAG_KEYS}}
    none_cited = [r for r in read if not any(r.get(k) for k in ("ai_instrument", "forum_rule", "frcp_11",
                                                                 "inherent", "model_rules", "usc_1001"))]
    res["no_listed_authority"] = {"n": len(none_cited), "of": len(read)}

    p = {}
    s = _share(agency, "ai_instrument")
    p["Q1"] = (_verdict(s["n"], Q1_MIN_N, s["n"] and s["share"] < Q1_SHARE), s)
    s = _share(agency, "forum_rule")
    p["Q2"] = (_verdict(s["n"], Q2_MIN_N, s["n"] and s["share"] >= Q2_SHARE), s)
    a, b = _share(agency, "forum_rule"), _share(agency, "frcp_11")
    p["Q3"] = (_verdict(a["n"], Q3_MIN_N, a["k"] > b["k"]), {"forum_rule": a, "frcp_11": b})
    us = [r for r in read if r["forum"] == "USPTO"]
    s = _share(us, "uspto_11_18")
    p["Q4"] = (_verdict(s["n"], Q4_MIN_N, s["n"] and s["share"] >= Q4_SHARE), s)
    us_post = [r for r in us if r["date"] and r["date"] >= USPTO_GUIDANCE_DATE]
    s = _share(us_post, "uspto_ai_guidance_2024")
    p["Q5"] = (_verdict(s["n"], Q5_MIN_N, s["n"] and s["share"] < Q5_SHARE), s)
    tx = [r for r in read if r["forum"] == "TAXCT"]
    s = _share(tx, "tax_6673")
    p["Q6"] = (_verdict(s["n"], Q6_MIN_N, s["n"] and s["share"] < Q6_SHARE), s)
    early = [r for r in read if r["date"] and r["date"] < USPTO_GUIDANCE_DATE]
    k = sum(1 for r in early if r["ai_instrument"])
    p["Q7"] = ("held" if k <= Q7_MAX else "failed", {"n": len(early), "matches": k})
    s = _share(read, "mata")
    p["Q8"] = (_verdict(s["n"], Q8_MIN_N, s["n"] and s["share"] >= Q8_SHARE), s)
    res["predictions"] = {k2: {"verdict": v2, "detail": d2} for k2, (v2, d2) in p.items()}
    return res


PUBLIC_COLUMNS = ("case_id", "stratum", "forum", "court", "date", "party", "doc_status", "chars",
                  "readable") + FLAG_KEYS + ("doc_sha256",)


def rows_csv(rows):
    """Public per-decision table: no case names, no excerpts (read those at the source)."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(PUBLIC_COLUMNS)
    for r in rows:
        w.writerow([("" if r.get(c) is None else r.get(c)) for c in PUBLIC_COLUMNS])
    return buf.getvalue()


PRED_TEXT = {
    "Q1": "agency decisions citing a named AI instrument (USPTO 2024 guidance or EOIR PM 25-40) < 25%",
    "Q2": "agency decisions citing the forum's own signature/sanction/conduct regulation >= 40%",
    "Q3": "agency decisions: forum's own regulation cited more often than FRCP 11",
    "Q4": "USPTO decisions citing 37 CFR 11.18 >= 50%",
    "Q5": "USPTO decisions from 2024-04-11 citing the USPTO AI guidance < 50%",
    "Q6": "Tax Court decisions citing 26 U.S.C. 6673 < 50%",
    "Q7": "method check: AI-instrument patterns match at most 1 decision dated before 2024-04-11",
    "Q8": "Mata v. Avianca cited in >= 15% of all readable decisions",
}


def results_md(res, source):
    L = ["# Agency AI-authority census %s: results" % VERSION, "",
         "Data: AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0), CSV SHA-256 `%s`, "
         "fetched %s. Decision texts: the documents the database links. Information about public "
         "decisions, not legal advice. Made with AI agents working in MV2's name." %
         (source.get("sha256", "?"), source.get("fetched_at", "?")), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, PRED_TEXT[k], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Flags by forum (k of n readable)", "",
          "| forum | n | " + " | ".join(FLAG_KEYS) + " |", "|---|---|" + "---|" * len(FLAG_KEYS)]
    for f, d in res["flags_by_forum"].items():
        n = next(iter(d.values()))["n"]
        L.append("| %s | %d | %s |" % (f, n, " | ".join(str(d[k]["k"]) for k in FLAG_KEYS)))
    L += ["", "Decisions citing none of: AI instrument, forum rule, FRCP 11, inherent authority, "
          "Model Rules, 18 U.S.C. 1001: `%s`" % json.dumps(res["no_listed_authority"]), ""]
    return "\n".join(L)
