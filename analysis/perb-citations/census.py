#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""California PERB fabricated-citation census 1.0.0 (pre-registered; see PLAN.md).

Pure functions only: parsing the Board's public decision listing (WordPress REST) and decision
pages, text classification, the database check and grading. Fetching lives in run_job.py.
Standard library only. Information about public decisions of a state labor-relations board,
not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import html.parser
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
SITE = "https://perb.ca.gov"
API = SITE + "/wp-json/wp/v2/decision"
PER_PAGE = 100
FRAME_START = "2022-01-01"      # WordPress post date of the decision, inclusive
MIN_FRAME = 250                 # fewer posts in the frame: stop before any decision page is fetched
MAX_FRAME = 600                 # more: stop before any decision page is fetched
MAX_UNPARSED = 10               # more frame posts with an unrecognised slug: stop
SUMMARY_CHARS = 100
READABLE_CHARS = 300
PROXIMITY = 2000
# The four decisions found before this census was frozen (monthly summaries, Dec 2025 to Oct 2026).
KNOWN = ("2995e", "3037h", "3040m", "3041h")
PRE_AI_CUTOFF = "2025-01-01"


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def listing_url(page):
    return "%s?per_page=%d&page=%d&orderby=date&order=desc&_fields=id,slug,date,link,title,content" % (
        API, PER_PAGE, page)


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


class _Text(html.parser.HTMLParser):
    BLOCK = ("p", "br", "div", "li", "h1", "h2", "h3", "h4", "h5", "tr", "td", "th", "section", "span")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self.BLOCK:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in self.BLOCK:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_text(s):
    p = _Text()
    p.feed(s or "")
    p.close()
    return normalize("".join(p.parts)).strip()


# --- the listing (WordPress REST, newest first) -------------------------------------------------
SLUG_RX = re.compile(r"^([a-z]{0,2})(\d{1,5})([a-z]{1,3})?$")
DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_slug(slug):
    """'3041h' -> number '3041', suffix 'h', key '3041h'; 'a530ha' -> prefix 'a', key 'a530h' (a later
    version keeps its first suffix letter, so it counts with the original). Unrecognised -> key = slug."""
    s = (slug or "").strip().lower()
    m = SLUG_RX.match(s)
    if not m:
        return {"prefix": None, "number": None, "suffix": None, "decision_key": s, "slug_ok": False}
    suf = m.group(3) or ""
    return {"prefix": m.group(1), "number": m.group(2), "suffix": suf,
            "decision_key": "%s%s%s" % (m.group(1), m.group(2), suf[:1]), "slug_ok": True}


def parse_api_page(body):
    """Posts on one REST page: id, slug, date (YYYY-MM-DD of the post), link, summary (plain text)."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    data = json.loads(body)
    if not isinstance(data, list):
        raise ValueError("listing page is not a JSON list")
    out = []
    for it in data:
        slug = str(it.get("slug") or "").strip().lower()
        d = str(it.get("date") or "")[:10]
        e = {"id": it.get("id"), "slug": slug, "date": d if DATE_ISO.match(d) else None,
             "link": str(it.get("link") or ""),
             "summary": html_text(((it.get("content") or {}).get("rendered")) or "")}
        e.update(parse_slug(slug))
        out.append(e)
    return out


def in_window(e):
    return bool(e.get("date")) and e["date"] >= FRAME_START


def page_url(e):
    link = (e.get("link") or "").strip()
    if link.startswith(SITE + "/decision/"):
        return link
    return "%s/decision/%s/" % (SITE, e.get("slug") or "")


# --- one decision page ----------------------------------------------------------------------------
PDF_HREF = re.compile(r"""href\s*=\s*["']([^"']*/decisionbank/[^"'?#]+?\.pdf)(?:[?#][^"']*)?["']""", re.I)
DEC_DATE = re.compile(r"Decision\s+Date\s*:?\s*([A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4})")
H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)


def parse_long_date(s):
    try:
        return dt.datetime.strptime(re.sub(r"\s+", " ", s.replace(".", "")).strip(), "%B %d, %Y").date().isoformat()
    except (ValueError, AttributeError):
        return None


def parse_page(body, slug, url):
    """PDF link (the one whose file name carries the slug, else the only one), decision date, heading."""
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    links = []
    for h in PDF_HREF.findall(body):
        u = urllib.parse.urljoin(url, html.unescape(h).strip())
        if u not in links:
            links.append(u)
    own = [u for u in links if slug and slug in u.rsplit("/", 1)[-1].lower()]
    pdf = own[0] if own else (links[0] if len(links) == 1 else "")
    text = html_text(body)
    m = DEC_DATE.search(text)
    h = H1.search(body)
    return {"pdf_url": pdf, "pdf_links": len(links), "decision_date": parse_long_date(m.group(1)) if m else None,
            "nonprecedential": bool(re.search(r"\bNon-?\s?Precedential\b", text, re.I)),
            "heading": html_text(h.group(1))[:300] if h else ""}


# --- text classification (frozen; the patterns of MV2's WCAB census, plus Atwater) -----------------
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
ATWATER = re.compile(r"\bAtwater\b")
ABUSE = re.compile(r"\babuse\s+of\s+(?:the\s+)?(?:PERB'?s?\s+)?process\b", re.I)

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "hallucination", "atwater")


def _excerpt(text, pos, width=350):
    return text[max(0, pos - width):min(len(text), pos + width)]


def classify(raw_text):
    """Flags for one text (a summary or a full decision), frozen."""
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
    w = ATWATER.search(text)
    r["atwater"] = bool(w)
    r["abuse_of_process"] = bool(ABUSE.search(text))
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    if h:
        r["excerpts"]["hallucination"] = _excerpt(text, h.start())
    if w:
        r["excerpts"]["atwater"] = _excerpt(text, w.start())
    return r


def combine(d, summ, full):
    """Set a post's flags from its summary's and (if read) its full text's classification."""
    full = full or {}
    d["chars_summary"] = summ["chars"]
    d["summary_ok"] = summ["chars"] >= SUMMARY_CHARS
    d["chars_full"] = full.get("chars", 0)
    d["fake_summary"] = summ["fake_cite"]
    d["fake_full"] = bool(full.get("fake_cite"))
    for k in FLAG_KEYS + ("abuse_of_process",):
        d[k] = bool(summ.get(k)) or bool(full.get(k))
    return d


# --- the AI Hallucination Cases Database -----------------------------------------------------------
PERB_COURT = re.compile(r"Public\s+Employment\s+Relations\s+Board|\bPERB\b", re.I)
_STOP = {"decision", "association", "teachers", "employees", "employee", "union", "local", "county", "city",
         "district", "school", "schools", "unified", "college", "colleges", "community", "university",
         "california", "regents", "federation", "american", "council", "state", "public", "service", "services",
         "workers", "international", "united", "elementary", "education", "educators", "labor", "teamsters",
         "afscme", "seiu", "board", "trustees", "superior", "court", "trial", "faculty", "classified", "chapter",
         "transit", "authority", "department", "officers", "police", "fire", "firefighters", "nurses",
         "professional", "engineers", "management", "water", "sanitation", "high", "joint", "valley", "unit",
         "and", "inc", "the", "of", "cta/nea", "nea", "cta", "employment", "relations", "agency", "office",
         "system", "trades", "building", "construction", "general", "health", "medical", "center", "hospital"}


def db_check(csv_text):
    """PERB-court rows (names kept private) and every row's joined text."""
    rows, joined = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        j = re.sub(r"\s+", " ", " | ".join(str(v) for v in row.values() if v))
        court = (row.get("Court") or "").strip()
        if PERB_COURT.search(court):
            rows.append({"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                         "court": court[:80], "name": (row.get("Case Name") or "").strip()})
        joined.append(j)
    return {"perb_rows": rows, "joined": joined}


def name_tokens(heading):
    """Distinctive words (5+ letters, not boilerplate) of a decision page's heading."""
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]{4,}", heading or "") if t.lower() not in _STOP]


def in_db(db, d):
    """True if a database row that mentions PERB quotes the decision number with its letter (2995-E, 2995E),
    or a PERB-court row's case name contains a distinctive word of the decision page's heading."""
    if not db:
        return False
    num, suf = d.get("number"), (d.get("suffix") or "")[:1]
    if num and suf:
        rx = re.compile(r"(?<![\dA-Za-z])%s\s*-?\s*%s(?![A-Za-z\d])" % (re.escape(num), re.escape(suf)), re.I)
        if any(rx.search(j) and PERB_COURT.search(j) for j in db["joined"]):
            return True
    for t in name_tokens(d.get("heading")):
        trx = re.compile(r"\b" + re.escape(t) + r"\b", re.I)
        if any(trx.search(r["name"]) for r in db["perb_rows"]):
            return True
    return False


# --- grading (frozen) ----------------------------------------------------------------------------
def _keys(rows):
    return sorted({d["decision_key"] for d in rows})


def grade(docs, db=None, listing=None):
    fake = [d for d in docs if d.get("fake_cite")]
    fake_keys = _keys(fake)
    pdf = [d for d in docs if d.get("pdf_posted")]
    full = [d for d in pdf if d.get("readable_full")]
    summ_ok = [d for d in docs if d.get("summary_ok")]
    P = {}
    in_frame = [k for k in KNOWN if any(d["decision_key"] == k for d in docs)]
    flagged = [k for k in KNOWN if k in fake_keys]
    P["P1"] = {"text": "recall check (not blind): the four decisions found from the monthly summaries (2995-E, 3037-H, "
                       "3040-M, 3041-H) are in the frame and each has a fabricated-citation phrase in its summary or "
                       "full text",
               "detail": {"in_frame": in_frame, "flagged": flagged},
               "verdict": "held" if len(flagged) == len(KNOWN) else "failed"}
    P["P2"] = {"text": "5 to 12 decisions in the frame have a fabricated-citation phrase (summary or full text)",
               "detail": {"n": len(fake_keys)}, "verdict": "held" if 5 <= len(fake_keys) <= 12 else "failed"}
    early = _keys([d for d in fake if (d.get("date") or "") < PRE_AI_CUTOFF])
    P["P3"] = {"text": "no decision posted before 1 January 2025 has a fabricated-citation phrase",
               "detail": {"early": early}, "verdict": "held" if not early else "failed"}
    under = _keys([d for d in full if d.get("fake_full") and not d.get("fake_summary")])
    P["P4"] = {"text": "at least one decision whose full text is posted has a fabricated-citation phrase in the full "
                       "text but not in the Board's summary",
               "detail": {"full_texts": len(full), "full_only": under},
               "verdict": "not testable" if not full else ("held" if under else "failed")}
    ai_keys = _keys([d for d in fake if d.get("ai_mention")])
    P["P5"] = {"text": "fewer than half of the decisions with a fabricated-citation phrase mention an AI term",
               "detail": {"n": len(fake_keys), "k": len(ai_keys), "ai": ai_keys},
               "verdict": "not testable" if not fake_keys else ("held" if 2 * len(ai_keys) < len(fake_keys)
                                                                else "failed")}
    text6 = ("the database has at most one PERB-court row, and at least three decisions with a fabricated-citation "
             "phrase are not in it (not blind: one PERB row on 11 Nov 2026)")
    if db is None:
        P["P6"] = {"text": text6, "detail": None, "verdict": "not testable"}
    else:
        listed = {d["decision_key"] for d in fake if d.get("in_db")}
        missing = [k for k in fake_keys if k not in listed]
        n_rows = len(db["perb_rows"])
        P["P6"] = {"text": text6, "detail": {"perb_rows": n_rows, "decisions": len(fake_keys), "missing": missing},
                   "verdict": "not testable" if not fake_keys else ("held" if n_rows <= 1 and len(missing) >= 3
                                                                    else "failed")}
    share_s = (len(summ_ok) / len(docs)) if docs else 0.0
    share_f = (len(full) / len(pdf)) if pdf else 0.0
    P["P7"] = {"text": "method check: at least 98% of posts in the frame have a summary of 100+ characters, and at "
                       "least 95% of posted full texts are readable",
               "detail": {"summaries": len(summ_ok), "in_frame": len(docs), "share_summaries": round(share_s, 4),
                          "pdfs": len(pdf), "readable": len(full), "share_readable": round(share_f, 4)},
               "verdict": "held" if docs and pdf and share_s >= 0.98 and share_f >= 0.95 else "failed"}
    atw = [k for k in _keys([d for d in fake if d.get("atwater")]) if k != "2995e"]
    P["P8"] = {"text": "at least two decisions with a fabricated-citation phrase, other than Atwater (2995-E) itself, "
                       "mention Atwater",
               "detail": {"k": len(atw), "decisions": atw}, "verdict": "held" if len(atw) >= 2 else "failed"}
    by_year = {}
    for d in docs:
        y = (d.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"posts": 0, "pdf_posted": 0, "readable_full": 0, "fake_cite": 0,
                                   "ai_mention": 0, "hallucination": 0})
        b["posts"] += 1
        for f in ("pdf_posted", "readable_full", "fake_cite", "ai_mention", "hallucination"):
            b[f] += bool(d.get(f))
    status = {}
    for d in docs:
        s = "%s/%s" % (d.get("page_status") or "not_fetched", d.get("pdf_status") or "-")
        status[s] = status.get(s, 0) + 1
    counts = {"in_frame": len(docs), "decisions": len(_keys(docs)), "summaries_ok": len(summ_ok),
              "pdf_posted": len(pdf), "readable_full": len(full), "fake_cite_posts": len(fake),
              "fake_cite_decisions": len(fake_keys), "fake_summary": sum(1 for d in docs if d.get("fake_summary")),
              "fake_full": sum(1 for d in docs if d.get("fake_full")),
              "nonprecedential": sum(1 for d in docs if d.get("nonprecedential"))}
    for f in ("ai_mention", "ai_citation", "hallucination", "atwater", "abuse_of_process"):
        counts[f] = sum(1 for d in docs if d.get(f))
    counts.update({"fetch_status": dict(sorted(status.items())), "by_year": dict(sorted(by_year.items()))})
    dbpub = None if db is None else {"perb_rows": [{k: r[k] for k in ("case_id", "date", "court")}
                                                   for r in db["perb_rows"]], "rows": len(db["joined"])}
    other = lambda d: any(d.get(k) for k in ("ai_mention", "hallucination", "atwater")) and not d.get("fake_cite")
    return {"census_version": VERSION, "frame_start": FRAME_START, "counts": counts, "listing": listing or {},
            "database": dbpub,
            "fake_cite_posts": [public_row(d) for d in fake],
            "other_flagged_posts": [public_row(d) for d in docs if other(d)],
            "predictions": P}


ROW_COLS = ["slug", "decision_key", "date", "decision_date", "nonprecedential", "pdf_posted", "page_status",
            "pdf_status", "chars_summary", "chars_full", "summary_ok", "readable_full", "pdf_sha256", "in_db",
            "known", "fake_summary", "fake_full"] + list(FLAG_KEYS) + ["abuse_of_process"]


def public_row(d):
    """One public row: decision numbers and flags only; no names, headings or texts."""
    return {c: d.get(c, "") for c in ROW_COLS}


def results_md(res, sources):
    L = ["# California PERB fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every decision and order the Public Employment Relations Board posted on perb.ca.gov from %s on. "
         "Information about public decisions of a state labor-relations board, not legal advice. "
         "Made with AI agents working in MV2's name." % res["frame_start"], "",
         "Sources: `%s`" % json.dumps(sources), "", "Listing: `%s`" % json.dumps(res["listing"]), "",
         "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Posts with a fabricated-citation phrase", "",
          "| slug | posted | decision date | full text posted | in summary | in full text | in database | flags |",
          "|---|---|---|---|---|---|---|---|"]
    for r in res["fake_cite_posts"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["slug"], r["date"], r["decision_date"], r["pdf_posted"], r["fake_summary"], r["fake_full"], r["in_db"],
            ", ".join(k for k in FLAG_KEYS + ("abuse_of_process",) if r.get(k))))
    L += ["", "## Other posts with an AI term, 'hallucinat...' or Atwater", "",
          "| slug | posted | flags |", "|---|---|---|"]
    for r in res["other_flagged_posts"]:
        L.append("| %s | %s | %s |" % (r["slug"], r["date"], ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("date") or "", x.get("slug") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
