#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""California Workers' Compensation Appeals Board fabricated-citation census 1.0.0 (pre-registered; see PLAN.md).

Pure functions only: listing parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public decisions of a
state workers' compensation tribunal, not legal advice.
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
LISTING_URL = "https://www.dir.ca.gov/wcab/wcab-Decisions.htm"
YEARS = (2024, 2026)
MIN_FRAME = 2600                # fewer decisions in the frame: stop before any decision is fetched
MAX_FRAME = 3800                # more: stop before any decision is fetched
READABLE_CHARS = 300
PROXIMITY = 2000
# The six documents read by hand before this census was frozen (folder year, ADJ number).
KNOWN = (("2025", "ADJ17550375"), ("2025", "ADJ17889413"), ("2026", "ADJ17889413"),
         ("2025", "ADJ12865802"), ("2025", "ADJ16902178"), ("2026", "ADJ16902178"))


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- the listing page --------------------------------------------------------------------------
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


DATE_RX = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
FOLDER_RX = re.compile(r"/Panel-Decisions-(\d{4})/", re.I)
ADJ_RX = re.compile(r"ADJ\d{6,9}", re.I)


def parse_date(raw):
    """'6/26/2026' -> '2026-06-26'; anything else -> None."""
    m = DATE_RX.match((raw or "").strip())
    if not m:
        return None
    try:
        return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return None


def quote_url(u):
    return urllib.parse.quote(u, safe=":/?&=%#~()+,;@!$'*-._")


def parse_listing(body, page_url=LISTING_URL):
    """(entries, info). Each entry: date (ISO or None), date_raw, url (absolute, quoted), folder_year,
    adj (ADJ numbers in the file name, in order), name (applicant as listed; private), pdf_links."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    p = _Table()
    p.feed(body)
    p.close()
    out, headers = [], 0
    for cells in p.rows:
        if all(c["th"] for c in cells):
            texts = [c["text"].strip().lower() for c in cells]
            if "date" in texts and "panel decision" in texts:
                headers += 1
            continue
        if len(cells) < 2:
            continue
        pdfs = []
        for c in cells:
            for h in c["hrefs"]:
                u = quote_url(urllib.parse.urljoin(page_url, h))
                if u.lower().endswith(".pdf") and u not in pdfs:
                    pdfs.append(u)
        url = pdfs[0] if pdfs else ""
        fm = FOLDER_RX.search(url)
        fname = urllib.parse.unquote(url.rsplit("/", 1)[-1]) if url else ""
        adj = []
        for a in ADJ_RX.findall(fname):
            if a.upper() not in adj:
                adj.append(a.upper())
        name = re.split(r",?\s*Applicants?\b", cells[1]["text"], maxsplit=1)[0].strip(" ,")
        out.append({"date": parse_date(cells[0]["text"]), "date_raw": cells[0]["text"][:20], "url": url,
                    "folder_year": int(fm.group(1)) if fm else None, "adj": adj, "name": name,
                    "pdf_links": len(pdfs)})
    info = {"url": page_url, "table_rows": len(p.rows), "entries": len(out), "headers": headers,
            "no_date": sum(1 for e in out if not e["date"]),
            "no_link": sum(1 for e in out if not e["url"]),
            "no_folder_year": sum(1 for e in out if e["url"] and not e["folder_year"]),
            "no_adj": sum(1 for e in out if e["url"] and not e["adj"]),
            "date_folder_mismatch": sum(1 for e in out if e["date"] and e["folder_year"]
                                        and int(e["date"][:4]) != e["folder_year"])}
    return out, info


def doc_year(e):
    if e.get("folder_year"):
        return e["folder_year"]
    return int(e["date"][:4]) if e.get("date") else None


def in_window(e):
    y = doc_year(e)
    return bool(y) and YEARS[0] <= y <= YEARS[1]


def row_key(e):
    return "%s|%s|%s" % (doc_year(e) or "", "+".join(e.get("adj") or []), e.get("date") or "")


def row_id(e, n=0):
    key = row_key(e) + ("|%d" % n if n else "")
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()[:12]


def is_known(e):
    y = str(doc_year(e) or "")
    return any((y, a) in KNOWN for a in e.get("adj") or [])


def case_key(e):
    """One case per first ADJ number (a decision can list several)."""
    a = e.get("adj") or []
    return a[0] if a else "row:" + (e.get("row_id") or "")


# --- text classification (frozen; the patterns of MV2's OTA census, plus ChatSOC and three WCAB flags) ----
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

HALLUC = re.compile(r"\bhallucinat\w*", re.I)
NOLAND = re.compile(r"\bNoland\b")
SEDANO = re.compile(r"\bSedano\b")
LC5813 = re.compile(r"\b5813\b")
NIT = re.compile(r"\bnotice\s+of\s+intent(?:ion)?\s+to\s+(?:impose\s+|issue\s+|order\s+)?sanctions?\b", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucination", "noland", "sedano")
EXTRA_KEYS = ("lc5813", "nit")


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
    h = HALLUC.search(text)
    r["hallucination"] = bool(h)
    r["noland"] = bool(NOLAND.search(text))
    s = SEDANO.search(text)
    r["sedano"] = bool(s)
    r["lc5813"] = bool(LC5813.search(text))
    r["nit"] = bool(NIT.search(text))
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if h:
        r["excerpts"]["hallucination"] = _excerpt(text, h.start())
    if s:
        r["excerpts"]["sedano"] = _excerpt(text, s.start())
    return r


# --- the AI Hallucination Cases Database -----------------------------------------------------
WCAB_COURT = re.compile(r"Workers['\u2019]?\s*Comp(?:ensation|\.)?\s+Appeals\s+Board|\bWCAB\b", re.I)
_STOP = {"and", "inc", "llc", "corp", "corporation", "company", "the", "dba", "estate", "deceased",
         "applicant", "applicants", "california", "services", "insurance"}


def db_check(csv_text):
    """WCAB-court rows (with case names, kept private) and every row's joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        if WCAB_COURT.search(court):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": (row.get("Case Name") or "").strip()})
        joined.append(re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v)))
    return {"wcab_rows": rows, "joined": joined}


def name_tokens(name):
    """Distinctive words of an applicant's name (4+ letters, not boilerplate)."""
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", name or "") if t.lower() not in _STOP]


def in_db(db, e):
    """True if any database row quotes one of the decision's ADJ numbers, or a WCAB-court row's case name
    contains a distinctive word of the applicant's name."""
    if not db:
        return False
    for a in e.get("adj") or []:
        rx = re.compile(r"(?<![A-Za-z0-9])%s(?!\d)" % re.escape(a), re.I)
        if any(rx.search(j) for j in db["joined"]):
            return True
    for t in name_tokens(e.get("name")):
        trx = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        if any(trx.search(r["name"]) for r in db["wcab_rows"]):
            return True
    return False


# --- grading (frozen) ------------------------------------------------------------------------
def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    by = lambda rows, y: [d for d in rows if doc_year(d) == y]
    P = {}
    known = [d for d in docs if d.get("known")]
    kf = sum(1 for d in known if d.get("readable") and d.get("fake_cite"))
    P["P1"] = {"text": "recall check (not blind): every one of the six hand-checked decisions is in the frame and "
                       "has a fabricated-citation phrase",
               "detail": {"known_in_frame": len(known), "flagged": kf},
               "verdict": "held" if len(known) >= 6 and kf == len(known) else "failed"}
    P["P2"] = {"text": "10 to 40 decisions in the frame have a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if 10 <= len(fake) <= 40 else "failed"}
    n24 = len(by(fake, 2024))
    P["P3"] = {"text": "at most one 2024 decision has a fabricated-citation phrase",
               "detail": {"n_2024": n24}, "verdict": "held" if n24 <= 1 else "failed"}
    n25, n26 = len(by(fake, 2025)), len(by(fake, 2026))
    P["P4"] = {"text": "more 2026 decisions than 2025 decisions have a fabricated-citation phrase",
               "detail": {"n_2025": n25, "n_2026": n26},
               "verdict": "not testable" if not fake else ("held" if n26 > n25 else "failed")}
    k = sum(1 for d in fake if d.get("ai_mention"))
    P["P5"] = {"text": "fewer than half of the fabricated-citation decisions mention an AI term",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if 2 * k < len(fake) else "failed")}
    k = sum(1 for d in fake if d.get("lc5813"))
    P["P6"] = {"text": "at least three quarters of the fabricated-citation decisions cite Labor Code section 5813 "
                       "(the WCAB's sanctions statute)",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if 4 * k >= 3 * len(fake) else "failed")}
    fake_cases = sorted({case_key(d) for d in fake})
    if db is None:
        P["P7"] = {"text": "the database has no WCAB-court row, and at least three cases with a fabricated-citation "
                           "decision are not in it (not blind: no WCAB row on 11 Nov 2026)",
                   "detail": None, "verdict": "not testable"}
    else:
        missing = sorted({case_key(d) for d in fake if not d.get("in_db")})
        n_rows = len(db["wcab_rows"])
        P["P7"] = {"text": "the database has no WCAB-court row, and at least three cases with a fabricated-citation "
                           "decision are not in it (not blind: no WCAB row on 11 Nov 2026)",
                   "detail": {"wcab_rows": n_rows, "cases": len(fake_cases), "missing": len(missing)},
                   "verdict": "not testable" if not fake else ("held" if n_rows == 0 and len(missing) >= 3
                                                               else "failed")}
    k = sum(1 for d in fake if d.get("sedano") and not d.get("known"))
    P["P8"] = {"text": "at least two fabricated-citation decisions other than the six hand-checked ones mention Sedano "
                       "(the WCAB's published 2025 sanctions decision)",
               "detail": {"k": k}, "verdict": "held" if k >= 2 else "failed"}
    share = (len(readable) / len(docs)) if docs else 0.0
    P["P9"] = {"text": "method check: at least 98% of the decisions in the frame are readable",
               "detail": {"readable": len(readable), "in_frame": len(docs), "share": round(share, 4)},
               "verdict": "held" if docs and share >= 0.98 else "failed"}
    status, by_year = {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
    for d in readable:
        y = str(doc_year(d) or "????")
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0, "hallucination": 0,
                                   "lc5813": 0, "nit": 0})
        b["readable"] += 1
        for f in ("fake_cite", "ai_mention", "hallucination", "lc5813", "nit"):
            b[f] += bool(d.get(f))
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "fake_cite_cases": len(fake_cases)}
    for f in ("ai_mention", "ai_citation", "hallucination", "noland", "sedano", "lc5813", "nit"):
        counts[f] = sum(1 for d in readable if d.get(f))
    counts.update({"fetch_status": dict(sorted(status.items())), "by_year": dict(sorted(by_year.items()))})
    dbpub = None if db is None else {"wcab_rows": [{k: r[k] for k in ("case_id", "date", "court")}
                                                   for r in db["wcab_rows"]], "rows": len(db["joined"])}
    flagged = lambda d: any(d.get(k) for k in ("ai_mention", "hallucination", "noland", "sedano"))
    return {"census_version": VERSION, "years": list(YEARS), "counts": counts, "listing": listing or {},
            "database": dbpub,
            "fake_cite_decisions": [public_row(d) for d in fake],
            "other_flagged_decisions": [public_row(d) for d in readable if flagged(d) and not d.get("fake_cite")],
            "predictions": P}


ROW_COLS = ["row_id", "folder_year", "date", "adj", "doc_status", "chars", "readable", "pdf_sha256", "in_db",
            "known"] + list(FLAG_KEYS) + list(EXTRA_KEYS)


def public_row(d):
    """One public row. ADJ numbers only for flagged decisions; applicant names and file names never."""
    r = {c: d.get(c, "") for c in ROW_COLS}
    r["adj"] = "+".join(d.get("adj") or []) if any(d.get(k) for k in FLAG_KEYS) else ""
    return r


def results_md(res, sources):
    L = ["# California WCAB fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every panel decision listed on the WCAB's panel-decision page in its %d to %d folders. "
         "Information about public decisions of a state workers' compensation tribunal, not legal advice. "
         "Made with AI agents working in MV2's name." % tuple(res["years"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Decisions with a fabricated-citation phrase", "",
          "| row | folder | date | ADJ | in database | hand-checked | flags |", "|---|---|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["row_id"], r["folder_year"], r["date"], r["adj"], r["in_db"], r["known"],
            ", ".join(k for k in FLAG_KEYS + EXTRA_KEYS if r.get(k))))
    L += ["", "## Other decisions with an AI term, 'hallucinat...', Noland or Sedano", "",
          "| row | folder | date | ADJ | flags |", "|---|---|---|---|---|"]
    for r in res["other_flagged_decisions"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["row_id"], r["folder_year"], r["date"], r["adj"],
                                                ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (doc_year(x) or 0, x.get("date") or "", x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
