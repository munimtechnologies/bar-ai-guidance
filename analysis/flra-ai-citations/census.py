#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""FLRA archive AI-citation census 1.0.0 (pre-registered; see PLAN.md next to this file).

Pure functions only: listing parser, text classification, coverage matching and grading.
Fetching lives in run_job.py. Standard library only. Information about public decisions,
not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import html as htmlmod
import io
import json
import re

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
START = "2022-01-01"          # first issuance date in the frame
END = "2026-11-10"            # last issuance date in the frame
FORUM = "FLRA"
PROXIMITY = 2000              # characters between an AI term and a citation-problem term
NEAR = 2500                   # characters around an AI term for the other-body flag

FLRA_LIST = "https://www.flra.gov/decisions/authority-decisions?order=issuance_date&sort=desc&page=%d"
FLRA_BASE = "https://www.flra.gov"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

DATE_RE = re.compile(
    r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b"
    r"|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),\s*(20\d\d)\b"
    r"|\b(20\d\d)-(\d\d)-(\d\d)\b")

FLRA_HREF = re.compile(r"""href=["']((?:https?://www\.flra\.gov)?/decisions/v(\d+)/(\d+)-(\d+)[a-z0-9_-]*)["']""", re.I)
FLRA_CITE = re.compile(r"\b(\d{2})\s+FLRA\s+(?:No\.\s*)?(\d+)\b")

# --- text classification (frozen) ---------------------------------------------------------
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?)\b"
    r"|(?-i:\(\s*[\"\u201c]?A[Il][\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\blarge language models?\b|\bLLMs?\b", re.I)
# PDF-derived text can read "AI" as "Al" (lower-case L), so both are accepted; the "AI"/"Al"
# parts are case-sensitive so that "(AL)" (Alabama) or "al" never match.
CITE_PROBLEM = re.compile(
    r"\bfictitious\b|\bnon-?existent\b|\bdo(?:es)? not exist\b|\bdid not exist\b"
    r"|\bfabricated\s+(?:citations?|cases?|quotations?|quotes|authorit\w*|decisions?)"
    r"|\bhallucinat\w*|\bghost\s+citations?\b|\bfake\s+(?:citations?|cases?|quotations?)", re.I)

OWN_RULE = re.compile(r"\b5\s*C\.?\s*F\.?\s*R\.?\s*(?:\u00a7+\s*)?24[23]\d\.\d+|\u00a7+\s*24[23]\d\.\d+\b")
OTHER_BODY = re.compile(r"\bNLRB\b|National Labor Relations Board|\bGAO\b|\bB-\d{6}\b|\bFed\.\s?Reg\.|\bUSPTO\b"
                        r"|Patent and Trademark Office|\bMSPB\b|Merit Systems Protection|\bEOIR\b")
FRCP_11 = re.compile(r"(?:Fed\.\s?R\.\s?Civ\.\s?P\.|Federal Rules? of Civil Procedure|FRCP)\s*(?:Rule\s*)?11\b"
                     r"|\bRule\s+11\b")
MATA = re.compile(r"\bMata\s+v\.?\s+Avianca\b")
ACTION = re.compile(r"Investigating Officer|refer(?:s|red|ring)?\s+(?:this|the)\s+matter"
                    r"|disciplinary\s+(?:proceedings?|action|referral)|\breprimand\w*|\bsuspended\s+from\s+practice"
                    r"|\b(?:impose|imposes|imposed)\s+(?:a\s+)?sanctions?\b|\bdisqualif\w+", re.I)

FLAG_KEYS = ("ai_mention", "ai_citation", "own_rule", "other_body", "frcp_11", "mata", "action")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_date(s):
    """First date in s as YYYY-MM-DD, or None."""
    for m in DATE_RE.finditer(s or ""):
        try:
            if m.group(1):
                d = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
            elif m.group(4):
                d = dt.date(int(m.group(6)), MONTHS[m.group(4)[:3].lower()], int(m.group(5)))
            else:
                d = dt.date(int(m.group(7)), int(m.group(8)), int(m.group(9)))
            return d.isoformat()
        except (ValueError, KeyError):
            continue
    return None


def strip_tags(s):
    s = re.sub(r"(?is)<(script|style|nav|header|footer)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", htmlmod.unescape(s)).strip()


def main_text(page_html):
    """Visible text of the page's main content (main, else article, else body)."""
    for tag in ("main", "article", "body"):
        m = re.search(r"(?is)<%s\b[^>]*>(.*)</%s>" % (tag, tag), page_html)
        if m:
            return strip_tags(m.group(1))
    return strip_tags(page_html)


def parse_flra_listing(page_html):
    """Rows of one page of the FLRA's Authority-decisions list."""
    parts = re.split(r"(?i)<tr\b", page_html)
    chunks = parts[1:] if len(parts) > 2 else []
    if not chunks:  # fallback: each HTML-version link with the text since the previous one
        ms = list(FLRA_HREF.finditer(page_html))
        chunks = [page_html[(ms[i - 1].end() if i else 0):m.end()] for i, m in enumerate(ms)]
    out, seen = [], set()
    for ch in chunks:
        m = FLRA_HREF.search(ch)
        if not m or m.group(2) != m.group(3):
            continue
        key = (int(m.group(2)), int(m.group(4)))
        if key in seen:
            continue
        seen.add(key)
        text = strip_tags(ch)
        c = FLRA_CITE.search(text)
        url = m.group(1) if m.group(1).startswith("http") else FLRA_BASE + m.group(1)
        out.append({"forum": FORUM, "volume": key[0], "number": key[1],
                    "citation": "%d FLRA No. %d" % key,
                    "reporter_cite": ("%s FLRA %s" % (c.group(1), c.group(2))) if c else "",
                    "date": parse_date(text), "url": url})
    return out


def in_window(date):
    return bool(date) and START <= date <= END


def _excerpt(text, pos, width=350):
    a, b = max(0, pos - width), min(len(text), pos + width)
    return re.sub(r"\s+", " ", text[a:b])


def classify(text):
    """Flags for one decision text (frozen)."""
    text = text or ""
    r = {"chars": len(re.sub(r"\s+", " ", text)), "excerpts": {}}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    prob = [m.start() for m in CITE_PROBLEM.finditer(text)]
    r["ai_mention"] = bool(ai)
    pair = next(((a, p) for a in ai for p in prob if abs(a - p) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    for key, rx in (("own_rule", OWN_RULE), ("frcp_11", FRCP_11), ("mata", MATA), ("action", ACTION)):
        m = rx.search(text) if r["ai_citation"] else None
        r[key] = bool(m)
        if m:
            r["excerpts"][key] = _excerpt(text, m.start())
    near = None
    if r["ai_citation"]:
        for a in ai:
            lo = max(0, a - NEAR)
            mm = OTHER_BODY.search(text[lo:a + NEAR])
            if mm:
                near = lo + mm.start()
                break
    r["other_body"] = near is not None
    if near is not None:
        r["excerpts"]["other_body"] = _excerpt(text, near)
    return r


# --- coverage against the AI Hallucination Cases Database ---------------------------------
DB_FORUM = re.compile(r"\bFLRA\b|Federal Labor Relations", re.I)
DB_REVIEW = re.compile(r"Circuit|Cir\.|Court of Appeals|District|Supreme", re.I)


def db_rows(csv_text):
    out = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        if DB_FORUM.search(court) and not DB_REVIEW.search(court):
            out.append({"case_id": (row.get("case_id") or "").strip(), "date": parse_date(row.get("Date") or "")})
    return out


def match_db(found, dbrows, days=7):
    """Adds 'in_db' and 'db_case_id' to each decision with a date."""
    for r in found:
        r["in_db"], r["db_case_id"] = False, ""
        if not r.get("date"):
            continue
        d0 = dt.date.fromisoformat(r["date"])
        for x in dbrows:
            if x["date"] and abs((dt.date.fromisoformat(x["date"]) - d0).days) <= days:
                r["in_db"], r["db_case_id"] = True, x["case_id"]
                break
    return found


# --- grading (frozen) -----------------------------------------------------------------------
def _share(rows, key):
    n = len(rows)
    k = sum(1 for r in rows if r.get(key))
    return {"n": n, "k": k, "share": round(k / n, 3) if n else None}


def _min3(s, test):
    return "not testable" if s["n"] < 3 else ("held" if test(s["share"]) else "failed")


def grade(rows):
    readable = [r for r in rows if r.get("readable")]
    hits = [r for r in readable if r.get("ai_citation")]
    P = {}
    P["P1"] = {"text": "the FLRA frame holds at least 2 AI-citation decisions",
               "detail": {"n": len(hits)}, "verdict": "held" if len(hits) >= 2 else "failed"}
    s = _share(hits, "in_db")
    P["P2"] = {"text": "fewer than half of the AI-citation decisions are in the AI Hallucination Cases Database",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    s = _share(hits, "action")
    P["P3"] = {"text": "at most half of the AI-citation decisions name a sanction, referral, reprimand or disqualification",
               "detail": s, "verdict": _min3(s, lambda x: x <= 0.5)}
    s = _share(hits, "other_body")
    P["P4"] = {"text": "at least half of the AI-citation decisions cite another agency or adjudicator within 2,500 characters of an AI term",
               "detail": s, "verdict": _min3(s, lambda x: x >= 0.5)}
    early = [r for r in hits if r.get("date") and r["date"] < "2023-01-01"]
    P["P5"] = {"text": "method check: no AI-citation decision is dated before 2023-01-01",
               "detail": {"n_before": len(early), "ids": [r.get("citation") for r in early]},
               "verdict": "held" if not early else "failed"}
    s = _share(hits, "mata")
    P["P6"] = {"text": "Mata v. Avianca is cited in fewer than half of the AI-citation decisions",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    y23 = [r for r in readable if (r.get("date") or "").startswith("2023")]
    y26 = [r for r in readable if (r.get("date") or "").startswith("2026")]
    a23, a26, al = _share(y23, "ai_mention"), _share(y26, "ai_mention"), _share(readable, "ai_mention")
    if a23["n"] < 50 or a26["n"] < 50 or (al["share"] or 0) > 0.8:
        v7 = "not testable"
    else:
        v7 = "held" if a26["share"] > a23["share"] else "failed"
    P["P7"] = {"text": "a larger share of 2026 decisions than of 2023 decisions mention an AI term",
               "detail": {"2023": a23, "2026": a26, "all": al}, "verdict": v7}
    by_year = {}
    for r in readable:
        y = (r.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"readable": 0, "ai_mention": 0, "ai_citation": 0})
        b["readable"] += 1
        b["ai_mention"] += bool(r.get("ai_mention"))
        b["ai_citation"] += bool(r.get("ai_citation"))
    counts = {"in_frame": len(rows), "readable": len(readable),
              "ai_mention": sum(1 for r in readable if r.get("ai_mention")),
              "ai_citation": len(hits), "by_year": dict(sorted(by_year.items()))}
    return {"census_version": VERSION, "window": [START, END], "counts": counts,
            "ai_citation_decisions": [{k: r.get(k) for k in ("citation", "reporter_cite", "date", "url", "in_db",
                                                             "db_case_id") + FLAG_KEYS} for r in hits],
            "predictions": P}


def results_md(res, sources):
    L = ["# FLRA archive AI-citation census %s: results" % res["census_version"], "",
         "Frame: every FLRA Authority decision issued %s to %s, read from flra.gov. "
         "Coverage check against the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). "
         "Information about public decisions, not legal advice. Made with AI agents working in MV2's name." % tuple(res["window"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## AI-citation decisions", "", "| citation | date | in database | flags |", "|---|---|---|---|"]
    for r in res["ai_citation_decisions"]:
        L.append("| [%s](%s) | %s | %s | %s |" % (r["citation"], r["url"], r["date"], r["in_db"],
                                                ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(rows):
    cols = ["citation", "reporter_cite", "date", "url", "doc_status", "chars", "readable",
            "doc_sha256", "in_db", "db_case_id"] + list(FLAG_KEYS)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
    return buf.getvalue()
