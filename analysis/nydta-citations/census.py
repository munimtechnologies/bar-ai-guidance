#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""New York Division of Tax Appeals and Tax Appeals Tribunal fabricated-citation census 1.0.0
(pre-registered; see PLAN.md here).

Pure functions only: listing parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public determinations and
decisions of a state tax tribunal, not legal or tax advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import difflib
import hashlib
import html.parser
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
PAGES = (
    ("det", "https://www.dta.ny.gov/determinations/"),          # ALJ determinations
    ("detord", "https://www.dta.ny.gov/determinations/orders.htm"),  # ALJ orders
    ("dec", "https://www.dta.ny.gov/decisions/"),               # Tribunal decisions
    ("decord", "https://www.dta.ny.gov/decisions/orders.htm"),  # Tribunal orders
)
TRIBUNAL_PAGES = ("dec", "decord")
YEAR_MIN, YEAR_MAX = 2013, 2026  # a listed year outside this range is treated as unreadable
MIN_FRAME = 650                  # fewer documents in the frame: stop before any document is fetched
MAX_FRAME = 1400                 # more: stop before any document is fetched
READABLE_CHARS = 300
PROXIMITY = 2000


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- listing pages ---------------------------------------------------------------------------
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


MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
          "october", "november", "december")
COLS = ("name", "number", "date")
NUM_RX = re.compile(r"(?<!\d)(\d{6})(?!\d)")


def parse_numbers(raw):
    """Every six-digit DTA number in a Number cell, in order, de-duplicated."""
    out = []
    for n in NUM_RX.findall(raw or ""):
        if n not in out:
            out.append(n)
    return out


def parse_month(token):
    t = re.sub(r"[^a-z]", "", (token or "").lower())
    if len(t) < 3:
        return None
    for i, name in enumerate(MONTHS):
        if name.startswith(t[:3]):
            return i + 1
    close = difflib.get_close_matches(t, MONTHS, n=1, cutoff=0.75)
    return MONTHS.index(close[0]) + 1 if close else None


def parse_date(raw):
    """(year, month, day) from 'Month D, YYYY' and its typos; None for each part not readable.
    A year outside YEAR_MIN..YEAR_MAX (e.g. '2925') is None."""
    t = (raw or "").strip()
    m = re.match(r"\s*([A-Za-z]+)\.?\s*(\d{1,2}(?!\d))?\s*[,.]?\s*(\d{4})?", t)
    if not m:
        return None, None, None
    month = parse_month(m.group(1))
    day = int(m.group(2)) if m.group(2) else None
    year = int(m.group(3)) if m.group(3) else None
    if year is not None and not (YEAR_MIN <= year <= YEAR_MAX):
        year = None
    return year, month, day


def quote_url(u):
    return urllib.parse.quote(u, safe=":/?&=%#~()+,;@!$'*-._")


def _header_map(cells):
    """Column index for each field if this row is the header, else None."""
    texts = [c["text"].strip().lower() for c in cells]
    if not any(t.startswith("name") for t in texts) or not any(t.startswith("date") for t in texts):
        return None
    idx = {}
    for i, t in enumerate(texts):
        if t.startswith("name"):
            idx["name"] = i
        elif t.startswith("number") or t.startswith("dta") or t == "no.":
            idx["number"] = i
        elif t.startswith("date"):
            idx["date"] = i
    return idx


def parse_listing(body, page_url, page="det"):
    """(entries, info). Rows count only after the header row. Each entry: page, name (private),
    numbers, number, date_raw, year, month, day, links (absolute, quoted, de-duplicated)."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    p = _Table()
    p.feed(body)
    p.close()
    cmap, header_found, out = {f: i for i, f in enumerate(COLS)}, False, []
    for cells in p.rows:
        h = _header_map(cells)
        if h is not None:
            cmap.update(h)
            header_found = True
            continue
        if not header_found or len(cells) < 3 or all(c["th"] for c in cells):
            continue
        get = lambda f: cells[cmap[f]] if cmap[f] < len(cells) else {"text": "", "hrefs": []}
        name, number = get("name"), get("number")
        if not name["text"] and not number["text"]:
            continue
        links = []
        for h2 in name["hrefs"] + number["hrefs"]:
            if h2.lower().startswith(("mailto:", "javascript:", "#")):
                continue
            u = quote_url(urllib.parse.urljoin(page_url, h2))
            if u not in links:
                links.append(u)
        nums = parse_numbers(number["text"])
        y, mo, d = parse_date(get("date")["text"])
        out.append({"page": page, "name": name["text"], "numbers": nums, "number": nums[0] if nums else "",
                    "date_raw": get("date")["text"][:40], "year": y, "month": mo, "day": d, "links": links})
    info = {"url": page_url, "page": page, "table_rows": len(p.rows), "entries": len(out),
            "header_found": header_found,
            "no_number": sum(1 for e in out if not e["number"]),
            "no_year": sum(1 for e in out if not e["year"]),
            "no_month": sum(1 for e in out if not e["month"]),
            "no_link": sum(1 for e in out if not e["links"])}
    return out, info


def row_key(e):
    return "%s|%s|%s" % (e.get("page", ""), e.get("number", ""), e.get("date_raw", ""))


def row_id(e, n=0):
    key = row_key(e) + ("|%d" % n if n else "")
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()[:12]


def is_tribunal(e):
    return e.get("page") in TRIBUNAL_PAGES


# --- text classification (frozen; fabricated-citation and AI patterns as in MV2's OTA census) ---
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

HALLUC = re.compile(r"\bhallucinat\w*", re.I)
FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucination")


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one document text (frozen)."""
    text = normalize(raw_text)
    r = {"chars": len(text), "excerpts": {}}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    fake = [m.start() for m in FAKE_CITE.finditer(text)]
    r["ai_mention"] = bool(ai)
    r["fake_cite"] = bool(fake)
    pair = next(((a, q) for a in ai for q in fake if abs(a - q) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    h = HALLUC.search(text)
    r["hallucination"] = bool(h)
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if h:
        r["excerpts"]["hallucination"] = _excerpt(text, h.start())
    return r


# --- the AI Hallucination Cases Database -----------------------------------------------------
NY_TAX = re.compile(r"Division\s+of\s+Tax\s+Appeals|Tax\s+Appeals\s+Tribunal|Tax\s+Appeals\s+Trib\b|\bDTA\b"
                    r"|N\.?\s?Y\.?\s+(?:State\s+)?Tax|New\s+York\s+(?:State\s+)?Tax", re.I)
_STOP = {"and", "inc", "llc", "corp", "corporation", "company", "the", "dba", "trust", "group", "holdings",
         "estate", "matter", "petition", "petitions", "new", "york", "services", "enterprises", "partners",
         "limited", "international", "america", "american", "united", "states", "deceased", "individually",
         "officer", "responsible", "person"}


def db_check(csv_text):
    """New York tax-tribunal rows (court or case name matches; names kept private) and every row's
    joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        name = (row.get("Case Name") or "").strip()
        if NY_TAX.search(court) or NY_TAX.search(name):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": name})
        joined.append(re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v)))
    return {"ny_tax_rows": rows, "joined": joined}


def name_tokens(name):
    """Distinctive words of a petitioner name (4+ letters, not boilerplate)."""
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", name or "") if t.lower() not in _STOP]


def in_db(db, e):
    """True if any database row quotes one of the document's DTA numbers after 'DTA', or a New York
    tax-tribunal row's case name contains a distinctive word of the petitioner name."""
    if not db:
        return False
    for n in e.get("numbers") or []:
        rx = re.compile(r"\bDTA\s*(?:Nos?\.?|Numbers?|#)?\s*:?\s*(?:\d{6}\s*(?:,|and|&|/)?\s*)*%s(?!\d)" % n, re.I)
        if any(rx.search(j) for j in db["joined"]):
            return True
    for t in name_tokens(e.get("name")):
        trx = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        if any(trx.search(r["name"]) for r in db["ny_tax_rows"]):
            return True
    return False


# --- grading (frozen) ------------------------------------------------------------------------
def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    P = {}
    P["P1"] = {"text": "0 to 3 documents in the frame have a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if len(fake) <= 3 else "failed"}
    early = [d for d in fake if d.get("year") and d["year"] < 2025]
    unknown = [d for d in fake if not d.get("year")]
    P["P2"] = {"text": "no document dated before 2025 has a fabricated-citation phrase",
               "detail": {"n_before_2025": len(early), "n_year_unknown": len(unknown)},
               "verdict": "failed" if early else ("not testable" if unknown else "held")}
    k = sum(1 for d in readable if d.get("ai_citation"))
    P["P3"] = {"text": "at most one document has an AI term within 2,000 characters of a fabricated-citation phrase",
               "detail": {"n": k}, "verdict": "held" if k <= 1 else "failed"}
    k = sum(1 for d in readable if d.get("ai_mention"))
    P["P4"] = {"text": "fewer than 10 readable documents mention an AI term at all",
               "detail": {"n": k}, "verdict": "held" if k < 10 else "failed"}
    k = sum(1 for d in fake if is_tribunal(d))
    P["P5"] = {"text": "no Tax Appeals Tribunal decision or order has a fabricated-citation phrase",
               "detail": {"n": k}, "verdict": "held" if k == 0 else "failed"}
    ptext = ("the database has no New York tax-tribunal row, and no fabricated-citation document is in it "
             "(not blind: no such row on 11 Nov 2026)")
    if db is None:
        P["P6"] = {"text": ptext, "detail": None, "verdict": "not testable"}
    else:
        n_rows = len(db["ny_tax_rows"])
        listed = sorted({d["number"] for d in fake if d.get("in_db")})
        P["P6"] = {"text": ptext, "detail": {"ny_tax_rows": n_rows, "n": len(fake), "in_db": listed},
                   "verdict": "not testable" if not fake else ("held" if n_rows == 0 and not listed else "failed")}
    share = (len(readable) / len(docs)) if docs else 0.0
    P["P7"] = {"text": "method check: at least 98% of the documents in the frame are readable",
               "detail": {"readable": len(readable), "in_frame": len(docs), "share": round(share, 4)},
               "verdict": "held" if docs and share >= 0.98 else "failed"}
    nodate = sum(1 for d in docs if not d.get("year"))
    P["P8"] = {"text": "listing check (not blind: typos seen in summaries): at most 2% of documents in the frame "
                       "have no readable year",
               "detail": {"no_year": nodate, "in_frame": len(docs)},
               "verdict": "held" if docs and nodate <= 0.02 * len(docs) else "failed"}
    status, by_year, by_page = {}, {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
    for d in readable:
        y = str(d.get("year") or "????")
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0, "hallucination": 0})
        b["readable"] += 1
        for f in ("fake_cite", "ai_mention", "hallucination"):
            b[f] += bool(d.get(f))
        g = by_page.setdefault(d.get("page") or "?", {"readable": 0, "fake_cite": 0, "ai_mention": 0})
        g["readable"] += 1
        g["fake_cite"] += bool(d.get("fake_cite"))
        g["ai_mention"] += bool(d.get("ai_mention"))
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "ai_mention": sum(1 for d in readable if d.get("ai_mention")),
              "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "hallucination": sum(1 for d in readable if d.get("hallucination")),
              "fetch_status": dict(sorted(status.items())), "by_page": dict(sorted(by_page.items())),
              "by_year": dict(sorted(by_year.items()))}
    dbpub = None if db is None else {"ny_tax_rows": [{k: r[k] for k in ("case_id", "date", "court")}
                                                     for r in db["ny_tax_rows"]], "rows": len(db["joined"])}
    flagged = lambda d: d.get("ai_mention") or d.get("hallucination")
    return {"census_version": VERSION, "counts": counts, "listing": listing or {}, "database": dbpub,
            "fake_cite_documents": [public_row(d) for d in fake],
            "other_flagged_documents": [public_row(d) for d in readable if flagged(d) and not d.get("fake_cite")],
            "predictions": P}


ROW_COLS = ["row_id", "page", "number", "year", "month", "doc_status", "chars", "readable", "file_sha256",
            "in_db"] + list(FLAG_KEYS)


def public_row(d):
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# New York Division of Tax Appeals and Tax Appeals Tribunal fabricated-citation census %s: results"
         % res["census_version"], "",
         "Frame: every document listed on the four listing pages of www.dta.ny.gov (ALJ determinations, ALJ orders, "
         "Tribunal decisions, Tribunal orders) when the job ran. Information about public documents of a state tax "
         "tribunal, not legal or tax advice. Made with AI agents working in MV2's name.", "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Documents with a fabricated-citation phrase", "",
          "| row | page | DTA number | year | month | in database | flags |", "|---|---|---|---|---|---|---|"]
    for r in res["fake_cite_documents"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (r["row_id"], r["page"], r["number"], r["year"], r["month"],
                                                         r["in_db"], ", ".join(k for k in FLAG_KEYS if r.get(k))))
    L += ["", "## Other documents with an AI term or 'hallucinat...'", "",
          "| row | page | DTA number | year | flags |", "|---|---|---|---|---|"]
    for r in res["other_flagged_documents"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["row_id"], r["page"], r["number"], r["year"],
                                                ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("page") or "", x.get("year") or 0, x.get("month") or 0,
                                         x.get("number") or "", x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
