#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""U.S. Employees' Compensation Appeals Board (ECAB) fabricated-citation census 1.0.0 (pre-registered; see PLAN.md).

Pure functions only: index and month-page parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public decisions of a federal
workers' compensation appeals board, not legal advice.
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
BASE = "https://www.dol.gov"
INDEX_URL = BASE + "/agencies/ecab/decisions"
YEARS = (2024, 2026)
MIN_MONTHS = 30                 # fewer month pages for 2024-2026 on the index: stop before any decision is fetched
MIN_FRAME = 1500                # fewer documents in the frame: stop before any decision is fetched
MAX_FRAME = 3600                # more: stop before any decision is fetched
MAX_NO_DATE = 40
READABLE_CHARS = 300
PROXIMITY = 2000
NEAR = 300

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
          "oct": 10, "nov": 11, "dec": 12}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- HTML ----------------------------------------------------------------------------------------
class _Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            h = (dict(attrs).get("href") or "").strip()
            if h:
                self.hrefs.append(h)


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


MONTH_LINK_RX = re.compile(r"/agencies/ecab/decisions/(\d{4})/([A-Za-z]{3,9})/?$")


def parse_index(body, page_url=INDEX_URL):
    """Month pages listed on the index: [{"year", "month", "label", "url"}] in page order, no repeats."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    p = _Links()
    p.feed(body)
    p.close()
    out, seen = [], set()
    for h in p.hrefs:
        u = urllib.parse.urljoin(page_url, h).split("#", 1)[0]
        m = MONTH_LINK_RX.search(urllib.parse.urlparse(u).path)
        if not m:
            continue
        mon = MONTHS.get(m.group(2)[:3].lower())
        if not mon or u in seen:
            continue
        seen.add(u)
        out.append({"year": int(m.group(1)), "month": mon, "label": m.group(2), "url": u})
    return out


def months_in_window(months):
    return [m for m in months if YEARS[0] <= m["year"] <= YEARS[1]]


DATE_RX = re.compile(r"^([A-Za-z]{3,9})\.?\s+(\d{1,2}),\s*(\d{4})$")
NUM_DATE_RX = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
DOCKET_RX = re.compile(r"^(\d{2})-(\d{3,4})")


def parse_date(raw):
    """'June 11, 2025' or '6/11/2025' -> '2025-06-11'; anything else -> None."""
    s = (raw or "").strip()
    m = DATE_RX.match(s)
    try:
        if m:
            mon = MONTHS.get(m.group(1)[:3].lower())
            return dt.date(int(m.group(3)), mon, int(m.group(2))).isoformat() if mon else None
        m = NUM_DATE_RX.match(s)
        if m:
            return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return None
    return None


def stem_info(url):
    """(file stem, docket like '23-0067' or None, kind: order | reissue | decision)."""
    stem = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    stem = re.sub(r"\.pdf$", "", stem, flags=re.I)
    m = DOCKET_RX.match(stem)
    docket = "%s-%s" % (m.group(1), m.group(2).zfill(4)) if m else None
    up = stem.upper()
    if "REISSUE" in up:
        kind = "reissue"
    elif re.search(r"_O\d*$", up):
        kind = "order"
    else:
        kind = "decision"
    return stem, docket, kind


def parse_month(body, month, page_url=None):
    """(entries, info) for one month page. Each entry: year, month, url, stem, docket, kind, date, date_raw,
    parties (private: initials and employing agency as listed)."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    page_url = page_url or month["url"]
    p = _Table()
    p.feed(body)
    p.close()
    out, headers = [], 0
    for cells in p.rows:
        texts = [c["text"].strip().lower() for c in cells]
        if any("docket" in t for t in texts) and any("date" in t for t in texts) and not any(
                c["hrefs"] for c in cells):
            headers += 1
            continue
        pdfs = []
        for c in cells:
            for h in c["hrefs"]:
                u = urllib.parse.urljoin(page_url, h)
                if "/ecab/decisions/" in u.lower() and u.lower().endswith(".pdf") and u not in pdfs:
                    pdfs.append(u)
        if not pdfs:
            continue
        date_raw, date = "", None
        for c in cells:
            d = parse_date(c["text"])
            if d:
                date_raw, date = c["text"], d
                break
        stem, docket, kind = stem_info(pdfs[0])
        parties = cells[-1]["text"] if len(cells) >= 3 else ""
        out.append({"year": month["year"], "month": month["month"], "url": pdfs[0], "stem": stem,
                    "docket": docket, "kind": kind, "date": date, "date_raw": date_raw[:30],
                    "parties": parties[:200], "pdf_links": len(pdfs)})
    info = {"url": page_url, "year": month["year"], "month": month["month"], "table_rows": len(p.rows),
            "entries": len(out), "headers": headers,
            "no_date": sum(1 for e in out if not e["date"]),
            "no_docket": sum(1 for e in out if not e["docket"]),
            "date_month_mismatch": sum(1 for e in out if e["date"] and (int(e["date"][:4]), int(e["date"][5:7]))
                                       != (month["year"], month["month"])),
            "kinds": {k: sum(1 for e in out if e["kind"] == k) for k in ("decision", "order", "reissue")}}
    return out, info


def row_id(e):
    return hashlib.sha256(e["url"].lower().encode("utf-8")).hexdigest()[:12]


def doc_year(e):
    return e.get("year")


# --- text classification (frozen; the patterns of MV2's WCAB census, plus three ECAB flags) -------
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

# New for ECAB: "unable to locate/find/identify (the) ... case(s)/citation(s)/decision(s)/authority/precedent".
NOT_LOCATED = re.compile(
    r"\b(?:unable\s+to|could\s+not|cannot|can\s+not)\s+(?:locate|find|identify|verify)\s+"
    r"(?:(?:the|any|these|such|this|that|a|an)\s+)?(?:\w+\s+){0,2}?"
    r"(?:cases?|citations?|decisions?|authorit(?:y|ies)|precedents?|case\s+law)\b", re.I)
HALLUC = re.compile(r"\bhallucinat\w*", re.I)
# Citation words only (not "opinion", "decision", "case" or "page", which medical evidence uses constantly).
CITE_WORD = re.compile(r"\b(?:citations?|cites|cited|citing|case\s+law|caselaw|authorit(?:y|ies)|precedents?"
                       r"|quotations?)\b", re.I)
PRO_SE = re.compile(r"\bAppellant,?\s+pro\s+se\b", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucinated_cite", "not_located")
EXTRA_KEYS = ("hallucination", "pro_se")


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
    hall = [m.start() for m in HALLUC.finditer(text)]
    auth = [m.start() for m in CITE_WORD.finditer(text)]
    hc = next((h for h in hall for a in auth if abs(h - a) <= NEAR), None)
    r["hallucination"] = bool(hall)
    r["hallucinated_cite"] = hc is not None
    nl = NOT_LOCATED.search(text)
    r["not_located"] = bool(nl)
    r["pro_se"] = bool(PRO_SE.search(text))
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if hc is not None:
        r["excerpts"]["hallucinated_cite"] = _excerpt(text, hc)
    if nl:
        r["excerpts"]["not_located"] = _excerpt(text, nl.start())
    return r


# --- the AI Hallucination Cases Database -----------------------------------------------------
ECAB_RX = re.compile(r"Employees['\u2019]?\s+Compensation\s+Appeals\s+Board|\bECAB\b", re.I)


def db_check(csv_text):
    """Rows whose court is ECAB, and the joined text of every row that mentions ECAB anywhere."""
    court_rows, mention = [], []
    total = 0
    for row in csv.DictReader(io.StringIO(csv_text)):
        total += 1
        court = (row.get("Court") or "").strip()
        joined = re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v))
        if ECAB_RX.search(court):
            court_rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "")[:10],
                               "court": court[:80]})
        if ECAB_RX.search(joined):
            mention.append(joined)
    return {"ecab_rows": court_rows, "mention": mention, "rows": total}


def in_db(db, e):
    """True if a database row that mentions ECAB quotes the decision's docket number."""
    if not db or not e.get("docket"):
        return False
    a, b = e["docket"].split("-")
    rx = re.compile(r"(?<![\d-])%s-0*%s(?!\d)" % (a, str(int(b))))
    return any(rx.search(j) for j in db["mention"])


# --- grading (frozen) ------------------------------------------------------------------------
def _v(ok):
    return "held" if ok else "failed"


def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    ai = [d for d in readable if d.get("ai_mention")]
    P = {}
    if db is None:
        P["P1"] = {"text": "the database has no ECAB-court row and lists none of the decisions with a fabricated-"
                           "citation phrase (not blind: no ECAB row on 15 Nov 2026)",
                   "detail": None, "verdict": "not testable"}
    else:
        listed = sum(1 for d in fake if d.get("in_db"))
        P["P1"] = {"text": "the database has no ECAB-court row and lists none of the decisions with a fabricated-"
                           "citation phrase (not blind: no ECAB row on 15 Nov 2026)",
                   "detail": {"ecab_court_rows": len(db["ecab_rows"]), "mention_rows": len(db["mention"]),
                              "fake_cite_listed": listed},
                   "verdict": _v(len(db["ecab_rows"]) == 0 and listed == 0)}
    P["P2"] = {"text": "at least one decision in the frame has a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": _v(len(fake) >= 1)}
    P["P3"] = {"text": "at most five decisions in the frame have a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": _v(len(fake) <= 5)}
    n24 = sum(1 for d in fake if doc_year(d) == 2024)
    P["P4"] = {"text": "no 2024 decision has a fabricated-citation phrase",
               "detail": {"n_2024": n24}, "verdict": _v(n24 == 0)}
    P["P5"] = {"text": "fewer than ten decisions in the frame mention an AI term",
               "detail": {"n": len(ai)}, "verdict": _v(len(ai) < 10)}
    dec = [d for d in readable if d.get("kind") != "order"]
    ps = sum(1 for d in dec if d.get("pro_se"))
    P["P6"] = {"text": "at least half of the readable decisions (orders excluded) record the appellant as pro se",
               "detail": {"decisions": len(dec), "pro_se": ps},
               "verdict": "not testable" if not dec else _v(2 * ps >= len(dec))}
    k = sum(1 for d in fake if d.get("pro_se"))
    P["P7"] = {"text": "every decision with a fabricated-citation phrase records the appellant as pro se",
               "detail": {"n": len(fake), "pro_se": k},
               "verdict": "not testable" if not fake else _v(k == len(fake))}
    share = (len(readable) / len(docs)) if docs else 0.0
    P["P8"] = {"text": "method check: at least 98% of the documents in the frame are readable",
               "detail": {"readable": len(readable), "in_frame": len(docs), "share": round(share, 4)},
               "verdict": _v(bool(docs) and share >= 0.98)}
    status, by_year = {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
    for d in readable:
        y = str(doc_year(d) or "????")
        b = by_year.setdefault(y, {"readable": 0, "orders": 0})
        b["readable"] += 1
        b["orders"] += d.get("kind") == "order"
        for f in FLAG_KEYS + EXTRA_KEYS:
            b[f] = b.get(f, 0) + bool(d.get(f))
    counts = {"in_frame": len(docs), "readable": len(readable)}
    for f in FLAG_KEYS + EXTRA_KEYS:
        counts[f] = sum(1 for d in readable if d.get(f))
    counts.update({"fetch_status": dict(sorted(status.items())), "by_year": dict(sorted(by_year.items()))})
    dbpub = None if db is None else {"ecab_rows": db["ecab_rows"], "mention_rows": len(db["mention"]),
                                     "rows": db["rows"]}
    other = [public_row(d) for d in readable if any(d.get(k) for k in FLAG_KEYS) and not d.get("fake_cite")]
    return {"census_version": VERSION, "years": list(YEARS), "counts": counts, "listing": listing or {},
            "database": dbpub, "fake_cite_decisions": [public_row(d) for d in fake],
            "other_flagged_decisions": other, "predictions": P}


ROW_COLS = ["row_id", "year", "month", "date", "docket", "kind", "doc_status", "chars", "readable", "pdf_sha256",
            "in_db"] + list(FLAG_KEYS) + list(EXTRA_KEYS)


def public_row(d):
    """One public row: docket numbers (the Board names appellants by initials only); parties never."""
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# ECAB fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every decision and order on the U.S. Employees' Compensation Appeals Board's month pages for "
         "%d to %d. Information about public decisions of a federal workers' compensation appeals board, not "
         "legal advice. Made with AI agents working in MV2's name." % tuple(res["years"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Documents with a fabricated-citation phrase", "",
          "| row | date | docket | kind | in database | flags |", "|---|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (r["row_id"], r["date"], r["docket"], r["kind"], r["in_db"],
                                                     ", ".join(k for k in FLAG_KEYS + EXTRA_KEYS if r.get(k))))
    L += ["", "## Other flagged documents (AI term, 'hallucinat...' near a citation word, or 'unable to locate')",
          "", "| row | date | docket | kind | flags |", "|---|---|---|---|---|"]
    for r in res["other_flagged_decisions"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["row_id"], r["date"], r["docket"], r["kind"],
                                                ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("year") or 0, x.get("month") or 0, x.get("date") or "",
                                         x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
