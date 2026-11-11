#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Pre-registered census (version 1.0.0): how far has Executive Order 14434's rename of
"artificial intelligence" to "Super Intelligence" reached in the Federal Register?

EO 14434, "Inaugurating the Era of Super Intelligence" (signed 29 Sept 2026, 91 FR 63129,
FR document 2026-20321, published 2 Oct 2026), tells executive departments and agencies to use
"Super Intelligence" and "SI" in place of "Artificial Intelligence" and "AI" in non-statutory
documents. This census reads every Federal Register document that the Federal Register's own
full-text search returns for "artificial intelligence", "super intelligence" or superintelligence
in fixed publication-date windows, and counts which words each document actually uses.

Source: the Federal Register API (https://www.federalregister.gov/api/v1/documents.json) and each
document's plain-text rendition (raw_text_url); robots.txt does not disallow /api/ or
/documents/full_text/. Also a descriptive eCFR snapshot. This file holds the windows, the term
list, the classification and the grading; run_job.py does the requests.
Standard library only. Information about public federal documents, not legal advice.
"""
from __future__ import annotations

import csv
import datetime
import html
import io
import re
import statistics
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
API = "https://www.federalregister.gov/api/v1/documents.json"
ECFR_API = "https://www.ecfr.gov/api/search/v1/results"
PER_PAGE = 100
MAX_PAGES = 20
DELAY_S = 1
ECFR_DELAY_S = 2

# Search terms sent to the Federal Register's full-text search (quoted = exact phrase).
TERMS = ['"artificial intelligence"', '"super intelligence"', "superintelligence"]
ECFR_TERMS = ['"super intelligence"', "superintelligence", '"artificial intelligence"']

# Publication-date windows, both ends inclusive. W0 = before the order was published.
WINDOWS = {
    "W0": ("2026-08-17", "2026-10-01"),
    "W1": ("2026-10-02", "2026-11-11"),
    "W2": ("2026-11-12", "2026-12-11"),
}
WAVES = {"w01": ("W0", "W1"), "w02": ("W0", "W1", "W2")}
FIELDS = ["document_number", "publication_date", "type", "agencies", "title", "raw_text_url",
          "html_url", "citation"]

MIN_FRAME_W1 = 20
MAX_FRAME = 600
READABLE_CHARS = 500

# Independent regulatory agencies named in 44 U.S.C. 3502(5), matched as lower-case
# substrings of the agency names the Federal Register lists for a document.
LISTED_INDEPENDENT = (
    "federal reserve system",
    "commodity futures trading commission",
    "consumer product safety commission",
    "federal communications commission",
    "federal deposit insurance corporation",
    "federal energy regulatory commission",
    "federal housing finance agency",
    "federal maritime commission",
    "federal trade commission",
    "federal mine safety and health review commission",
    "national labor relations board",
    "nuclear regulatory commission",
    "occupational safety and health review commission",
    "postal regulatory commission",
    "securities and exchange commission",
    "consumer financial protection bureau",
    "financial research office",
    "office of financial research",
    "comptroller of the currency",
)
OCC = "comptroller of the currency"

PATTERNS = [
    ("si", re.compile(r"\bsuper[\s\-]+intelligence\b", re.I)),
    ("superintelligence", re.compile(r"\bsuperintelligen\w*", re.I)),
    ("ai", re.compile(r"\bartificial[\s\-]+intelligence\b", re.I)),
    ("ai_lower", re.compile(r"\bartificial intelligence\b")),
    ("ai_acronym", re.compile(r"\bAI\b")),
    ("si_acronym", re.compile(r"\bSI\b")),
    ("eo14434", re.compile(r"\b14434\b|era of super intelligence", re.I)),
    ("usc9401", re.compile(r"\b9401\b")),
]
COUNT_KEYS = tuple(k for k, _ in PATTERNS)
EXCERPT_KEYS = ("si", "ai", "eo14434")
TAG = re.compile(r"<[^<>]{0,300}>")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def search_url(term, start, end, page=1):
    params = [("conditions[term]", term),
              ("conditions[publication_date][gte]", start),
              ("conditions[publication_date][lte]", end),
              ("order", "oldest"), ("per_page", str(PER_PAGE)), ("page", str(page))]
    params += [("fields[]", f) for f in FIELDS]
    return API + "?" + urllib.parse.urlencode(params)


def ecfr_url(term):
    return ECFR_API + "?" + urllib.parse.urlencode([("query", term), ("per_page", "1")])


def parse_page(obj):
    """(count, total_pages, results) from one decoded API response."""
    count = int(obj.get("count") or 0)
    pages = int(obj.get("total_pages") or 0)
    results = obj.get("results") or []
    return count, pages, results


def ecfr_total(obj):
    meta = obj.get("meta") or {}
    return int(meta.get("total_count") or 0)


def normalize(s):
    s = TAG.sub(" ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def agency_names(doc):
    out = []
    for a in doc.get("agencies") or []:
        n = str(a.get("name") or a.get("raw_name") or "").strip()
        if n:
            out.append(n)
    return out


def top_agency(doc):
    for a in doc.get("agencies") or []:
        n = str(a.get("name") or a.get("raw_name") or "").strip()
        if n and not a.get("parent_id"):
            return n
    names = agency_names(doc)
    return names[0] if names else ""


def listed_keys(names):
    low = [n.lower() for n in names]
    return sorted({k for k in LISTED_INDEPENDENT for n in low if k in n})


def is_presidential(doc):
    return str(doc.get("type") or "").lower().startswith("presidential")


def agency_class(doc):
    if is_presidential(doc):
        return "presidential"
    return "listed_independent" if listed_keys(agency_names(doc)) else "other"


def classify(text, width=200, max_per=3):
    """Counts per pattern key, the category and a few excerpts (private) for one document."""
    counts, excerpts = {}, {}
    for key, rx in PATTERNS:
        found = list(rx.finditer(text))
        counts[key] = len(found)
        if key in EXCERPT_KEYS and found:
            parts = []
            for m in found[:max_per]:
                a, b = max(0, m.start() - width), min(len(text), m.end() + width)
                parts.append(text[a:b])
            excerpts[key] = "\n...\n".join(parts)
    return {"counts": counts, "category": category(counts), "chars": len(text), "excerpts": excerpts}


def category(c):
    si, ai = c.get("si", 0) > 0, c.get("ai", 0) > 0
    if si and ai:
        return "both"
    if si:
        return "si_only"
    if ai:
        return "ai_only"
    return "neither"


def week_start(date_str):
    d = datetime.date.fromisoformat(date_str)
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def window_of(date_str, windows=WINDOWS):
    for w, (a, b) in windows.items():
        if a <= date_str <= b:
            return w
    return ""


def _np(docs, window):
    """Readable, non-presidential documents of one window."""
    return [d for d in docs if d.get("window") == window and d.get("readable")
            and d.get("agency_class") != "presidential"]


def _verdict(ok):
    return "held" if ok else "failed"


def _si(d):
    return d["counts"].get("si", 0) > 0


def _share(num, den):
    return round(num / den, 4) if den else None


def si_share_other(docs, window):
    """(documents with "Super Intelligence", matched documents) among readable non-presidential
    documents of agencies not on the 3502(5) list."""
    m = [d for d in _np(docs, window) if d["agency_class"] == "other" and d["category"] != "neither"]
    return sum(1 for d in m if _si(d)), len(m)


def grade(docs, ecfr, wave):
    windows = WAVES[wave]
    pred = {}
    w1 = _np(docs, "W1")
    S = [d for d in w1 if _si(d)]
    B = [d for d in S if d["counts"].get("ai", 0) > 0]
    A = [d for d in w1 if d["category"] == "ai_only"]

    if S:
        pred["P1"] = {"verdict": _verdict(2 * len(B) >= len(S)), "value": "%d of %d" % (len(B), len(S))}
    else:
        pred["P1"] = {"verdict": "not testable", "value": "no such document"}
    pred["P1"]["text"] = ("At least half of the W1 non-presidential documents that say 'Super Intelligence' "
                          "also say 'artificial intelligence'.")
    if B:
        n = sum(1 for d in B if d["counts"].get("eo14434", 0) > 0)
        pred["P2"] = {"verdict": _verdict(2 * n >= len(B)), "value": "%d of %d" % (n, len(B))}
    else:
        pred["P2"] = {"verdict": "not testable", "value": "no W1 document with both terms"}
    pred["P2"]["text"] = ("At least half of the W1 non-presidential documents with both terms cite EO 14434 "
                          "(its number or its title).")
    if A:
        n = sum(1 for d in A if d["agency_class"] == "other")
        pred["P3"] = {"verdict": _verdict(2 * n >= len(A)), "value": "%d of %d" % (n, len(A))}
        med = statistics.median([d["counts"].get("ai_lower", 0) for d in A])
        pred["P5"] = {"verdict": _verdict(med >= 1), "value": "median %s" % med}
        ind = sorted({k for d in A if d["agency_class"] == "listed_independent"
                      for k in listed_keys(agency_names(d)) if k != OCC})
        pred["P6"] = {"verdict": _verdict(bool(ind)), "value": "; ".join(ind) or "none"}
    else:
        for k in ("P3", "P5", "P6"):
            pred[k] = {"verdict": "not testable", "value": "no W1 ai_only document"}
    pred["P3"]["text"] = ("At least half of the W1 non-presidential documents that say 'artificial intelligence' "
                          "and never 'Super Intelligence' come from agencies not on the 44 U.S.C. 3502(5) list.")
    pred["P5"]["text"] = ("In those 'artificial intelligence'-only W1 documents, the median count of lower-case "
                          "'artificial intelligence' (ordinary use, not a capitalised name) is at least 1.")
    pred["P6"]["text"] = ("At least one listed independent regulatory agency other than the OCC has a W1 document "
                          "that says 'artificial intelligence' and never 'Super Intelligence'.")
    w0 = [d for d in docs if d.get("window") == "W0" and d.get("readable") and _si(d)]
    pred["P4"] = {"text": "At most 1 W0 document (before 2 Oct 2026, any type) says 'Super Intelligence'.",
                  "verdict": _verdict(len(w0) <= 1), "value": str(len(w0))}
    fetched = [d for d in docs if d.get("window") in windows]
    rd = sum(1 for d in fetched if d.get("readable"))
    pred["P7"] = {"text": "At least 98% of the documents in the frame are readable (500+ characters of text).",
                  "verdict": _verdict(bool(fetched) and rd >= 0.98 * len(fetched)),
                  "value": "%d of %d" % (rd, len(fetched))}
    if "W2" in windows:
        n1, d1 = si_share_other(docs, "W1")
        n2, d2 = si_share_other(docs, "W2")
        if d1 and d2:
            pred["P8"] = {"verdict": _verdict(n2 / d2 > n1 / d1),
                          "value": "W2 %d of %d vs W1 %d of %d" % (n2, d2, n1, d1)}
        else:
            pred["P8"] = {"verdict": "not testable", "value": "W1 %d of %d, W2 %d of %d" % (n1, d1, n2, d2)}
        ind2 = sorted({k for d in _np(docs, "W2") if d["agency_class"] == "listed_independent" and _si(d)
                       for k in listed_keys(agency_names(d)) if k != OCC})
        pred["P9"] = {"verdict": _verdict(bool(ind2)), "value": "; ".join(ind2) or "none"}
    else:
        pred["P8"] = {"verdict": "pending wave w02", "value": ""}
        pred["P9"] = {"verdict": "pending wave w02", "value": ""}
    pred["P8"]["text"] = ("Among matched non-presidential documents of agencies not on the 3502(5) list, the share "
                          "that says 'Super Intelligence' is higher in W2 than in W1.")
    pred["P9"]["text"] = ("At least one listed independent regulatory agency other than the OCC has a W2 document "
                          "that says 'Super Intelligence'.")
    return {"census_version": VERSION, "wave": wave, "windows": {w: WINDOWS[w] for w in windows},
            "predictions": {k: pred[k] for k in sorted(pred)}, "counts": describe(docs, windows),
            "ecfr": ecfr}


def describe(docs, windows):
    out = {}
    for w in windows:
        ds = [d for d in docs if d.get("window") == w]
        rd = [d for d in ds if d.get("readable")]
        cell = {"documents": len(ds), "readable": len(rd), "by_category": {}, "by_class": {},
                "weekly_nonpresidential": {}, "agencies": {}}
        for d in rd:
            cat, cls = d["category"], d["agency_class"]
            cell["by_category"][cat] = cell["by_category"].get(cat, 0) + 1
            c = cell["by_class"].setdefault(cls, {})
            c[cat] = c.get(cat, 0) + 1
            if cls != "presidential" and cat != "neither":
                wk = cell["weekly_nonpresidential"].setdefault(week_start(d["publication_date"]),
                                                               {"matched": 0, "super_intelligence": 0})
                wk["matched"] += 1
                wk["super_intelligence"] += 1 if _si(d) else 0
                ag = cell["agencies"].setdefault(d.get("top_agency") or "?",
                                                 {"matched": 0, "super_intelligence": 0, "ai_only": 0})
                ag["matched"] += 1
                ag["super_intelligence"] += 1 if _si(d) else 0
                ag["ai_only"] += 1 if cat == "ai_only" else 0
        n, den = si_share_other(docs, w)
        np_m = [d for d in _np(docs, w) if d["category"] != "neither"]
        cell["si_share_nonpresidential"] = _share(sum(1 for d in np_m if _si(d)), len(np_m))
        cell["si_share_other_agencies"] = _share(n, den)
        cell["weekly_nonpresidential"] = dict(sorted(cell["weekly_nonpresidential"].items()))
        cell["agencies"] = dict(sorted(cell["agencies"].items(), key=lambda kv: (-kv[1]["matched"], kv[0])))
        out[w] = cell
    return out


ROW_FIELDS = ["document_number", "publication_date", "window", "type", "top_agency", "agencies",
              "agency_class", "listed_independent", "citation", "title", "html_url", "fetch_status",
              "chars", "readable", "category", "terms_matched"] + list(COUNT_KEYS)


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(ROW_FIELDS)
    for d in sorted(docs, key=lambda x: (x.get("publication_date") or "", x.get("document_number") or "")):
        names = agency_names(d)
        row = [d.get("document_number"), d.get("publication_date"), d.get("window"), d.get("type"),
               d.get("top_agency"), "; ".join(names), d.get("agency_class"), "; ".join(listed_keys(names)),
               d.get("citation"), d.get("title"), d.get("html_url"), d.get("fetch_status"), d.get("chars", 0),
               d.get("readable", False), d.get("category", ""), "; ".join(sorted(d.get("terms_matched") or []))]
        row += [(d.get("counts") or {}).get(k, 0) for k in COUNT_KEYS]
        w.writerow(row)
    return buf.getvalue()


def results_md(res):
    lines = ["# Results: EO 14434 terminology census (census %s, wave %s)" % (res["census_version"], res["wave"]),
             "", "Generated %s by the pre-registered job. Graded exactly as frozen in PLAN.md." % now(), "",
             "## Predictions", "", "| | Prediction | Verdict | Value |", "|---|---|---|---|"]
    for k, p in res["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, p.get("text", ""), p["verdict"], p.get("value", "")))
    lines += ["", "## Counts by window (readable documents)", ""]
    for w, c in res["counts"].items():
        a, b = res["windows"][w]
        lines.append("### %s (%s to %s): %d documents, %d readable" % (w, a, b, c["documents"], c["readable"]))
        lines.append("")
        lines.append("- By category: " + ", ".join("%s %d" % kv for kv in sorted(c["by_category"].items())))
        for cls, cats in sorted(c["by_class"].items()):
            lines.append("- %s: %s" % (cls, ", ".join("%s %d" % kv for kv in sorted(cats.items()))))
        lines.append("- Share saying 'Super Intelligence' among matched non-presidential documents: %s; "
                     "agencies not on the 3502(5) list only: %s"
                     % (c["si_share_nonpresidential"], c["si_share_other_agencies"]))
        lines.append("")
    lines += ["## eCFR snapshot (descriptive)", ""]
    for t, v in (res.get("ecfr") or {}).items():
        lines.append("- %s: %s" % (t, v))
    lines.append("")
    return "\n".join(lines)
