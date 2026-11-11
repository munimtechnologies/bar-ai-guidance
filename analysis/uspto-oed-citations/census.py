#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""USPTO OED discipline-archive fabricated-citation census 1.0.0 (pre-registered; see PLAN.md here).

Pure functions only: listing parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public decisions of a
federal agency, not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import html.parser
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
PAGE_URL = "https://foiadocuments.uspto.gov/oed/"
WINDOW = ("2023-01-01", "2026-11-10")
MIN_FRAME = 100                 # fewer decisions in the window: stop before any decision is fetched
MAX_FRAME = 300                 # more: stop before any decision is fetched
READABLE_CHARS = 300
PROXIMITY = 2000
MITCHELL = "D2026-16"           # public reprimand of 27 July 2026 (known before freezing)
MATOS = "D2025-13"              # public reprimand of 6 March 2025 (known before freezing)


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- listing page ----------------------------------------------------------------------------
class _Table(html.parser.HTMLParser):
    """Collects every table row as a list of cells: {"text": str, "hrefs": [str], "th": bool}."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self._row, self._cell, self._skip = [], None, None, 0

    def _close_cell(self):
        if self._cell is not None:
            self._cell["text"] = re.sub(r"\s+", " ", "".join(self._cell["text"])).strip()
            if self._row is None:
                self._row = []
            self._row.append(self._cell)
            self._cell = None

    def _close_row(self):
        self._close_cell()
        if self._row:
            self.rows.append(self._row)
        self._row = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "tr":
            self._close_row()
            self._row = []
        elif tag in ("td", "th"):
            self._close_cell()
            self._cell = {"text": [], "hrefs": [], "th": tag == "th"}
        elif tag == "a" and self._cell is not None:
            href = (dict(attrs).get("href") or "").strip()
            if href:
                self._cell["hrefs"].append(href)
        elif tag == "br" and self._cell is not None:
            self._cell["text"].append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in ("td", "th"):
            self._close_cell()
        elif tag in ("tr", "table"):
            self._close_row()

    def handle_data(self, data):
        if self._cell is not None and not self._skip:
            self._cell["text"].append(data)

    def close(self):
        super().close()
        self._close_row()


DATE_RX = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b")
PROC_NEW = re.compile(r"\bD20(?:2[2-9])-\d+\b")
COLS = ("proceeding", "decision_text", "respondent", "decision_type", "date")
_HEAD = {"proceeding": "proceeding", "related": "decision_text", "respondent": "respondent",
         "type": "decision_type", "date": "date"}


def parse_date(raw):
    m = DATE_RX.search(raw or "")
    if not m:
        return None
    try:
        if m.group(3):
            d = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        else:
            d = dt.date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
    except ValueError:
        return None
    return d.isoformat()


def quote_url(u):
    return urllib.parse.quote(u, safe=":/?&=%#~()+,;@!$'*-._")


def _header_map(cells):
    """Column index for each field if this row is the header, else None."""
    texts = [c["text"].lower() for c in cells]
    if not any("proceeding" in t for t in texts) or not any("date" in t for t in texts):
        return None
    if any(parse_date(c["text"]) for c in cells):
        return None
    idx = {}
    for i, t in enumerate(texts):
        for key, field in _HEAD.items():
            if key in t and field not in idx:
                idx[field] = i
                break
    return idx


def parse_listing(body, page_url=PAGE_URL):
    """(entries, info). Each entry: proceeding, decision_text, respondent (private), decision_type,
    date (ISO or None), links (absolute, quoted, de-duplicated; proceeding cell first)."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    p = _Table()
    p.feed(body)
    p.close()
    cmap, header_found, out = {f: i for i, f in enumerate(COLS)}, False, []
    for cells in p.rows:
        h = _header_map(cells)
        if h is not None and len(h) >= 3:
            cmap.update(h)
            header_found = True
            continue
        if len(cells) < 5 or all(c["th"] for c in cells):
            continue
        get = lambda f: cells[cmap[f]] if cmap[f] < len(cells) else {"text": "", "hrefs": []}
        links = []
        for f in ("proceeding", "decision_text"):
            for h2 in get(f)["hrefs"]:
                u = quote_url(urllib.parse.urljoin(page_url, h2))
                if u not in links and not u.startswith(("mailto:", "javascript:")):
                    links.append(u)
        out.append({"proceeding": get("proceeding")["text"], "decision_text": get("decision_text")["text"],
                    "respondent": get("respondent")["text"], "decision_type": get("decision_type")["text"],
                    "date_raw": get("date")["text"], "date": parse_date(get("date")["text"]), "links": links})
    info = {"table_rows": len(p.rows), "entries": len(out), "header_found": header_found,
            "bad_date": sum(1 for e in out if not e["date"]),
            "bad_date_new": sum(1 for e in out if not e["date"] and PROC_NEW.search(e["proceeding"]))}
    return out, info


def in_window(e):
    return bool(e.get("date")) and WINDOW[0] <= e["date"] <= WINDOW[1]


def row_id(e):
    key = "%s|%s|%s" % (e.get("proceeding", ""), e.get("date", ""), e.get("decision_text", ""))
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()[:12]


def has_proc(e, number):
    return re.search(r"(?<![\w-])" + re.escape(number) + r"(?![\w-])", e.get("proceeding") or "") is not None


# --- text classification (frozen) -------------------------------------------------------------
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?|based|powered)\b"
    r"|(?-i:\(\s*[\"\u201c]?AI[\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\blarge language models?\b", re.I)

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

GUIDANCE = re.compile(r"\b89\s+(?:Fed\.?\s*Reg\.?|FR)\s+25,?6(?:09|1\d)\b"
                      r"|\bGuidance\s+on\s+(?:the\s+)?Use\s+of\s+Artificial[- ]Intelligence[- ]Based\s+Tools\b", re.I)
R1118 = re.compile(r"\b11\.18\b")
R11101 = re.compile(r"\b11\.101\b")
R11804 = re.compile(r"\b11\.804\b")

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "guidance", "r11_18", "r11_101", "r11_804")


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one decision text (frozen)."""
    text = normalize(raw_text)
    r = {"chars": len(text), "excerpts": {}}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    fake = [m.start() for m in FAKE_CITE.finditer(text)]
    r["ai_mention"] = bool(ai)
    r["fake_cite"] = bool(fake)
    pair = next(((a, q) for a in ai for q in fake if abs(a - q) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    g = GUIDANCE.search(text)
    r["guidance"] = bool(g)
    r["r11_18"] = bool(R1118.search(text))
    r["r11_101"] = bool(R11101.search(text))
    r["r11_804"] = bool(R11804.search(text))
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if g:
        r["excerpts"]["guidance"] = _excerpt(text, g.start())
    return r


# --- the AI Hallucination Cases Database -----------------------------------------------------
USPTO_NAME = re.compile(r"\bUSPTO\b|Patent\s+and\s+Trademark\s+Office|Office\s+of\s+Enrollment|\bOED\b"
                        r"|Trademark\s+Trial|Patent\s+Trial|\bPTAB\b|\bTTAB\b", re.I)


def db_check(csv_text):
    """USPTO-court rows (with case names, kept private) and every row's joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        if USPTO_NAME.search(court):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": (row.get("Case Name") or "").strip()})
        joined.append(re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v)))
    return {"uspto_rows": rows, "joined": joined}


_NOT_NAME = ("esq", "jr", "sr", "ii", "iii", "iv")


def surname(respondent):
    """The respondent's surname: the last word before a comma ('Last, First'), else the last word."""
    s = respondent or ""
    part = s.split(",")[0] if "," in s else s
    toks = [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]+", part) if t.lower().strip(".") not in _NOT_NAME]
    return toks[-1] if toks and len(toks[-1]) >= 2 else ""


def in_db(db, e):
    """True if a USPTO-court row's case name contains the respondent's surname, or any row quotes
    the proceeding number."""
    if not db:
        return False
    sn = surname(e.get("respondent"))
    if sn:
        rx = re.compile(r"\b" + re.escape(sn) + r"\b", re.I)
        if any(rx.search(r["name"]) for r in db["uspto_rows"]):
            return True
    for num in re.findall(r"\bD\d{4}-\d+\b", e.get("proceeding") or ""):
        rx = re.compile(r"(?<![\w-])" + re.escape(num) + r"(?![\w-])")
        if any(rx.search(j) for j in db["joined"]):
            return True
    return False


# --- grading (frozen) ------------------------------------------------------------------------
def _named(docs, number, need):
    hits = [d for d in docs if has_proc(d, number)]
    readable = [d for d in hits if d.get("readable")]
    if not readable:
        return "not testable", {"rows": len(hits), "readable": 0}
    ok = any(all(d.get(k) for k in need) for d in readable)
    return ("held" if ok else "failed"), {"rows": len(hits), "readable": len(readable)}


def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    fake_procs = sorted({d["proceeding"] for d in fake})
    ai_procs = sorted({d["proceeding"] for d in readable if d.get("ai_mention")})
    P = {}
    v, det = _named(docs, MITCHELL, ("fake_cite", "ai_mention"))
    P["P1"] = {"text": "D2026-16 is readable and has both a fabricated-citation phrase and an AI term (pattern check, not blind)",
               "detail": det, "verdict": v}
    v, det = _named(docs, MATOS, ("fake_cite",))
    P["P2"] = {"text": "D2025-13 is readable and has a fabricated-citation phrase (pattern check, not blind)",
               "detail": det, "verdict": v}
    P["P3"] = {"text": "2 to 4 proceedings in the frame have a readable decision with a fabricated-citation phrase",
               "detail": {"n": len(fake_procs)}, "verdict": "held" if 2 <= len(fake_procs) <= 4 else "failed"}
    P["P4"] = {"text": "fewer than 5 proceedings in the frame have a readable decision that mentions an AI term",
               "detail": {"n": len(ai_procs)}, "verdict": "held" if len(ai_procs) < 5 else "failed"}
    k = sum(1 for d in fake if d.get("guidance"))
    P["P5"] = {"text": "at least one fabricated-citation decision cites the USPTO's April 2024 AI guidance",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if k >= 1 else "failed")}
    k = sum(1 for d in fake if d.get("r11_101"))
    P["P6"] = {"text": "every fabricated-citation decision cites the competence rule, 37 C.F.R. 11.101 (not blind for D2026-16)",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if k == len(fake) else "failed")}
    k = sum(1 for d in fake if d.get("r11_18"))
    P["P7"] = {"text": "at least half of the fabricated-citation decisions cite 37 C.F.R. 11.18 (signature and certification)",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if 2 * k >= len(fake) else "failed")}
    if db is None:
        P["P8"] = {"text": "the database has exactly one USPTO row, and it matches a readable decision in the frame (not blind)",
                   "detail": None, "verdict": "not testable"}
        P["P9"] = {"text": "at least one fabricated-citation proceeding in the frame is not in the database (not blind for D2025-13)",
                   "detail": None, "verdict": "not testable"}
    else:
        n_rows = len(db["uspto_rows"])
        matched = [d["proceeding"] for d in readable if d.get("in_db")]
        P["P8"] = {"text": "the database has exactly one USPTO row, and it matches a readable decision in the frame (not blind)",
                   "detail": {"uspto_rows": n_rows, "matched_proceedings": sorted(set(matched))},
                   "verdict": "held" if n_rows == 1 and matched else "failed"}
        missing = sorted({d["proceeding"] for d in fake if not d.get("in_db")})
        P["P9"] = {"text": "at least one fabricated-citation proceeding in the frame is not in the database (not blind for D2025-13)",
                   "detail": {"n": len(fake_procs), "missing": missing},
                   "verdict": "not testable" if not fake else ("held" if missing else "failed")}
    status, by_year, by_type = {}, {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
        t = d.get("decision_type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1
    for d in readable:
        y = (d.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0})
        b["readable"] += 1
        b["fake_cite"] += bool(d.get("fake_cite"))
        b["ai_mention"] += bool(d.get("ai_mention"))
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "fake_cite_proceedings": len(fake_procs), "ai_mention": sum(1 for d in readable if d.get("ai_mention")),
              "ai_mention_proceedings": len(ai_procs), "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "guidance": sum(1 for d in readable if d.get("guidance")),
              "fetch_status": dict(sorted(status.items())), "by_type": dict(sorted(by_type.items())),
              "by_year": dict(sorted(by_year.items()))}
    dbpub = None if db is None else {"uspto_rows": [{k: r[k] for k in ("case_id", "date", "court")} for r in db["uspto_rows"]],
                                     "rows": len(db["joined"])}
    return {"census_version": VERSION, "window": list(WINDOW), "counts": counts, "listing": listing or {},
            "database": dbpub,
            "fake_cite_decisions": [public_row(d) for d in fake],
            "ai_mention_decisions": [public_row(d) for d in readable if d.get("ai_mention")],
            "predictions": P}


ROW_COLS = ["row_id", "proceeding", "decision_text", "decision_type", "date", "doc_status", "chars", "readable",
            "pdf_sha256", "in_db"] + list(FLAG_KEYS)


def public_row(d):
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# USPTO OED discipline-archive fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every decision in the USPTO's OED FOIA reading room dated %s to %s. Information about public "
         "decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name."
         % tuple(res["window"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Decisions with a fabricated-citation phrase", "",
          "| row | proceeding | decision | type | date | in database | flags |", "|---|---|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (r["row_id"], r["proceeding"], r["decision_text"],
                                                         r["decision_type"], r["date"], r["in_db"],
                                                         ", ".join(k for k in FLAG_KEYS if r.get(k))))
    L += ["", "## Decisions that mention an AI term", "", "| row | proceeding | date | flags |", "|---|---|---|---|"]
    for r in res["ai_mention_decisions"]:
        L.append("| %s | %s | %s | %s |" % (r["row_id"], r["proceeding"], r["date"],
                                           ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("date") or "", x.get("proceeding") or "", x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
