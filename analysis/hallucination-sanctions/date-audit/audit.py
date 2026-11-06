#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Date audit (version 1.0.0) for the graded hallucination-sanctions study.

Question: for the US decisions involving a lawyer in the AI Hallucination Cases Database
(Damien Charlotin, CC BY 4.0), does the recorded decision date match the hosted decision
document, and would the study's graded predictions change if misdated rows were moved?

Rules are frozen in analysis/hallucination-sanctions/date-audit/PLAN.md before any decision
document is fetched. Standard library plus pypdf (text extraction only, no OCR).
"""
from __future__ import annotations

import collections
import csv
import datetime
import io
import json
import os
import re
import urllib.parse

VERSION = "1.0.0"
BASE = "https://www.damiencharlotin.com"
WINDOW_DAYS = 7          # a date within 7 days of another counts as the same event
MIN_TEXT = 200           # fewer extracted characters than this = no usable text layer
MAX_PAGES = 80
SNIPPET = 160

MONTH_NAMES = {
    1: ("january", "jan"), 2: ("february", "feb"), 3: ("march", "mar"), 4: ("april", "apr"),
    5: ("may",), 6: ("june", "jun"), 7: ("july", "jul"), 8: ("august", "aug"),
    9: ("september", "sept", "sep"), 10: ("october", "oct"), 11: ("november", "nov"),
    12: ("december", "dec"),
}

_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
_FNAME = re.compile(r"_(\d{2})-(\d{2})-(\d{4})\.pdf$", re.I)
_ECF = re.compile(r"(?:filed|entered)\s*:?\s*(?:on\s*[a-z]{2,6}\s*docket\s*)?"
                  r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4}|\d{2})(?!\d)")


# ---------------------------------------------------------------- dates

def parse_iso(raw):
    m = _ISO.match((raw or "").strip())
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def period_of(d):
    if d is None:
        return ""
    return "%dH%d" % (d.year, 1 if d.month <= 6 else 2)


def norm_text(t):
    t = (t or "").lower().replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", t)


def date_patterns(d):
    """Regexes that match date d written in the common US forms."""
    mon = "(?:%s)" % "|".join(MONTH_NAMES[d.month])
    D = r"0?%d(?!\d)" % d.day
    Y = r"%d(?!\d)" % d.year
    YY = r"%02d(?!\d)" % (d.year % 100)
    ORD = r"(?:st|nd|rd|th)?"
    S = r"\s*"
    return [
        # October 27, 2026 / Oct. 27th 2026
        re.compile(r"(?<![a-z])" + mon + r"\.?" + S + D + ORD + S + r",?" + S + Y),
        # 27 October 2026 / 27th day of October, 2026
        re.compile(r"(?<!\d)" + D + ORD + S + r"(?:day" + S + r"of" + S + r")?" + mon + r"\.?" + S + r",?" + S + Y),
        # 10/27/2026, 10/27/26, 10-27-2026, 10.27.26
        re.compile(r"(?<!\d)0?%d" % d.month + S + r"[/.\-]" + S + D + S + r"[/.\-]" + S + r"(?:" + Y + r"|" + YY + r")"),
        # 2026-10-27
        re.compile(r"(?<!\d)%d-0?%d-" % (d.year, d.month) + D),
    ]


def find_date(text_norm, d):
    """First match span of date d in normalised text, or None."""
    if d is None:
        return None
    for p in date_patterns(d):
        m = p.search(text_norm)
        if m:
            return m.span()
    return None


def ecf_date(text_norm):
    """Most frequent CM/ECF-style 'Filed MM/DD/YY' or 'Entered on ... Docket MM/DD/YYYY' date.

    Returns (date, count); ties go to the latest date."""
    counts = collections.Counter()
    for m in _ECF.finditer(text_norm):
        mm, dd, yy = int(m.group(1)), int(m.group(2)), m.group(3)
        y = int(yy) + 2000 if len(yy) == 2 else int(yy)
        try:
            counts[datetime.date(y, mm, dd)] += 1
        except ValueError:
            continue
    if not counts:
        return None, 0
    best = max(counts.items(), key=lambda kv: (kv[1], kv[0]))
    return best[0], best[1]


def filename_date(source):
    m = _FNAME.search(source or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def far(a, b):
    """True if both dates exist and differ by more than WINDOW_DAYS, or a exists and b does not."""
    if a is None:
        return False
    if b is None:
        return True
    return abs((a - b).days) > WINDOW_DAYS


def correct(recorded, recorded_found, ecf, fname, fname_found):
    """Return {'c1': (date, rule), 'c2': (date, rule)} under the two frozen correction rules.

    C1 (document-date first): an ECF header date more than 7 days from the recorded date wins;
       otherwise, if the recorded date is not in the text, a file-name date that is in the text
       and more than 7 days away wins; otherwise the recorded date is kept.
    C2 (conservative): only rows whose recorded date is NOT in the text (or is missing) are
       corrected, ECF date first, then a file-name date found in the text, each only if more
       than 7 days away.
    """
    # C1
    if far(ecf, recorded):
        c1 = (ecf, "ecf")
    elif not recorded_found and fname_found and far(fname, recorded):
        c1 = (fname, "filename")
    else:
        c1 = (recorded, "kept")
    # C2
    if recorded_found:
        c2 = (recorded, "kept")
    elif far(ecf, recorded):
        c2 = (ecf, "ecf")
    elif fname_found and far(fname, recorded):
        c2 = (fname, "filename")
    else:
        c2 = (recorded, "kept")
    return {"c1": c1, "c2": c2}


# ---------------------------------------------------------------- documents

def doc_url(source):
    s = (source or "").strip()
    if not (s.startswith("/documents/") and s.lower().endswith(".pdf")):
        return None
    return BASE + urllib.parse.quote(s, safe="/%")


def pdf_text(data, max_pages=MAX_PAGES):
    """(text, pages, error) from PDF bytes using pypdf; no OCR."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - the job installs pypdf
        return "", 0, "pypdf missing: %s" % exc
    try:
        reader = PdfReader(io.BytesIO(data))
        n = len(reader.pages)
        parts = []
        for i in range(min(n, max_pages)):
            try:
                parts.append(reader.pages[i].extract_text() or "")
            except Exception as exc:  # one bad page should not sink the document
                parts.append("")
        return "\n".join(parts), n, None
    except Exception as exc:
        return "", 0, "%s: %s" % (type(exc).__name__, str(exc)[:200])


def snippet(text_norm, span):
    if not span:
        return ""
    a = max(0, span[0] - SNIPPET // 2)
    return text_norm[a:span[1] + SNIPPET // 2]


def audit_row(case_id, recorded_raw, source, fetch):
    """Audit one row. fetch(url) -> bytes (or raises). Returns a dict."""
    recorded = parse_iso(recorded_raw)
    fname = filename_date(source)
    out = {"case_id": case_id, "recorded_date": recorded_raw or "", "recorded_period": period_of(recorded),
           "source": source or "", "filename_date": fname.isoformat() if fname else "",
           "status": "", "pages": 0, "text_chars": 0, "recorded_found": "", "ecf_date": "", "ecf_count": 0,
           "filename_found": "", "c1_date": "", "c1_rule": "", "c1_period": "", "c2_date": "", "c2_rule": "",
           "c2_period": "", "snip_recorded": "", "snip_ecf": "", "snip_filename": "", "error": ""}
    url = doc_url(source)
    if url is None:
        out["status"] = "no_hosted_pdf"
    else:
        try:
            data = fetch(url)
        except Exception as exc:
            out["status"] = "fetch_failed"
            out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
            data = None
        if data is not None:
            text, pages, err = pdf_text(data)
            t = norm_text(text)
            out["pages"], out["text_chars"] = pages, len(t)
            if err:
                out["status"], out["error"] = "pdf_error", err
            elif len(t) < MIN_TEXT:
                out["status"] = "no_text"
            else:
                out["status"] = "text"
                rspan = find_date(t, recorded)
                ecf, ecf_n = ecf_date(t)
                fspan = find_date(t, fname)
                out["recorded_found"] = bool(rspan) if recorded else ""
                out["ecf_date"] = ecf.isoformat() if ecf else ""
                out["ecf_count"] = ecf_n
                out["filename_found"] = bool(fspan) if fname else ""
                out["snip_recorded"] = snippet(t, rspan)
                if ecf:
                    out["snip_ecf"] = snippet(t, find_date(t, ecf))
                out["snip_filename"] = snippet(t, fspan)
                cc = correct(recorded, bool(rspan), ecf, fname, bool(fspan))
                for k in ("c1", "c2"):
                    d, rule = cc[k]
                    out[k + "_date"] = d.isoformat() if d else ""
                    out[k + "_rule"] = rule
                    out[k + "_period"] = period_of(d)
    if out["status"] != "text":
        for k in ("c1", "c2"):
            out[k + "_date"] = recorded_raw or ""
            out[k + "_rule"] = "kept_unaudited"
            out[k + "_period"] = period_of(recorded)
    return out


# ---------------------------------------------------------------- regrade helpers

def pseudo_raw(us_row, date_override=None):
    """Rebuild a database-style row from a published us_rows.csv row so that the frozen
    analyze.classify() reproduces the graded record."""
    def flag(v):
        v = (v or "").strip()
        return "Yes" if v == "True" else ("No" if v == "False" else "")
    return {
        "case_id": us_row["case_id"],
        "State(s)": "USA",
        "Date": us_row["date"] if date_override is None else date_override,
        "Party(ies)": us_row["parties"],
        "Monetary Penalty": us_row["penalty_raw"],
        "Professional Sanction": "Yes" if us_row["prof"] == "True" else "No",
        "Alleged": flag(us_row["alleged"]),
    }


def summarise(rows):
    """Counts and the D1-D3 statistics over audited rows (list of audit_row dicts)."""
    st = collections.Counter(r["status"] for r in rows)
    text = [r for r in rows if r["status"] == "text"]
    dated = [r for r in text if r["recorded_date"]]
    found = [r for r in dated if r["recorded_found"] is True]
    with_ecf = [r for r in dated if r["ecf_date"]]
    ecf_close = [r for r in with_ecf if not far(parse_iso(r["ecf_date"]), parse_iso(r["recorded_date"]))]
    ecf_far_but_found = [r for r in with_ecf if r not in ecf_close and r["recorded_found"] is True]

    def moved(key):
        return [r for r in text if r[key + "_period"] != r["recorded_period"]]

    def flows(key):
        c = collections.Counter("%s -> %s" % (r["recorded_period"] or "(none)", r[key + "_period"] or "(none)")
                                for r in moved(key))
        return dict(sorted(c.items()))

    def share(a, b):
        return round(len(a) / len(b), 4) if b else None

    return {
        "n_rows": len(rows),
        "status_counts": dict(sorted(st.items())),
        "n_text": len(text),
        "D1": {"n": len(dated), "found": len(found), "share": share(found, dated)},
        "D2": {"n": len(with_ecf), "within_7_days": len(ecf_close), "share": share(ecf_close, with_ecf),
               "far_but_recorded_date_in_text": len(ecf_far_but_found)},
        "D3": {"n": len(text), "moved_c1": len(moved("c1")), "share_c1": share(moved("c1"), text),
               "moved_c2": len(moved("c2")), "share_c2": share(moved("c2"), text),
               "flows_c1": flows("c1"), "flows_c2": flows("c2")},
        "filename": {
            "n_with_filename_date": sum(1 for r in rows if r["filename_date"]),
            "n_filename_differs_gt7": sum(1 for r in rows if r["filename_date"] and
                                          far(parse_iso(r["filename_date"]), parse_iso(r["recorded_date"]))),
        },
    }


ROW_FIELDS = ("case_id", "recorded_date", "recorded_period", "date_now", "source", "status", "pages", "text_chars",
              "recorded_found", "ecf_date", "ecf_count", "filename_date", "filename_found", "c1_date", "c1_rule",
              "c1_period", "c2_date", "c2_rule", "c2_period", "error")


def write_rows(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(ROW_FIELDS)
        for r in rows:
            w.writerow([r.get(f, "") for f in ROW_FIELDS])


def write_review(path, rows):
    """Snippets for every row whose date is in doubt, for a human reading afterwards."""
    lines = ["# Rows to read by hand (recorded date not found, or a correction moved the half-year)", ""]
    for r in rows:
        doubt = (r["status"] == "text" and (r["recorded_found"] is not True or r["c1_period"] != r["recorded_period"]
                                            or r["c2_period"] != r["recorded_period"]))
        if not doubt:
            continue
        lines.append("## case %s: recorded %s; ECF %s (x%s); file name %s (found %s); C1 %s (%s); C2 %s (%s)" % (
            r["case_id"], r["recorded_date"] or "(none)", r["ecf_date"] or "-", r["ecf_count"],
            r["filename_date"] or "-", r["filename_found"], r["c1_date"] or "-", r["c1_rule"],
            r["c2_date"] or "-", r["c2_rule"]))
        lines.append("")
        lines.append("source: %s" % (BASE + r["source"] if r["source"].startswith("/") else r["source"]))
        for k in ("snip_recorded", "snip_ecf", "snip_filename"):
            if r.get(k):
                lines.append("- %s: \"%s\"" % (k[5:], r[k].replace("\"", "'")))
        lines.append("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
