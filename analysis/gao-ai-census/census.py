#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Prospective census of published GAO bid-protest decisions that discuss AI-fabricated
authority (census 1.0.0). Standard library only. Information only, not legal advice.

One run is one "wave". It reads the published ledger (decisions.csv in this folder on
GitHub), fetches GAO's legal-decisions RSS feed once, and fetches each new bid-protest
decision page at least DELAY_S seconds apart, honouring gao.gov's robots.txt
(Crawl-delay: 420; /search is never requested). It classifies only the decision text
(from the "Matter of" line to the General Counsel's signature), never the site menus.
Raw pages stay private in out/raw/; only derived rows are published.
"""
from __future__ import annotations

import csv
import datetime
import email.utils
import hashlib
import html
import io
import re
import urllib.parse
import xml.etree.ElementTree as ET

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
DELAY_S = 425
MAX_PAGES = 40
RSS_URL = "https://www.gao.gov/rss/reportslegal.xml"

AI_TERMS = ("artificial intelligence", "large language model", "large-language model", "generative ai",
            "genai", "chatgpt", "hallucinat", "ai-generated", "ai program", "ai tool")
CITE_TERMS = ("non-existent", "nonexistent", "does not exist", "do not exist", "fabricated", "fictitious",
              "no such decision", "erroneous citation", "inaccurate citation", "could not locate",
              "unable to locate")
SUSTAINED_RE = re.compile(r"protests? (is|are) sustained|we sustain the protest", re.I)
COMPANY_RE = re.compile(r"\b(LLC|L\.L\.C\.|Inc\b|Inc\.|Incorporated|Corp\b|Corp\.|Corporation|Company|Co\.|"
                        r"Ltd\b|Ltd\.|LP\b|LLP\b|PLLC\b|P\.C\.|PC\b|JV\b|Joint Venture|d/b/a)", re.I)

FIELDS = ["b_number", "b_numbers", "url", "rss_pubdate", "decision_date", "protester", "protester_counsel",
          "parsed", "category", "ai_terms", "cite_terms", "sustained", "body_chars", "body_sha256",
          "wave", "fetched_at"]


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def text_of(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>", "\n", raw)
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"[ \t ]+", " ", t)


def parse_rss(xml_text) -> list:
    """xml_text may be bytes (as fetched) or str."""
    root = ET.fromstring(xml_text)
    items = []
    for it in root.iter("item"):
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        items.append({"link": link, "title": (it.findtext("title") or "").strip(), "pubdate": iso_pubdate(pub)})
    return items


def iso_pubdate(pub: str) -> str:
    try:
        d = email.utils.parsedate_to_datetime(pub)
        return d.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ""


def b_numbers_from_link(link: str) -> list:
    last = urllib.parse.unquote(link.rstrip("/").rsplit("/", 1)[-1])
    out = []
    for part in last.split(","):
        part = part.strip()
        if re.match(r"(?i)^b-\d+", part):
            out.append("B-" + part[2:])
    return out


def is_protest(b_number: str) -> bool:
    m = re.match(r"B-(\d+)", b_number or "")
    return bool(m) and int(m.group(1)) >= 400000


def extract_body(page: str):
    i = page.find('class="matterOf"')
    if i < 0:
        return None
    start = page.rfind("<p", 0, i)
    if start < 0:
        start = i
    j = page.find("General Counsel</p>", i)
    end = j + len("General Counsel</p>") if j >= 0 else min(len(page), i + 400000)
    return text_of(page[start:end])


def iso_decision_date(s: str) -> str:
    try:
        return datetime.datetime.strptime(s.strip().rstrip("."), "%B %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        return ""


def protester_public(name: str) -> str:
    """Company names are published; a name without a company marker is withheld."""
    name = (name or "").strip()
    return name if COMPANY_RE.search(name) else ""


def parse_decision(page: str) -> dict:
    body = extract_body(page)
    if body is None:
        return {"parsed": False}
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    protester, ddate, counsel = "", "", "unknown"
    for ln in lines:
        if ln.upper().startswith("DIGEST") or ln.upper().startswith("DECISION"):
            break
        if ln.startswith("Matter of:") and not protester:
            protester = ln[len("Matter of:"):].strip()
        elif ln.startswith("Date:") and not ddate:
            ddate = iso_decision_date(ln[len("Date:"):])
        elif counsel == "unknown" and re.search(r"\bthe protesters?\b", ln, re.I):
            counsel = "lawyer" if "Esq." in ln else "no_lawyer"
    low = body.lower()
    ai = [t for t in AI_TERMS if re.search(r"\b" + re.escape(t), low)]
    cite = [t for t in CITE_TERMS if re.search(r"\b" + re.escape(t), low)]
    category = "ai_citation" if (ai and cite) else "ai_only" if ai else "cite_only" if cite else "none"
    return {"parsed": True, "protester_full": protester, "protester": protester_public(protester),
            "decision_date": ddate, "protester_counsel": counsel, "category": category,
            "ai_terms": ";".join(ai), "cite_terms": ";".join(cite),
            "sustained": bool(SUSTAINED_RE.search(body)), "body_chars": len(body),
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()}


def load_ledger(text: str) -> list:
    if not text.strip():
        return []
    return [dict(r) for r in csv.DictReader(io.StringIO(text))]


def ledger_csv(rows: list) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r.get("rss_pubdate", ""), r.get("b_number", "")), reverse=True):
        w.writerow({k: r.get(k, "") for k in FIELDS})
    return buf.getvalue()


def gap_possible(feed_dates: list, ledger_dates: list) -> bool:
    """True if the feed's oldest item is newer than the ledger's newest: items may have been missed."""
    feed = [d for d in feed_dates if d]
    led = [d for d in ledger_dates if d]
    if not feed or not led:
        return False
    return min(feed) > max(led)


def _key(name: str) -> str:
    name = re.sub(r"(?i)^matter of:?\s*", "", name or "")
    name = re.split(r",|--|\(|\bd/b/a\b|\bv\.", name)[0]
    name = COMPANY_RE.sub(" ", name)
    return re.sub(r"[^a-z0-9]", "", name.lower())


def db_match(decision: dict, db_rows: list) -> bool:
    """Pre-registered rule for B3: a database row at GAO matches a census decision if its case name,
    source or details contain the decision's B-number core (B-dddddd), or if its case-name key equals
    the protester key and its Date is within 3 days of the decision date."""
    core = re.match(r"B-\d{6}", decision.get("b_number", ""))
    core = core.group(0).lower() if core else ""
    key = _key(decision.get("protester_full") or decision.get("protester", ""))
    try:
        dd = datetime.date.fromisoformat(decision.get("decision_date", ""))
    except ValueError:
        dd = None
    for r in db_rows:
        court = r.get("Court", "")
        if not re.search(r"GAO|Government Accountability Office|Comptroller General", court):
            continue
        hay = " ".join([r.get("Case Name", ""), r.get("Source", ""), r.get("Details", "")]).lower()
        if core and core in hay.replace("‑", "-"):
            return True
        if key and len(key) >= 4 and _key(r.get("Case Name", "")) == key and dd:
            try:
                rd = datetime.date.fromisoformat(r.get("Date", "")[:10])
            except ValueError:
                continue
            if abs((rd - dd).days) <= 3:
                return True
    return False


def plan_wave(items: list, ledger_ids: set, max_pages: int = MAX_PAGES):
    """Split feed items into pages to fetch (new protest decisions) and the rest."""
    fetch, skipped = [], {"not_protest": 0, "already_in_ledger": 0, "over_cap": 0, "no_b_number": 0}
    seen = set()
    for it in items:
        bn = b_numbers_from_link(it["link"])
        if not bn:
            skipped["no_b_number"] += 1
            continue
        if not is_protest(bn[0]):
            skipped["not_protest"] += 1
            continue
        if bn[0] in ledger_ids or bn[0] in seen:
            skipped["already_in_ledger"] += 1
            continue
        if len(fetch) >= max_pages:
            skipped["over_cap"] += 1
            continue
        seen.add(bn[0])
        fetch.append(dict(it, b_number=bn[0], b_numbers=";".join(bn)))
    return fetch, skipped
