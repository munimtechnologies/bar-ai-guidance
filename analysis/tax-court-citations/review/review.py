#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Post-grading excerpt review for the U.S. Tax Court fabricated-citation census 1.0.0.

The census is graded and its verdicts do not change. Its plan promises that the agents report
documents the frozen patterns missed. This job helps a person do that: it re-reads every document
in the published frame (results/rows.csv in munimtechnologies/bar-ai-guidance) and writes, to
out/private/, every passage that matches a deliberately broad review pattern, so a person can read
them. It also looks up one opinion that a frame document cites near an AI passage (Tellock,
T.C. Memo. 2026-59). Nothing here is graded and texts stay private.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
API = "https://public-api-green.dawson.ustaxcourt.gov/public-api"
ROWS_URL = ("https://raw.githubusercontent.com/munimtechnologies/bar-ai-guidance/main/"
            "analysis/tax-court-citations/results/rows.csv")
DELAY_S = 3
MAX_BYTES = 40 * 1024 * 1024
WIDTH = 300
MAX_HITS_PER_DOC = 40
EXTRA_SEARCHES = (("opinion", "Tellock"),)

REVIEW = re.compile(
    r"\b(?:do(?:es)?|did)\s+not\s+exist\b"
    r"|\bnon-?existent\b|\bfictitious\b|\bfabricat\w*|\bbogus\b|\bfake\b|\bhallucinat\w*"
    r"|\bChatGPT\b|\bchatbots?\b|\bGemini\b|\bClaude\b|\bCopilot\b|\bartificial[- ]intelligence\b"
    r"|(?-i:\bA[Il]\b)|\blarge language models?\b"
    r"|\b(?:unable|could\s+not|cannot|can\s*not)\s+(?:to\s+)?(?:locate|find)\b"
    r"|\bno\s+such\s+(?:case|opinion|decision|authority)\b"
    r"|\bmisquot\w*|\bmisrepresent\w*\s+(?:the\s+)?(?:holding|case|authorit)", re.I)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get(url, timeout=120, accept="*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(MAX_BYTES)


def get_retry(url, tries=3, timeout=120, accept="*/*"):
    err = None
    for i in range(tries):
        try:
            return get(url, timeout=timeout, accept=accept)
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 403, 404, 410):
                raise
            err = exc
        except Exception as exc:
            err = exc
        time.sleep(20 * (i + 1))
    raise err


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def parse_rows(csv_text):
    """[(docket_entry_id, first docket number, date, kind)] from the published rows.csv."""
    out = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        eid = (row.get("docket_entry_id") or "").strip()
        dockets = (row.get("dockets") or "").strip()
        if not eid or not dockets:
            continue
        out.append((eid, dockets.split(";")[0], (row.get("date") or "").strip(), (row.get("kind") or "").strip()))
    return out


def hits(text, width=WIDTH, cap=MAX_HITS_PER_DOC):
    """Merged context windows around every review-pattern match: [(start, end, terms)]."""
    spans = []
    for m in REVIEW.finditer(text):
        a, b = max(0, m.start() - width), min(len(text), m.end() + width)
        term = m.group(0).lower()
        if spans and a <= spans[-1][1]:
            s = spans[-1]
            spans[-1] = (s[0], max(s[1], b), s[2] if term in s[2] else s[2] + [term])
        else:
            spans.append((a, b, [term]))
    return spans[:cap]


def search_url(kind, keyword):
    url = "%s/%s-search?keyword=%s&dateRange=allDates" % (API, kind, urllib.parse.quote(keyword, safe=""))
    if kind == "opinion":
        url += "&opinionTypes=MOP,OST,SOP,TCOP"
    return url


def download_url(docket_number, docket_entry_id):
    return "%s/%s/%s/public-document-download-url" % (API, docket_number, docket_entry_id)


def pdf_text(data):
    from pypdf import PdfReader  # installed by the job's setup step
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages[:300]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def fetch_pdf(docket_number, eid):
    try:
        meta = json.loads(get_retry(download_url(docket_number, eid), accept="application/json").decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return None, "url_http_%s" % exc.code
    except Exception:
        return None, "url_error"
    link = meta.get("url") if isinstance(meta, dict) else None
    if not link:
        return None, "no_url"
    try:
        return get_retry(link, timeout=180), "ok"
    except urllib.error.HTTPError as exc:
        return None, "pdf_http_%s" % exc.code
    except Exception:
        return None, "pdf_error"


def wait_for_rows(max_minutes, step_minutes=5):
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            return get(ROWS_URL).decode("utf-8-sig")
        except Exception as exc:
            print(now(), "rows.csv not public yet:", exc, flush=True)
        if time.time() > deadline:
            return None
        time.sleep(step_minutes * 60)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=120)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "texts"), exist_ok=True)
    status = {"started": now(), "log": []}

    rows_text = wait_for_rows(args.wait_minutes)
    if rows_text is None:
        status["result"] = "stopped: published rows.csv not reachable"
        return finish(args.out_dir, status, 3)
    targets = parse_rows(rows_text)
    status["rows_sha256"] = hashlib.sha256(rows_text.encode("utf-8")).hexdigest()
    status["targets"] = len(targets)

    extra = []
    for kind, kw in EXTRA_SEARCHES:
        time.sleep(DELAY_S)
        try:
            data = json.loads(get_retry(search_url(kind, kw), accept="application/json").decode("utf-8"))
            for x in data.get("results") or []:
                if (x.get("filingDate") or "")[:4] == "2026" and x.get("docketEntryId") and x.get("docketNumber"):
                    extra.append((x["docketEntryId"], x["docketNumber"], x["filingDate"][:10], "extra:" + kw))
        except Exception as exc:
            status["log"].append("search %s %s failed: %s" % (kind, kw, str(exc)[:200]))
    seen = {t[0] for t in targets}
    targets += [t for t in extra if t[0] not in seen]
    status["extra"] = len(targets) - status["targets"]

    out_lines, summary = [], []
    for eid, docket, date, kind in targets:
        time.sleep(DELAY_S)
        body, st = fetch_pdf(docket, eid)
        rec = {"docket_entry_id": eid, "docket": docket, "date": date, "kind": kind, "status": st}
        if body is not None:
            try:
                text = normalize(pdf_text(body))
            except Exception:
                text, rec["status"] = "", "extract_error"
            spans = hits(text)
            rec["chars"] = len(text)
            rec["hits"] = len(spans)
            rec["terms"] = sorted({t for s in spans for t in s[2]})
            if spans:
                with open(os.path.join(priv, "texts", "%s.txt" % eid), "w", encoding="utf-8") as fh:
                    fh.write(text)
            for a, b, terms in spans:
                out_lines.append("== %s | %s | %s | %s\n%s\n" % (docket, date, kind, ",".join(terms), text[a:b]))
        summary.append(rec)
        print(now(), docket, date, rec["status"], rec.get("hits"), rec.get("terms"), flush=True)

    with open(os.path.join(priv, "review_excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines))
    with open(os.path.join(priv, "review_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    status["result"] = "done"
    status["read"] = sum(1 for r in summary if r["status"] == "ok")
    status["with_hits"] = sum(1 for r in summary if r.get("hits"))
    return finish(args.out_dir, status, 0)


def finish(out_dir, status, rc):
    status["finished"] = now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1)
    print(json.dumps(status)[:3000])
    return rc


if __name__ == "__main__":
    sys.exit(main())
