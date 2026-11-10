#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""U.S. Tax Court fabricated-citation census 1.0.0 (pre-registered; see PLAN.md next to this file).

Pure functions only: search URLs, result parsing, frame merging, text classification,
coverage matching against the AI Hallucination Cases Database, and grading. Fetching lives
in run_job.py. Standard library only. Information about public court documents, not legal
advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
START = "2023-01-01"          # first filing date in the frame
END = "2026-11-10"            # last filing date in the frame
API = "https://public-api-green.dawson.ustaxcourt.gov/public-api"
OPINION_TYPES = "MOP,OST,SOP,TCOP"
OPINION_CODES = frozenset(OPINION_TYPES.split(","))
CASE_URL = "https://dawson.ustaxcourt.gov/case-detail/%s"
MIN_FRAME = 20                # fewer documents in the frame: stop before any text is fetched
MAX_FRAME = 2000              # more documents in the frame: stop before any text is fetched
READABLE_CHARS = 300          # an order can be one short page
PROXIMITY = 2000              # characters between an AI term and a fabricated-citation phrase
SEARCH_CAP = 5000             # the court's search returns at most this many results

# Fixed list of keyword searches, each run against both order search and opinion search.
# Quoted strings are sent with their quotes (exact phrase); the rest are sent as typed.
QUERIES = (
    '"artificial intelligence"', "artificial intelligence", "ChatGPT", "generative",
    '"large language model"', "hallucinated", "hallucination", "hallucinations", "hallucinate",
    "nonexistent", "non-existent", "nonexistent cases", "nonexistent case", "nonexistent citations",
    "fictitious", "fictitious cases", "fictitious case", "fictitious citations", "fake", "fake cases",
    "fake citations", "fabricated", "fabricated citations", "fabricated cases", "fabricated quotations",
    "bogus", "Avianca",
)
# Not searched (checked 2026-11-10 on metadata only): "case does not exist", "cases do not exist" and
# "unable to locate case" each return hundreds to thousands of documents, because the court's search
# matches the words, not the phrase; opinion search for "case does not exist" returns most opinions.
AI_PHRASE_QUERY = '"artificial intelligence"'

# --- text classification (frozen) ---------------------------------------------------------
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?)\b"
    r"|(?-i:\(\s*[\"\u201c]?A[Il][\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\blarge language models?\b|\bLLMs?\b", re.I)
AI_PHRASE = re.compile(r"\bartificial intelligence\b", re.I)

_AUTH = r"(?:cases?|citations?|cites|authorit(?:y|ies)|quotations?|quotes|opinions?|decisions?|case\s+law|caselaw|precedents?)"
FAKE_CITE = re.compile(
    # an adjective of falsity, up to two words (not function words), then a kind of legal authority
    r"\b(?:fictitious|non-?existent|fabricated|fake|hallucinated|made-up|bogus|phantom|invented)\s+"
    r"(?:(?!(?:in|of|for|this|that|the|and|to|by|on|at|from|with)\b)\w+\s+){0,2}?" + _AUTH + r"\b"
    # "... cited (by petitioner) do not exist"
    r"|\b(?:cited|quoted|referenced)\s+(?:\w+\s+){0,3}?(?:do(?:es)?|did)\s+not\s+exist\b"
    # "the cases do not exist" (plural nouns only)
    r"|\b(?:cases|citations|authorities)\s+(?:(?:that|which)\s+)?(?:do|did)\s+not\s+exist\b"
    # "unable to locate the cases cited" ("find" is left out: "we find the cases cited inapposite")
    r"|\blocate\s+(?:(?:the|any|these|such|this|that)\s+)?" + _AUTH +
    r"\s+(?:\w+\s+){0,2}?(?:cited|relied|referenced|quoted)\b", re.I)

RULE_33 = re.compile(r"\bRule\s+33\s*\(\s*b\s*\)")
SEC_6673 = re.compile(r"\b6673\b")
MATA = re.compile(r"\bMata\s+v\.?\s+Avianca\b")
ACTION = re.compile(r"\bsanction(?:s|ed)?\b|\bRule\s+202\b|\bdisciplinary\b"
                    r"|\bpenalty\s+(?:of\s+\$[\d,]+\s+)?(?:under|pursuant\s+to)\s+(?:I\.?R\.?C\.?\s*)?(?:section|sec\.|\u00a7)\s*6673", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "ai_phrase", "rule_33", "sec_6673", "mata", "action")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def search_url(kind, keyword):
    """Search URL for kind 'order' or 'opinion'. Spaces are sent as %20, never '+',
    because '+' is an operator in the court's search syntax."""
    base = "%s/%s-search?keyword=%s&dateRange=allDates" % (API, kind, urllib.parse.quote(keyword, safe=""))
    if kind == "opinion":
        base += "&opinionTypes=" + OPINION_TYPES
    return base


def download_url(docket_number, docket_entry_id):
    return "%s/%s/%s/public-document-download-url" % (API, docket_number, docket_entry_id)


def parse_results(body):
    """Documents in one search response (JSON with a 'results' list)."""
    data = json.loads(body.decode("utf-8") if isinstance(body, bytes) else body)
    out = []
    for x in data.get("results") or []:
        if not x.get("docketEntryId") or not x.get("docketNumber"):
            continue
        out.append({
            "docket_entry_id": x["docketEntryId"],
            "docket_number": x["docketNumber"],
            "docket_suffixed": x.get("docketNumberWithSuffix") or x["docketNumber"],
            "caption": x.get("caseCaption") or "",
            "document_type": x.get("documentType") or "",
            "title": (x.get("documentTitle") or "")[:200],
            "event_code": x.get("eventCode") or "",
            "date": (x.get("filingDate") or "")[:10] or None,
            "judge": x.get("signedJudgeName") or x.get("judge") or "",
            "pages": x.get("numberOfPages"),
            "stricken": bool(x.get("isStricken")),
        })
    return out


def in_window(date):
    return bool(date) and START <= date <= END


def doc_kind(event_code):
    return "opinion" if event_code in OPINION_CODES else "order"


def merge(frame, kind, query, results):
    """Adds in-window results to frame (dict keyed by docket entry id). Returns the in-window count.
    One document filed in several consolidated dockets has one docket entry id and is kept once."""
    n = 0
    for r in results:
        if not in_window(r["date"]):
            continue
        n += 1
        d = frame.get(r["docket_entry_id"])
        if d is None:
            d = dict(r, dockets=[], queries=[], kind=doc_kind(r["event_code"]))
            frame[r["docket_entry_id"]] = d
        if r["docket_number"] not in d["dockets"]:
            d["dockets"].append(r["docket_number"])
        tag = "%s:%s" % (kind, query)
        if tag not in d["queries"]:
            d["queries"].append(tag)
    return n


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)  # words split across PDF lines


def _excerpt(text, pos, width=350):
    a, b = max(0, pos - width), min(len(text), pos + width)
    return text[a:b]


def classify(raw_text):
    """Flags for one document text (frozen)."""
    text = normalize(raw_text)
    r = {"chars": len(text), "excerpts": {}}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    fake = [m.start() for m in FAKE_CITE.finditer(text)]
    r["ai_mention"] = bool(ai)
    r["fake_cite"] = bool(fake)
    r["ai_phrase"] = bool(AI_PHRASE.search(text))
    pair = next(((a, p) for a in ai for p in fake if abs(a - p) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    for key, rx in (("rule_33", RULE_33), ("sec_6673", SEC_6673), ("mata", MATA), ("action", ACTION)):
        m = rx.search(text) if r["fake_cite"] else None
        r[key] = bool(m)
        if m:
            r["excerpts"][key] = _excerpt(text, m.start())
    return r


# --- coverage against the AI Hallucination Cases Database ---------------------------------
DB_COURT = re.compile(r"^\s*(?:U\.?\s?S\.?\s+|United\s+States\s+)?Tax\s+Court\s*$", re.I)
NAME_STOP = frozenset("""estate trust family company corporation corp petitioner petitioners deceased
    commissioner internal revenue service subsidiaries partners partnership holdings group the and
    successor interest inc llc ltd""".split())


def name_tokens(case_name):
    first = re.split(r"\s+v\.?\s+|\s+vs\.?\s+", case_name or "", maxsplit=1, flags=re.I)[0]
    return [w.lower() for w in re.findall(r"[A-Za-z]{4,}", first) if w.lower() not in NAME_STOP]


def db_rows(csv_text):
    """US Tax Court rows of the database (not state tax courts, not Canada)."""
    out = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        state = (row.get("State(s)") or "").strip()
        if DB_COURT.match(court) and "USA" in state:
            date = (row.get("Date") or "").strip()[:10]
            out.append({"case_id": (row.get("case_id") or "").strip(), "date": date or None,
                        "tokens": name_tokens(row.get("Case Name") or "")})
    return out


def _date(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def match_db(docs, dbrows, days=7):
    """Marks docs 'in_db' when a database row is dated within `days` and a party-name word of the
    row appears in the caption. Returns the database rows dated in the window, each with the
    docket entry ids it matched."""
    for d in docs:
        d["in_db"], d["db_case_id"] = False, ""
    in_win = []
    for x in dbrows:
        x0 = _date(x["date"])
        if x0 is None or not in_window(x["date"]):
            continue
        hit = []
        for d in docs:
            d0 = _date(d.get("date"))
            if d0 is None or abs((d0 - x0).days) > days:
                continue
            cap = (d.get("caption") or "").lower()
            if any(re.search(r"\b%s\b" % re.escape(t), cap) for t in x["tokens"]):
                hit.append(d)
        for d in hit:
            d["in_db"] = True
            d["db_case_id"] = d["db_case_id"] or x["case_id"]
        in_win.append({"case_id": x["case_id"], "date": x["date"],
                       "matched": [d["docket_entry_id"] for d in hit],
                       "matched_fake_cite": [d["docket_entry_id"] for d in hit if d.get("fake_cite")]})
    return in_win


# --- grading (frozen) -----------------------------------------------------------------------
def _share(rows, key):
    n = len(rows)
    k = sum(1 for r in rows if r.get(key))
    return {"n": n, "k": k, "share": round(k / n, 3) if n else None}


def _min3(s, test):
    return "not testable" if s["n"] < 3 else ("held" if test(s["share"]) else "failed")


def grade(docs, db_in_window=None, queries=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    for d in fake:
        d["is_order"] = d.get("kind") == "order"
    P = {}
    P["P1"] = {"text": "the frame holds at least 10 readable documents with a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if len(fake) >= 10 else "failed"}
    s = _share(fake, "in_db")
    v = _min3(s, lambda x: x < 0.5) if db_in_window is not None else "not testable"
    P["P2"] = {"text": "fewer than half of the fabricated-citation documents are in the AI Hallucination Cases Database",
               "detail": s, "verdict": v}
    s = _share(fake, "ai_mention")
    P["P3"] = {"text": "fewer than half of the fabricated-citation documents mention an AI term",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    s = _share(fake, "is_order")
    P["P4"] = {"text": "at least half of the fabricated-citation documents are orders, not opinions",
               "detail": s, "verdict": _min3(s, lambda x: x >= 0.5)}
    s = _share(fake, "rule_33")
    P["P5"] = {"text": "at least half of the fabricated-citation documents cite Tax Court Rule 33(b)",
               "detail": s, "verdict": _min3(s, lambda x: x >= 0.5)}
    s = _share(fake, "sec_6673")
    P["P6"] = {"text": "fewer than half of the fabricated-citation documents cite section 6673",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    if db_in_window is None or not db_in_window:
        P["P7"] = {"text": "every US Tax Court row of the database dated in the window matches a document in the frame",
                   "detail": {"n": 0 if db_in_window is not None else None}, "verdict": "not testable"}
    else:
        missed = [x["case_id"] for x in db_in_window if not x["matched"]]
        P["P7"] = {"text": "every US Tax Court row of the database dated in the window matches a document in the frame",
                   "detail": {"n": len(db_in_window), "missed_case_ids": missed},
                   "verdict": "held" if not missed else "failed"}
    phrase = [d for d in readable if d.get("ai_phrase")]
    for d in phrase:
        d["by_phrase_query"] = any(q.split(":", 1)[1] == AI_PHRASE_QUERY for q in d.get("queries", []))
    s = _share(phrase, "by_phrase_query")
    P["P8"] = {"text": "search check: at least 90% of readable frame documents whose text contains 'artificial intelligence' were returned by the exact-phrase search for it",
               "detail": s, "verdict": _min3(s, lambda x: x >= 0.9)}
    by_year = {}
    for d in readable:
        y = (d.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_citation": 0})
        b["readable"] += 1
        b["fake_cite"] += bool(d.get("fake_cite"))
        b["ai_citation"] += bool(d.get("ai_citation"))
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "fake_cite_orders": sum(1 for d in fake if d["is_order"]),
              "ai_mention": sum(1 for d in readable if d.get("ai_mention")),
              "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "by_year": dict(sorted(by_year.items()))}
    return {"census_version": VERSION, "window": [START, END], "counts": counts,
            "queries": queries or [], "db_rows_in_window": db_in_window,
            "fake_cite_documents": [public_row(d) for d in fake],
            "predictions": P}


ROW_COLS = ["docket_entry_id", "dockets", "date", "kind", "event_code", "document_type", "judge", "pages",
            "stricken", "link", "doc_status", "chars", "readable", "doc_sha256", "in_db", "db_case_id",
            "queries"] + list(FLAG_KEYS)


def public_row(d):
    """One document as published: docket numbers and court metadata, never the caption."""
    out = {c: d.get(c, "") for c in ROW_COLS}
    out["dockets"] = ";".join(d.get("dockets") or [d.get("docket_number", "")])
    out["queries"] = "|".join(d.get("queries") or [])
    out["link"] = CASE_URL % (d.get("docket_number") or "")
    return out


def results_md(res, sources):
    L = ["# U.S. Tax Court fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every order and opinion filed %s to %s that the court's own DAWSON search returns for a fixed "
         "list of keyword searches. Coverage check against the AI Hallucination Cases Database (Damien Charlotin, "
         "CC BY 4.0). Information about public court documents, not legal advice. Made with AI agents working in "
         "MV2's name." % tuple(res["window"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Searches", "", "| search | results | in window |", "|---|---|---|"]
    for q in res["queries"]:
        L.append("| %s `%s` | %s | %s |" % (q.get("kind"), q.get("query"), q.get("results"), q.get("in_window")))
    L += ["", "## Documents with a fabricated-citation phrase", "",
          "| docket | date | kind | in database | flags |", "|---|---|---|---|---|"]
    for r in res["fake_cite_documents"]:
        L.append("| [%s](%s) | %s | %s | %s | %s |" % (r["dockets"], r["link"], r["date"], r["kind"], r["in_db"],
                                                       ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("date") or "", x.get("docket_entry_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
