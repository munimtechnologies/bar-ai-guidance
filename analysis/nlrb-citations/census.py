#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""NLRB fabricated-citation census 1.0.0 (pre-registered; see PLAN.md).

Pure functions only: parsing the Board's public decisions listing (www.nlrb.gov), text
classification, the database check and grading. Fetching lives in run_job.py. Standard library
only. Information about public decisions of a federal labor board, not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import html.parser
import io
import json
import re

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
LISTING = "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?page=%d"
# apps.nlrb.gov/link/ is disallowed by its robots.txt, so the same NLRB document (same document id) is
# read from nlrbresearch.com's mirror, whose /pdfs/ path its robots.txt allows.
MIRROR = "https://nlrbresearch.com/pdfs/%s.pdf"
FRAME_START = "2024-01-01"      # listed decision date, inclusive
MIN_FRAME = 250                 # fewer decisions in the frame: stop before any decision is fetched
MAX_FRAME = 600                 # more: stop before any decision is fetched
MAX_NO_DOC = 10                 # more frame decisions without a document id: stop
READABLE_CHARS = 300
PROXIMITY = 2000
# The three decisions known before this census was frozen.
KNOWN = ("374-30", "375-31", "375-65")
BACKFLOW = "375-31"
CUTOFF = "2026-01-01"


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def listing_url(page):
    return LISTING % page


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip()


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def html_text(s):
    p = _Text()
    p.feed(s or "")
    p.close()
    return normalize(" ".join(p.parts))


# --- the listing (newest first, 20 rows a page) ----------------------------------------------------
ROW_SPLIT = re.compile(r"<tr[\s>]", re.I)
DATE_RX = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")
CITE_RX = re.compile(r"\b(\d{3})\s+NLRB\s+No\.\s*(\d+)", re.I)
DOC_RX = re.compile(r"document\.aspx/([0-9a-f]{16})", re.I)
NAME_RX = re.compile(r"document\.aspx/[0-9a-fA-F]{16}[^>]*>(.*?)</a>", re.I | re.S)
CASE_RX = re.compile(r"/case/(\d{2}-[A-Z]{2}-\d+)")


def parse_rows(page_html):
    """One dict per table row that carries an 'NNN NLRB No. N' citation."""
    if isinstance(page_html, bytes):
        page_html = page_html.decode("utf-8", "replace")
    rows = []
    for chunk in ROW_SPLIT.split(page_html)[1:]:
        chunk = chunk.split("</tr", 1)[0]
        cite = CITE_RX.search(chunk)
        if not cite:
            continue
        date = DATE_RX.search(chunk)
        doc = DOC_RX.search(chunk)
        name = NAME_RX.search(chunk)
        case = CASE_RX.search(chunk)
        vol, slip = int(cite.group(1)), int(cite.group(2))
        rows.append({
            "key": "%d-%d" % (vol, slip),
            "volume": vol,
            "slip": slip,
            "date": ("%s-%02d-%02d" % (date.group(3), int(date.group(1)), int(date.group(2)))) if date else None,
            "doc": doc.group(1).lower() if doc else None,
            "case": case.group(1) if case else None,
            "name": html_text(name.group(1))[:300] if name else "",
        })
    return rows


def in_window(r):
    return bool(r.get("date")) and r["date"] >= FRAME_START


def page_done(page_rows):
    """True when a page has no rows, or every dated row on it is before FRAME_START."""
    dates = [r["date"] for r in page_rows if r.get("date")]
    return not page_rows or (bool(dates) and max(dates) < FRAME_START)


def mirror_url(doc):
    if not doc or not re.fullmatch(r"[0-9a-f]{16}", doc):
        return ""
    return MIRROR % doc


# --- text classification (frozen) ------------------------------------------------------------------
# Series patterns: unchanged from MV2's WCAB, OTA, USPTO and PERB censuses.
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?|based|powered)\b"
    r"|(?-i:\(\s*[\"\u201c]?AI[\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\bChatSOC\b|\blarge language models?\b", re.I)

_AUTH = (r"(?:cases?|citations?|cites|authorit(?:y|ies)|quotations?|quotes|opinions?|decisions?|case\s+law|caselaw"
         r"|precedents?|portions?|passages?|pages?|parentheticals?)")
_SKIP = r"(?:in|of|for|this|that|the|and|to|by|on|at|from|with|its|his|her|their|a|an)"
FAKE_CITE = re.compile(
    r"\b(?:fictitious|non-?existent|fabricated|fake|hallucinated|made-up|bogus|phantom|invented)\s+"
    r"(?:(?!" + _SKIP + r"\b)\w+\s+){0,2}?" + _AUTH + r"\b"
    r"|\b(?:cited|cites?|quoted|referenced)\s+(?:\w+\s+){0,3}?(?:do(?:es)?|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\b(?:cases|citations|authorities|decisions|quotations|quotes|portions|passages|pages)\s+(?:(?:that|which)\s+)?"
    r"(?:do|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\b(?:case|citation|authority|decision|opinion|quotation|quote|portion|passage|page)\s+(?:that|which)\s+"
    r"(?:does|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\blocate\s+(?:(?:the|any|these|such|this|that)\s+)?" + _AUTH +
    r"\s+(?:\w+\s+){0,2}?(?:cited|relied|referenced|quoted)\b", re.I)
# NLRB addition (needed for Rivas Painting, 374 NLRB No. 30: "cites to cases that, as far as we can
# determine, do not exist"): an authority word followed, within 100 characters and before any
# '.', ';' or ':', by "do/does/did not (appear to) exist".
NOT_EXIST_NEAR = re.compile(
    r"\b(?:cases?|citations?|cites|authorit(?:y|ies)|decisions?|quotations?|precedents?|case\s+law)\b"
    r"[^.;:]{0,100}?\b(?:do|does|did)\s+not\s+(?:appear\s+to\s+)?exist\b", re.I)

HALLUC = re.compile(r"\bhallucinat\w*", re.I)
BACKFLOW_RX = re.compile(r"\bAmerican\s+Backflow\b", re.I)
REFERRAL = re.compile(r"\bInvestigating\s+Officer\b|\b102\.177\b", re.I)
GHOST = re.compile(r"\bghost\s+citations?\b", re.I)
PRO_SE = re.compile(r"\bpro\s+se\b", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucination", "backflow", "ghost")
RECORD_KEYS = ("fake_series", "fake_nlrb", "referral", "pro_se")


def variants(text):
    """The collapsed text twice: with line-break hyphens joined ('cita- tions' -> 'citations') and as is."""
    t = normalize(text)
    joined = re.sub(r"(\w)- (\w)", r"\1\2", t)
    return [joined, t] if joined != t else [t]


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one decision's text, frozen. A flag is set if it matches either text variant."""
    vs = variants(raw_text)
    r = {"chars": len(vs[-1]), "excerpts": {}}
    for k in FLAG_KEYS + RECORD_KEYS:
        r[k] = False
    for text in vs:
        ai = [m.start() for m in AI_TERMS.finditer(text)]
        series = [m.start() for m in FAKE_CITE.finditer(text)]
        extra = [m.start() for m in NOT_EXIST_NEAR.finditer(text)]
        fake = sorted(series + extra)
        pair = next(((a, q) for a in ai for q in fake if abs(a - q) <= PROXIMITY), None)
        found = {"ai_mention": ai, "fake_series": series, "fake_nlrb": extra, "fake_cite": fake,
                 "ai_citation": [pair[0]] if pair else []}
        for key, rx in (("hallucination", HALLUC), ("backflow", BACKFLOW_RX), ("ghost", GHOST),
                        ("referral", REFERRAL), ("pro_se", PRO_SE)):
            m = rx.search(text)
            found[key] = [m.start()] if m else []
        for key, pos in found.items():
            if pos:
                r[key] = True
                if key not in r["excerpts"] and key != "pro_se":
                    r["excerpts"][key] = _excerpt(text, pos[0])
    return r


# --- the AI Hallucination Cases Database -------------------------------------------------------------
NLRB_COURT = re.compile(r"\bN\.?\s?L\.?\s?R\.?\s?B\b|National\s+Labor\s+Relations\s+Board", re.I)
_STOP = {"american", "national", "international", "united", "company", "companies", "corporation", "services",
         "service", "group", "holdings", "enterprises", "management", "center", "centers", "health", "healthcare",
         "hospital", "medical", "systems", "industries", "operating", "partners", "limited", "incorporated",
         "union", "local", "workers", "association", "employees", "brotherhood", "teamsters", "district",
         "council", "construction", "transportation", "logistics", "restaurant", "restaurants", "stores", "store",
         "global", "solutions", "technologies", "university", "college", "school", "county", "state", "board",
         "national", "labor", "relations", "affiliated", "america", "north", "south", "east", "west", "western",
         "eastern", "northern", "southern", "pacific", "atlantic", "street", "first", "general", "products",
         "manufacturing", "foods", "markets", "building", "properties", "nursing", "rehabilitation", "living",
         "senior", "communications", "energy", "electric", "power", "security", "airlines", "airport", "station",
         "hotel", "hotels", "resort", "casino", "theatre", "theater", "media", "news", "contractors", "contracting",
         "company's", "successor", "subsidiary", "employer", "respondent", "charging", "party"}


def db_check(csv_text):
    """NLRB-court rows (names kept private) and every row's joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        j = re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v))
        court = (row.get("Court") or "").strip()
        if NLRB_COURT.search(court):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": (row.get("Case Name") or "").strip()})
        joined.append(j)
    return {"nlrb_rows": rows, "joined": joined}


def name_tokens(name):
    """Distinctive words (5+ letters, not boilerplate) of a listed case name."""
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]{4,}", name or "") if t.lower() not in _STOP]


def in_db(db, d):
    """True if any database row quotes the decision's 'VVV NLRB No. S' citation, or an NLRB-court row's
    case name contains a distinctive word of the listed case name."""
    if not db:
        return False
    vol, slip = d.get("volume"), d.get("slip")
    if vol and slip:
        rx = re.compile(r"\b%d\s+N\.?\s?L\.?\s?R\.?\s?B\.?\s+No\.?\s*%d\b" % (int(vol), int(slip)), re.I)
        if any(rx.search(j) for j in db["joined"]):
            return True
    for t in name_tokens(d.get("name")):
        trx = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        if any(trx.search(r["name"]) for r in db["nlrb_rows"]):
            return True
    return False


# --- grading (frozen) --------------------------------------------------------------------------------
def _keys(rows):
    return sorted({d["key"] for d in rows})


def grade(docs, db=None, listing=None):
    fake = [d for d in docs if d.get("fake_cite")]
    fake_keys = _keys(fake)
    readable = [d for d in docs if d.get("readable")]
    P = {}
    in_frame = [k for k in KNOWN if any(d["key"] == k for d in docs)]
    flagged = [k for k in KNOWN if k in fake_keys]
    P["P1"] = {"text": "recall check (not blind): Rivas Painting (374 NLRB No. 30), American Backflow (375 NLRB "
                       "No. 31) and Pepperjacks (375 NLRB No. 65) are in the frame and each has a fabricated-citation "
                       "phrase",
               "detail": {"in_frame": in_frame, "flagged": flagged},
               "verdict": "held" if len(flagged) == len(KNOWN) else "failed"}
    P["P2"] = {"text": "4 to 10 decisions in the frame have a fabricated-citation phrase (at least one beyond the "
                       "three known)",
               "detail": {"n": len(fake_keys), "keys": fake_keys},
               "verdict": "held" if 4 <= len(fake_keys) <= 10 else "failed"}
    early = _keys([d for d in fake if (d.get("date") or "") < CUTOFF])
    P["P3"] = {"text": "no decision dated before 1 January 2026 has a fabricated-citation phrase",
               "detail": {"early": early}, "verdict": "held" if not early else "failed"}
    ai_keys = _keys([d for d in fake if d.get("ai_mention")])
    P["P4"] = {"text": "fewer than half of the decisions with a fabricated-citation phrase mention an AI term",
               "detail": {"n": len(fake_keys), "k": len(ai_keys), "ai": ai_keys},
               "verdict": "not testable" if not fake_keys else ("held" if 2 * len(ai_keys) < len(fake_keys)
                                                                else "failed")}
    text5 = ("the database has at most one NLRB-court row, and at least two decisions with a fabricated-citation "
             "phrase are not in it (not blind: one NLRB row, American Backflow, on its live search on 13 Nov 2026)")
    if db is None:
        P["P5"] = {"text": text5, "detail": None, "verdict": "not testable"}
    else:
        listed = {d["key"] for d in fake if d.get("in_db")}
        missing = [k for k in fake_keys if k not in listed]
        n_rows = len(db["nlrb_rows"])
        P["P5"] = {"text": text5, "detail": {"nlrb_rows": n_rows, "decisions": len(fake_keys), "missing": missing},
                   "verdict": "not testable" if not fake_keys else ("held" if n_rows <= 1 and len(missing) >= 2
                                                                    else "failed")}
    bf = [k for k in _keys([d for d in fake if d.get("backflow")]) if k != BACKFLOW]
    P["P6"] = {"text": "at least two decisions with a fabricated-citation phrase, other than American Backflow "
                       "itself, mention American Backflow (not blind for one: Pepperjacks does)",
               "detail": {"k": len(bf), "decisions": bf}, "verdict": "held" if len(bf) >= 2 else "failed"}
    share = (len(readable) / len(docs)) if docs else 0.0
    P["P7"] = {"text": "method check: at least 97% of decisions in the frame have a readable text from the mirror",
               "detail": {"readable": len(readable), "in_frame": len(docs), "share": round(share, 4)},
               "verdict": "held" if docs and share >= 0.97 else "failed"}
    ref = _keys([d for d in fake if d.get("referral")])
    P["P8"] = {"text": "at most one decision with a fabricated-citation phrase mentions the Investigating Officer "
                       "or Sec. 102.177",
               "detail": {"k": len(ref), "decisions": ref},
               "verdict": "not testable" if not fake_keys else ("held" if len(ref) <= 1 else "failed")}
    by_year = {}
    for d in docs:
        y = (d.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"decisions": 0, "readable": 0, "fake_cite": 0, "ai_mention": 0,
                                   "hallucination": 0})
        b["decisions"] += 1
        for f in ("readable", "fake_cite", "ai_mention", "hallucination"):
            b[f] += bool(d.get(f))
    status = {}
    for d in docs:
        s = d.get("pdf_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake_keys),
              "fake_series_only_patterns": len(_keys([d for d in docs if d.get("fake_series")])),
              "fake_nlrb_clause_only": len(_keys([d for d in docs if d.get("fake_nlrb") and not d.get("fake_series")]))}
    for f in ("ai_mention", "ai_citation", "hallucination", "backflow", "ghost", "referral"):
        counts[f] = sum(1 for d in docs if d.get(f))
    counts["pro_se_among_fake"] = sum(1 for d in fake if d.get("pro_se"))
    counts.update({"fetch_status": dict(sorted(status.items())), "by_year": dict(sorted(by_year.items()))})
    dbpub = None if db is None else {"nlrb_rows": [{k: r[k] for k in ("case_id", "date", "court")}
                                                   for r in db["nlrb_rows"]], "rows": len(db["joined"])}
    other = lambda d: any(d.get(k) for k in ("ai_mention", "hallucination", "backflow", "ghost")) and not d.get("fake_cite")
    return {"census_version": VERSION, "frame_start": FRAME_START, "counts": counts, "listing": listing or {},
            "database": dbpub,
            "fake_cite_decisions": [public_row(d) for d in fake],
            "other_flagged_decisions": [public_row(d) for d in docs if other(d)],
            "predictions": P}


ROW_COLS = ["key", "volume", "slip", "date", "case", "doc", "pdf_status", "pages", "chars", "readable", "pdf_sha256",
            "in_db", "known"] + list(FLAG_KEYS) + list(RECORD_KEYS)


def public_row(d):
    """One public row: citation, date, case number, document id and flags; no names or texts."""
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# NLRB fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every Board decision on the NLRB's public decisions listing dated %s or later. "
         "Information about public decisions of a federal labor board, not legal advice. "
         "Made with AI agents working in MV2's name." % res["frame_start"], "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Decisions with a fabricated-citation phrase", "",
          "| citation | date | case | in database | flags |", "|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s NLRB No. %s | %s | %s | %s | %s |" % (
            r["volume"], r["slip"], r["date"], r["case"], r["in_db"],
            ", ".join(k for k in FLAG_KEYS + RECORD_KEYS if r.get(k))))
    L += ["", "## Other decisions with an AI term, 'hallucinat...', 'ghost citation' or American Backflow", "",
          "| citation | date | flags |", "|---|---|---|"]
    for r in res["other_flagged_decisions"]:
        L.append("| %s NLRB No. %s | %s | %s |" % (r["volume"], r["slip"], r["date"],
                                                   ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("date") or "", x.get("volume") or 0, x.get("slip") or 0)):
        w.writerow(public_row(d))
    return buf.getvalue()
