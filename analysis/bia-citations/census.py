#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""BIA / A.G. precedent fabricated-citation census 1.0.0 (pre-registered; see PLAN.md next to this file).

Pure functions only: listing-page parsing, text classification, the database check and grading.
Fetching lives in run_job.py. Standard library only. Information about public decisions of a
federal agency, not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import html.parser
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
VOLUMES = (28, 29, 30)                       # Administrative Decisions under Immigration and Nationality Laws
PAGE_URL = "https://www.justice.gov/eoir/volume-%d"
MIN_FRAME = 250                             # fewer decisions listed: stop before any decision is fetched
MAX_FRAME = 400                             # more decisions listed: stop before any decision is fetched
ID_MIN, ID_MAX = 3900, 4500                 # plausible Interim Decision numbers for volumes 28-30
CITE_WINDOW = 600                           # an entry's own citation sits at most this far before its ID
READABLE_CHARS = 300
HEAD_CHARS = 4000
PROXIMITY = 2000
SETHI = (30, 112)                           # Matter of Sethi, 30 I&N Dec. 112 (BIA 2026), Interim Decision 4254


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- listing pages ---------------------------------------------------------------------------
class _Flat(html.parser.HTMLParser):
    """Flattens a page to one whitespace-collapsed string and records every link's span in it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.length, self.links, self._open = [], 0, [], []
        self._skip = 0

    def _add(self, s):
        s = re.sub(r"\s+", " ", s)
        if not s:
            return
        if s.startswith(" ") and (not self.parts or self.parts[-1].endswith(" ")):
            s = s[1:]
        if s:
            self.parts.append(s)
            self.length += len(s)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "a":
            self._open.append({"href": dict(attrs).get("href") or "", "start": self.length})
        elif tag in ("p", "div", "br", "hr", "li", "h1", "h2", "h3", "h4", "tr", "td"):
            self._add(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "a" and self._open:
            a = self._open.pop()
            a["end"] = self.length
            self.links.append(a)
        elif tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "tr", "td"):
            self._add(" ")

    def handle_data(self, data):
        if not self._skip:
            self._add(data)

    def text(self):
        return "".join(self.parts)


CITE = re.compile(r"\b(\d{2})\s*I\s*&\s*N\s+Dec\.?\s+(\d{1,4})\s*\(([^()]{1,20}?)\s*((?:19|20)\d{2})\s*\)")
ID_RX = re.compile(r"\bID\s*#?\s*(\d{4})\b")


def issuer_of(raw):
    s = re.sub(r"[\s.]", "", raw or "").upper()
    return {"BIA": "BIA", "AG": "AG", "AAO": "AAO", "DIR": "DIR"}.get(s, s[:12] or "unknown")


def parse_listing(body, volume, page_url):
    """Entries of one volume page: [{id, volume, page, issuer, year, cite, links:[abs urls]}].
    Entries are found by their 'ID nnnn' marker; the entry's citation is the last citation of this
    volume within CITE_WINDOW characters before it; its links are the non-empty links touching
    the marker. Duplicate IDs keep the first."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    p = _Flat()
    p.feed(body)
    p.close()
    text = p.text()
    links = [l for l in p.links if text[l["start"]:l.get("end", l["start"])].strip()]  # empty-text links dropped
    cites = [m for m in CITE.finditer(text) if int(m.group(1)) == volume]
    out, seen = [], set()
    for m in ID_RX.finditer(text):
        n = int(m.group(1))
        if n in seen or not (ID_MIN <= n <= ID_MAX):
            continue
        seen.add(n)
        c = None
        for cm in cites:
            if cm.start() < m.start() and m.start() - cm.end() <= CITE_WINDOW:
                c = cm
            elif cm.start() >= m.start():
                break
        lo, hi = m.start() - 5, m.end() + 12
        hrefs = []
        for l in links:
            if l["start"] < hi and l["end"] > lo and l["href"]:
                u = urllib.parse.urljoin(page_url, l["href"].strip())
                if u not in hrefs:
                    hrefs.append(u)
        out.append({"id": n, "volume": volume,
                    "page": int(c.group(2)) if c else None,
                    "issuer": issuer_of(c.group(3)) if c else "unknown",
                    "year": int(c.group(4)) if c else None,
                    "cite": "%d I&N Dec. %d" % (volume, int(c.group(2))) if c else "",
                    "links": hrefs})
    return out


def id_gaps(entries):
    ids = sorted(e["id"] for e in entries)
    if not ids:
        return []
    have = set(ids)
    return [i for i in range(ids[0], ids[-1] + 1) if i not in have]


# --- text classification (frozen) ---------------------------------------------------------
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?)\b"
    r"|(?-i:\(\s*[\"\u201c]?AI[\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\blarge language models?\b", re.I)

_AUTH = r"(?:cases?|citations?|cites|authorit(?:y|ies)|quotations?|quotes|opinions?|decisions?|case\s+law|caselaw|precedents?)"
_SKIP = r"(?:in|of|for|this|that|the|and|to|by|on|at|from|with|its|his|her|their|a|an)"
FAKE_CITE = re.compile(
    r"\b(?:fictitious|non-?existent|fabricated|fake|hallucinated|made-up|bogus|phantom|invented)\s+"
    r"(?:(?!" + _SKIP + r"\b)\w+\s+){0,2}?" + _AUTH + r"\b"
    r"|\b(?:cited|cites?|quoted|referenced)\s+(?:\w+\s+){0,3}?(?:do(?:es)?|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\b(?:cases|citations|authorities|decisions)\s+(?:(?:that|which)\s+)?(?:do|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\b(?:case|citation|authority|decision|opinion)\s+(?:that|which)\s+(?:does|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    r"|\blocate\s+(?:(?:the|any|these|such|this|that)\s+)?" + _AUTH +
    r"\s+(?:\w+\s+){0,2}?(?:cited|relied|referenced|quoted)\b", re.I)

PM2540 = re.compile(r"\b(?:PM|Policy\s+Memorandum|Policy\s+Memo)\s*(?:No\.?\s*)?25-40\b"
                    r"|\bUse\s+of\s+Generative\s+Artificial\s+Intelligence\s+in\s+EOIR\b", re.I)
DISC_REG = re.compile(r"\b1003\.10[1-9]\b|\b1292\.3\b")
DISC_WORD = re.compile(r"\b(?:suspen(?:d|ded|sion)|expel(?:led)?|expulsion|disbar(?:red|ment)?|disciplin\w*)\b", re.I)
DISC_CTX = re.compile(r"\bpractice\s+before\b|\bpractitioners?\b|\bdisciplinary\b", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "pm2540", "disc_reg", "discipline")


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one decision text (frozen)."""
    text = normalize(raw_text)
    head = text[:HEAD_CHARS]
    r = {"chars": len(text), "excerpts": {}}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    fake = [m.start() for m in FAKE_CITE.finditer(text)]
    r["ai_mention"] = bool(ai)
    r["fake_cite"] = bool(fake)
    pair = next(((a, q) for a in ai for q in fake if abs(a - q) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    pm = PM2540.search(text)
    r["pm2540"] = bool(pm)
    r["disc_reg"] = bool(DISC_REG.search(text))
    r["discipline"] = bool(DISC_WORD.search(head) and DISC_CTX.search(head))
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if pm:
        r["excerpts"]["pm2540"] = _excerpt(text, pm.start())
    return r


# --- the AI Hallucination Cases Database ----------------------------------------------------
EOIR_NAME = re.compile(r"Board\s+of\s+Immigration\s+Appeals|\bBIA\b|Immigration\s+(?:Court|Judge)s?\b|\bEOIR\b"
                       r"|Executive\s+Office\s+for\s+Immigration", re.I)
PFR_NAME = re.compile(r"\bv\.?\s+(?:[A-Z][a-z]+\s+){0,3}?(?:Garland|Bondi|Blanche|Sessions|Barr|Whitaker|Wilkinson|"
                      r"Holder|Lynch|Mukasey|Gonzales|Attorney\s+General)\b")


def db_check(csv_text):
    """EOIR-court rows, circuit petition-for-review rows (descriptive) and every row's joined text
    (for the citation check)."""
    court_rows, pfr_rows, joined = [], [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        name = (row.get("Case Name") or "").strip()
        item = {"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                "court": court[:80]}
        if EOIR_NAME.search(court):
            court_rows.append(item)
        elif "Cir" in court and PFR_NAME.search(name):
            pfr_rows.append(item)
        joined.append(re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v)))
    return {"court_rows": court_rows, "pfr_rows": pfr_rows, "joined": joined}


def in_db(db, cite):
    """True if any database row quotes this citation ('30 I&N Dec. 112')."""
    if not db or not cite:
        return False
    rx = re.compile(r"(?<!\d)" + re.escape(cite).replace(r"\ ", r"\s*").replace("I\\&N", r"I\s*&\s*N") + r"(?!\d)", re.I)
    return any(rx.search(j) for j in db["joined"])


# --- grading (frozen) -----------------------------------------------------------------------
def grade(docs, db=None, listing=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    P = {}
    sethi = next((d for d in docs if d.get("volume") == SETHI[0] and d.get("page") == SETHI[1]), None)
    if sethi is None or not sethi.get("readable"):
        v = "not testable"
    else:
        v = "held" if sethi.get("fake_cite") else "failed"
    P["P1"] = {"text": "Matter of Sethi, 30 I&N Dec. 112, is readable and has a fabricated-citation phrase (not blind)",
               "detail": {"found": sethi is not None, "readable": bool(sethi and sethi.get("readable"))}, "verdict": v}
    P["P2"] = {"text": "1 to 3 readable decisions in the frame have a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if 1 <= len(fake) <= 3 else "failed"}
    n_pm = sum(1 for d in readable if d.get("pm2540"))
    P["P3"] = {"text": "no readable decision cites EOIR Policy Memorandum 25-40",
               "detail": {"n": n_pm}, "verdict": "held" if n_pm == 0 else "failed"}
    k = sum(1 for d in fake if d.get("disc_reg"))
    P["P4"] = {"text": "every fabricated-citation decision cites the EOIR practitioner-discipline rules (8 C.F.R. 1003.101-1003.109 or 1292.3)",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if k == len(fake) else "failed")}
    k = sum(1 for d in fake if d.get("discipline"))
    P["P5"] = {"text": "every fabricated-citation decision is a practitioner-discipline decision",
               "detail": {"n": len(fake), "k": k},
               "verdict": "not testable" if not fake else ("held" if k == len(fake) else "failed")}
    n_ai = sum(1 for d in readable if d.get("ai_mention"))
    P["P6"] = {"text": "fewer than 5 readable decisions mention an AI term",
               "detail": {"n": n_ai}, "verdict": "held" if n_ai < 5 else "failed"}
    if db is None:
        P["P7"] = {"text": "the AI Hallucination Cases Database has no row whose court is an EOIR body (not blind)",
                   "detail": None, "verdict": "not testable"}
        P["P8"] = {"text": "no fabricated-citation decision in the frame is in the database (not blind for Sethi)",
                   "detail": None, "verdict": "not testable"}
    else:
        P["P7"] = {"text": "the AI Hallucination Cases Database has no row whose court is an EOIR body (not blind)",
                   "detail": {"court_rows": len(db["court_rows"]), "pfr_rows": len(db["pfr_rows"])},
                   "verdict": "held" if not db["court_rows"] else "failed"}
        hits = [d["cite"] for d in fake if in_db(db, d.get("cite"))]
        if not fake:
            v = "not testable"
        elif hits:
            v = "failed"
        else:
            v = "not testable" if db["court_rows"] else "held"   # an EOIR-court row needs a hand check
        P["P8"] = {"text": "no fabricated-citation decision in the frame is in the database (not blind for Sethi)",
                   "detail": {"n": len(fake), "cited_in_db": hits, "eoir_court_rows": len(db["court_rows"])},
                   "verdict": v}
    status, by_year, by_issuer = {}, {}, {}
    for d in docs:
        s = d.get("doc_status") or "not_fetched"
        status[s] = status.get(s, 0) + 1
    for d in readable:
        y = str(d.get("year") or "????")
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0, "discipline": 0})
        b["readable"] += 1
        for key in ("fake_cite", "ai_mention", "discipline"):
            b[key] += bool(d.get(key))
        by_issuer[d.get("issuer") or "unknown"] = by_issuer.get(d.get("issuer") or "unknown", 0) + 1
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "ai_mention": n_ai, "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "pm2540": n_pm, "discipline": sum(1 for d in readable if d.get("discipline")),
              "fetch_status": dict(sorted(status.items())), "by_issuer": dict(sorted(by_issuer.items())),
              "by_year": dict(sorted(by_year.items()))}
    dbpub = None if db is None else {"court_rows": db["court_rows"], "pfr_rows": len(db["pfr_rows"]), "rows": len(db["joined"])}
    return {"census_version": VERSION, "volumes": list(VOLUMES), "counts": counts, "listing": listing or [],
            "database": dbpub,
            "fake_cite_decisions": [public_row(d) for d in fake],
            "ai_mention_decisions": [public_row(d) for d in readable if d.get("ai_mention")],
            "predictions": P}


ROW_COLS = ["id", "cite", "volume", "page", "issuer", "year", "doc_status", "chars", "readable", "pdf_sha256",
            "url"] + list(FLAG_KEYS)


def public_row(d):
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# BIA / A.G. precedent fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every decision listed on EOIR's pages for volumes %s of I&N Dec. Information about public "
         "decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name."
         % ", ".join(str(v) for v in res["volumes"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Listing pages", "", "| volume | entries | no citation | no link | ID gaps | error |", "|---|---|---|---|---|---|"]
    for m in res["listing"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (m.get("volume"), m.get("entries"), m.get("no_cite"),
                                                      m.get("no_link"), m.get("gaps"), m.get("error", "")))
    L += ["", "## Decisions with a fabricated-citation phrase", "", "| id | citation | issuer | year | flags |",
          "|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s | %s | %s | %s | %s |" % (r["id"], r["cite"], r["issuer"], r["year"],
                                                 ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: x.get("id") or 0):
        w.writerow(public_row(d))
    return buf.getvalue()
