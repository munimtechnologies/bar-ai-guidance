#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""California Office of Tax Appeals fabricated-citation census 1.0.0 (pre-registered; see PLAN.md here).

Pure functions only: listing parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public opinions of a
state tax tribunal, not legal or tax advice.
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
PAGES = (
    ("fit", 2026, "https://ota.ca.gov/2026-franchise-income-tax-opinions/"),
    ("fit", 2025, "https://ota.ca.gov/2025-franchise-income-tax-opinions/"),
    ("fit", 2024, "https://ota.ca.gov/2024-franchise-income-tax-opinions/"),
    ("bt", 2026, "https://ota.ca.gov/2026-business-tax-opinions/"),
    ("bt", 2025, "https://ota.ca.gov/2025-business-tax-opinions/"),
    ("bt", 2024, "https://ota.ca.gov/2024-business-tax-opinions/"),
)
YEARS = (2024, 2026)
MIN_FRAME = 1300                # fewer opinions in the frame: stop before any opinion is fetched
MAX_FRAME = 2600                # more: stop before any opinion is fetched
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


CITE_RX = re.compile(r"\b(20\d\d)\s*[-=\u2013\u2014]\s*OTA\s*[-=\u2013\u2014]\s*(\d{1,4})\s*([A-Za-z]{0,4})\b")
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
          "october", "november", "december")
COLS = ("name", "month", "year", "cite", "decision_type", "issues")


def parse_cite(raw):
    """(normalized cite, year, number, suffix) or None. '2026=OTA=551' -> '2026-OTA-551'."""
    m = CITE_RX.search(raw or "")
    if not m:
        return None
    suffix = m.group(3).upper()
    return "%s-OTA-%s%s" % (m.group(1), m.group(2), suffix), int(m.group(1)), int(m.group(2)), suffix


def parse_month(raw):
    t = (raw or "").strip().lower()
    for i, name in enumerate(MONTHS):
        if t == name or (len(t) >= 3 and name.startswith(t.rstrip("."))):
            return i + 1
    return None


def quote_url(u):
    return urllib.parse.quote(u, safe=":/?&=%#~()+,;@!$'*-._")


def _header_map(cells):
    """Column index for each field if this row is the header, else None."""
    texts = [c["text"].strip().lower() for c in cells]
    if "cite" not in texts or "month" not in texts:
        return None
    idx = {}
    for i, t in enumerate(texts):
        if t.startswith("decision type") or t == "type":
            idx["decision_type"] = i
        elif t.startswith("decision"):
            idx["name"] = i
        elif t == "month":
            idx["month"] = i
        elif t == "year":
            idx["year"] = i
        elif t == "cite":
            idx["cite"] = i
        elif t.startswith("issue"):
            idx["issues"] = i
    return idx


def parse_listing(body, page_url, page="fit", page_year=0):
    """(entries, info). Each entry: page, page_year, name (private), month, year, cite, cite_year,
    cite_num, suffix, decision_type, issues, links (absolute, quoted, de-duplicated)."""
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
        if len(cells) < 5 or all(c["th"] for c in cells):
            continue
        get = lambda f: cells[cmap[f]] if cmap[f] < len(cells) else {"text": "", "hrefs": []}
        links = []
        for h2 in get("name")["hrefs"] + get("cite")["hrefs"]:
            u = quote_url(urllib.parse.urljoin(page_url, h2))
            if u not in links and not u.startswith(("mailto:", "javascript:")):
                links.append(u)
        c = parse_cite(get("cite")["text"])
        yr = re.search(r"\b(20\d\d)\b", get("year")["text"])
        out.append({"page": page, "page_year": page_year, "name": get("name")["text"],
                    "month_raw": get("month")["text"], "month": parse_month(get("month")["text"]),
                    "year": int(yr.group(1)) if yr else None,
                    "cite": c[0] if c else "", "cite_year": c[1] if c else None,
                    "cite_num": c[2] if c else None, "suffix": c[3] if c else "",
                    "decision_type": get("decision_type")["text"], "issues": get("issues")["text"][:300],
                    "links": links})
    info = {"url": page_url, "page": page, "page_year": page_year, "table_rows": len(p.rows),
            "entries": len(out), "header_found": header_found,
            "no_cite": sum(1 for e in out if not e["cite"]),
            "no_month": sum(1 for e in out if not e["month"]),
            "year_mismatch": sum(1 for e in out if e["cite_year"] and e["year"] and e["cite_year"] != e["year"]),
            "page_year_mismatch": sum(1 for e in out if (e["cite_year"] or e["year"]) != page_year)}
    return out, info


def opinion_year(e):
    return e.get("cite_year") or e.get("year")


def in_window(e):
    y = opinion_year(e)
    return bool(y) and YEARS[0] <= y <= YEARS[1]


def row_key(e):
    return "%s|%s|%s|%s" % (e.get("page", ""), e.get("cite", ""), e.get("month") or "", e.get("year") or "")


def row_id(e, n=0):
    key = row_key(e) + ("|%d" % n if n else "")
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()[:12]


def is_precedential(e):
    t = (e.get("decision_type") or "").lower()
    return "precedential" in t and "nonprecedential" not in t and "non-precedential" not in t


# --- text classification (frozen; fabricated-citation and AI patterns as in MV2's USPTO OED census) ---
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
NOLAND = re.compile(r"\bNoland\b")

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucination", "noland")


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one opinion text (frozen)."""
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
    r["noland"] = bool(NOLAND.search(text))
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
OTA_COURT = re.compile(r"Office\s+of\s+Tax\s+Appeals|\bOTA\b|Board\s+of\s+Equalization|\bBOE\b"
                       r"|California\s+Tax|Cal\.?\s+Tax", re.I)
_STOP = {"and", "inc", "llc", "corp", "corporation", "company", "subsidiaries", "affiliates", "the", "dba",
         "trust", "group", "holdings", "estate", "opinion", "pfr", "california", "services", "enterprises",
         "partners", "limited", "international", "america", "american", "united", "states"}


def db_check(csv_text):
    """OTA-court rows (with case names, kept private) and every row's joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        if OTA_COURT.search(court):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": (row.get("Case Name") or "").strip()})
        joined.append(re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v)))
    return {"ota_rows": rows, "joined": joined}


def name_tokens(name):
    """Distinctive words of a party name (4+ letters, not company boilerplate)."""
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", name or "") if t.lower() not in _STOP]


def in_db(db, e):
    """True if any database row quotes the opinion's cite (e.g. '2026-OTA-311'), or an OTA-court row's
    case name contains a distinctive word of the party name."""
    if not db or not e.get("cite_year"):
        return False
    rx = re.compile(r"(?<![\w-])%d\s*-\s*OTA\s*-\s*0*%d(?!\d)" % (e["cite_year"], e["cite_num"]), re.I)
    if any(rx.search(j) for j in db["joined"]):
        return True
    for t in name_tokens(e.get("name")):
        trx = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        if any(trx.search(r["name"]) for r in db["ota_rows"]):
            return True
    return False


# --- grading (frozen) ------------------------------------------------------------------------
def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    by = lambda rows, y: [d for d in rows if opinion_year(d) == y]
    P = {}
    hits = [d for d in by(fake, 2026) if is_precedential(d)]
    P["P1"] = {"text": "at least one 2026 opinion designated precedential or pending precedential has a fabricated-citation "
                       "phrase (not blind: press report of July 2026)",
               "detail": {"n": len(hits)}, "verdict": "held" if hits else "failed"}
    P["P2"] = {"text": "2 to 8 opinions in the frame have a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if 2 <= len(fake) <= 8 else "failed"}
    n24 = len(by(fake, 2024))
    P["P3"] = {"text": "no 2024 opinion has a fabricated-citation phrase",
               "detail": {"n_2024": n24}, "verdict": "held" if n24 == 0 else "failed"}
    n25, n26 = len(by(fake, 2025)), len(by(fake, 2026))
    P["P4"] = {"text": "at least as many 2026 opinions as 2025 opinions have a fabricated-citation phrase",
               "detail": {"n_2025": n25, "n_2026": n26},
               "verdict": "not testable" if not fake else ("held" if n26 >= n25 else "failed")}
    k = sum(1 for d in fake if d.get("ai_mention"))
    P["P5"] = {"text": "fewer than half of the fabricated-citation opinions mention an AI term",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if 2 * k < len(fake) else "failed")}
    k = sum(1 for d in fake if d.get("page") == "fit")
    P["P6"] = {"text": "at least half of the fabricated-citation opinions are franchise and income tax opinions",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if 2 * k >= len(fake) else "failed")}
    k = sum(1 for d in fake if d.get("noland"))
    P["P7"] = {"text": "at least one fabricated-citation opinion cites Noland v. Land of the Free (not blind for the July 2026 "
                       "opinion: the press report says it cites a 2025 Court of Appeal ruling)",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if k >= 1 else "failed")}
    if db is None:
        P["P8"] = {"text": "the database has no OTA-court row, and at least one fabricated-citation opinion is not in it "
                           "(not blind: no OTA row on 11 Nov 2026)", "detail": None, "verdict": "not testable"}
    else:
        missing = sorted({d["cite"] for d in fake if not d.get("in_db")})
        n_rows = len(db["ota_rows"])
        P["P8"] = {"text": "the database has no OTA-court row, and at least one fabricated-citation opinion is not in it "
                           "(not blind: no OTA row on 11 Nov 2026)",
                   "detail": {"ota_rows": n_rows, "n": len(fake), "missing": missing},
                   "verdict": "not testable" if not fake else ("held" if n_rows == 0 and missing else "failed")}
    share = (len(readable) / len(docs)) if docs else 0.0
    P["P9"] = {"text": "method check: at least 98% of the opinions in the frame are readable",
               "detail": {"readable": len(readable), "in_frame": len(docs), "share": round(share, 4)},
               "verdict": "held" if docs and share >= 0.98 else "failed"}
    status, by_year, by_type, by_page = {}, {}, {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
        t = d.get("decision_type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1
    for d in readable:
        y = str(opinion_year(d) or "????")
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0, "hallucination": 0})
        b["readable"] += 1
        for f in ("fake_cite", "ai_mention", "hallucination"):
            b[f] += bool(d.get(f))
        g = by_page.setdefault(d.get("page") or "?", {"readable": 0, "fake_cite": 0})
        g["readable"] += 1
        g["fake_cite"] += bool(d.get("fake_cite"))
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "ai_mention": sum(1 for d in readable if d.get("ai_mention")),
              "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "hallucination": sum(1 for d in readable if d.get("hallucination")),
              "noland": sum(1 for d in readable if d.get("noland")),
              "fetch_status": dict(sorted(status.items())), "by_type": dict(sorted(by_type.items())),
              "by_page": dict(sorted(by_page.items())), "by_year": dict(sorted(by_year.items()))}
    dbpub = None if db is None else {"ota_rows": [{k: r[k] for k in ("case_id", "date", "court")} for r in db["ota_rows"]],
                                     "rows": len(db["joined"])}
    flagged = lambda d: d.get("ai_mention") or d.get("hallucination") or d.get("noland")
    return {"census_version": VERSION, "years": list(YEARS), "counts": counts, "listing": listing or {},
            "database": dbpub,
            "fake_cite_opinions": [public_row(d) for d in fake],
            "other_flagged_opinions": [public_row(d) for d in readable if flagged(d) and not d.get("fake_cite")],
            "predictions": P}


ROW_COLS = ["row_id", "cite", "page", "month", "year", "decision_type", "issues", "doc_status", "chars", "readable",
            "pdf_sha256", "in_db"] + list(FLAG_KEYS)


def public_row(d):
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# California Office of Tax Appeals fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every opinion listed on the OTA's franchise and income tax and business tax opinion pages for %d to %d. "
         "Information about public opinions of a state tax tribunal, not legal or tax advice. Made with AI agents "
         "working in MV2's name." % tuple(res["years"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Opinions with a fabricated-citation phrase", "",
          "| row | cite | pages | month | year | type | in database | flags |", "|---|---|---|---|---|---|---|---|"]
    for r in res["fake_cite_opinions"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (r["row_id"], r["cite"], r["page"], r["month"], r["year"],
                                                               r["decision_type"], r["in_db"],
                                                               ", ".join(k for k in FLAG_KEYS if r.get(k))))
    L += ["", "## Other opinions with an AI term, 'hallucinat...' or a Noland citation", "",
          "| row | cite | year | flags |", "|---|---|---|---|"]
    for r in res["other_flagged_opinions"]:
        L.append("| %s | %s | %s | %s |" % (r["row_id"], r["cite"], r["year"], ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (opinion_year(x) or 0, x.get("cite_num") or 0, x.get("cite") or "",
                                         x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
