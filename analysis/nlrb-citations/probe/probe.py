#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""NLRB hand-check and sizing probe (not a census, nothing graded).

1. Fetches the text of Rivas Painting, Inc., 374 NLRB No. 30 (28 Jan 2026), whose footnote 1 the
   Board later cited for a request for review that cited cases that do not exist, so a person can
   read it before it is reported. The decision is fetched from nlrbresearch.com's mirror of the
   NLRB document (the /pdfs/ path is allowed by that site's robots.txt; apps.nlrb.gov/link/ is
   disallowed by its robots.txt, so it is never requested).
2. Reads the first pages of the NLRB's public Board-decisions listing (www.nlrb.gov, allowed by its
   robots.txt), newest first, to size a possible later census: rows by volume and by year, and
   whether rows carry a document id.
3. Fetches up to SAMPLE listed decisions through the same mirror, to see whether it covers them.

One request every DELAY_S seconds. Listing HTML, texts and excerpts go to out/private/ and are
never published; out/ gets counts only.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
DELAY_S = 3
MAX_BYTES = 60 * 1024 * 1024
LISTING = "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?page=%d"
MIRROR = "https://nlrbresearch.com/pdfs/%s.pdf"
MAX_PAGES = 25
STOP_BEFORE_YEAR = 2024
SAMPLE = 3
TARGETS = [("rivas-374-30", "09031d45841abdeb")]

I = re.IGNORECASE
PATTERNS = [
    ("not_exist", r"(?:do|does|did) not exist|non-?existent", I),
    ("fabricat", r"fabricat", I),
    ("fictitious", r"fictitious", I),
    ("hallucinat", r"hallucinat", I),
    ("ghost", r"ghost citation", I),
    ("cannot_locate", r"unable to (?:locate|find)|(?:could|can)not (?:locate|find|be located|be found)", I),
    ("ai_term", r"(?i:artificial intelligence|generative|chatgpt|large language model)|\bAI\b", 0),
    ("referral", r"102\.177|Investigating Officer", I),
    ("footnote1", r"\b1 ?fn\. ?1\b|\bfn\. 1\b", I),
]
COMPILED = [(k, re.compile(p, f)) for k, p, f in PATTERNS]
ROW_SPLIT = re.compile(r"<tr[\s>]", I)
DATE_RX = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")
CITE_RX = re.compile(r"\b(\d{3})\s+NLRB\s+No\.\s*(\d+)", I)
DOC_RX = re.compile(r"document\.aspx/([0-9a-f]{16})", I)
CASE_RX = re.compile(r"/case/(\d{2}-[A-Z]{2}-\d+)")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip()


def find_hits(text, width=300, max_per=12):
    """(counts per pattern key, [(key, offset, excerpt)])."""
    counts, excerpts = {}, []
    for key, rx in COMPILED:
        found = list(rx.finditer(text))
        counts[key] = len(found)
        for m in found[:max_per]:
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            excerpts.append((key, m.start(), text[a:b]))
    return counts, excerpts


def parse_rows(html):
    """One dict per table row that has a citation: year, volume, slip, doc id, case number."""
    rows = []
    for chunk in ROW_SPLIT.split(html)[1:]:
        chunk = chunk.split("</tr", 1)[0]
        cite = CITE_RX.search(chunk)
        if not cite:
            continue
        date = DATE_RX.search(chunk)
        doc = DOC_RX.search(chunk)
        case = CASE_RX.search(chunk)
        rows.append({
            "year": int(date.group(3)) if date else None,
            "volume": int(cite.group(1)),
            "slip": int(cite.group(2)),
            "doc": doc.group(1).lower() if doc else None,
            "case": case.group(1) if case else None,
        })
    return rows


def tally(rows):
    by_volume, by_year = {}, {}
    for r in rows:
        v = str(r["volume"])
        y = str(r["year"]) if r["year"] else "none"
        by_volume[v] = by_volume.get(v, 0) + 1
        by_year[y] = by_year.get(y, 0) + 1
    return {"rows": len(rows), "by_volume": dict(sorted(by_volume.items())),
            "by_year": dict(sorted(by_year.items())),
            "no_doc": sum(1 for r in rows if not r["doc"]),
            "no_case": sum(1 for r in rows if not r["case"]),
            "no_year": sum(1 for r in rows if not r["year"])}


def should_stop(page_rows):
    years = [r["year"] for r in page_rows if r["year"]]
    return not page_rows or (bool(years) and max(years) < STOP_BEFORE_YEAR)


def is_pdf(body):
    return body.lstrip()[:5] == b"%PDF-"


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(MAX_BYTES)


def pdf_text(data):
    from pypdf import PdfReader  # installed by the job's setup step
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages[:200]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return len(reader.pages), "\n".join(parts)


def fetch_doc(doc_id, doc, priv, excerpts):
    row = {"id": doc_id, "doc": doc}
    time.sleep(DELAY_S)
    try:
        body = get(MIRROR % doc)
    except urllib.error.HTTPError as exc:
        row["status"] = "http_%s" % exc.code
        return row
    except Exception as exc:
        row["status"] = "error: %s" % str(exc)[:200]
        return row
    row.update({"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "fetched_at": now()})
    if not is_pdf(body):
        row["status"] = "not_pdf"
        return row
    try:
        pages, raw = pdf_text(body)
    except Exception as exc:
        row["status"] = "extract_error: %s" % str(exc)[:200]
        return row
    text = normalize(raw)
    counts, ex = find_hits(text)
    row.update({"status": "ok", "pages": pages, "chars": len(text), "counts": counts})
    with open(os.path.join(priv, "texts", doc_id + ".txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    for key, off, snippet in ex:
        excerpts.append("== %s | %s | @%d\n%s\n" % (doc_id, key, off, snippet))
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "texts"), exist_ok=True)
    status = {"started": now(), "log": []}

    all_rows, pages = [], []
    for n in range(MAX_PAGES):
        time.sleep(DELAY_S)
        url = LISTING % n
        try:
            body = get(url)
        except Exception as exc:
            status["log"].append("listing page %d failed: %s" % (n, str(exc)[:200]))
            break
        html = body.decode("utf-8", "replace")
        with open(os.path.join(priv, "listing-%02d.html" % n), "w", encoding="utf-8") as fh:
            fh.write(html)
        page_rows = parse_rows(html)
        pages.append({"page": n, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                      "rows": len(page_rows)})
        all_rows.extend(page_rows)
        print(now(), "page", n, len(page_rows), flush=True)
        if should_stop(page_rows):
            break
    with open(os.path.join(priv, "listing_rows.json"), "w", encoding="utf-8") as fh:
        json.dump(all_rows, fh, indent=1)
    listing = {"pages": pages, "tally": tally(all_rows), "fetched_at": now()}
    rivas_listed = [r for r in all_rows if r["volume"] == 374 and r["slip"] == 30]
    listing["rivas_row"] = rivas_listed[0] if rivas_listed else None
    with open(os.path.join(args.out_dir, "listing.json"), "w", encoding="utf-8") as fh:
        json.dump(listing, fh, indent=1)

    docs = list(TARGETS)
    have = {d for _, d in docs}
    for r in all_rows:
        if len(docs) >= len(TARGETS) + SAMPLE:
            break
        if r["doc"] and r["doc"] not in have:
            docs.append(("sample-%d-%d" % (r["volume"], r["slip"]), r["doc"]))
            have.add(r["doc"])

    rows, excerpts = [], []
    for doc_id, doc in docs:
        row = fetch_doc(doc_id, doc, priv, excerpts)
        rows.append(row)
        print(now(), doc_id, row.get("status"), flush=True)
    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    public = [{k: r.get(k) for k in ("id", "status", "bytes", "sha256", "pages", "chars", "counts")} for r in rows]
    with open(os.path.join(args.out_dir, "docs_public.json"), "w", encoding="utf-8") as fh:
        json.dump(public, fh, indent=1)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    status.update({"finished": now(), "listing_rows": len(all_rows), "docs": len(rows), "docs_ok": ok})
    with open(os.path.join(args.out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1)
    print(json.dumps(status))
    return 0 if (ok or all_rows) else 5


if __name__ == "__main__":
    sys.exit(main())
