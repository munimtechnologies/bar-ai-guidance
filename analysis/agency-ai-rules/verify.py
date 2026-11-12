#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Source check for data/agency_ai_rules.json (not a census, nothing graded).

Fetches each administrative tribunal's own copy of the AI instruments listed in the dataset
(a short fixed list), extracts the text (PDF or HTML) and keeps short excerpts around fixed
phrases (AI terms, disclosure, certification, verification, sanctions, rule citations) so a
person can confirm each dataset field against the issuer's own words before the entry's
source_check is upgraded. One request every DELAY_S seconds, at most MAX_DOCS documents.

Texts and excerpts go to out/private/ and are never published; out/docs_public.json keeps
only status, size, SHA-256 and phrase counts.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
DELAY_S = 10
MAX_DOCS = 20
MAX_BYTES = 60 * 1024 * 1024
MAX_PAGES = 400
DOCS = [
    ("us-dol-oalj-order-2026-mis-00004",
     "https://www.dol.gov/sites/dolgov/files/OALJ/OFFICE_OF_ADMINISTRA_v_Standing_Order_on_AI_2026MIS00004_"
     "(JUL_08_2026)_091853_CADEC_SD_202678942.pdf"),
    ("us-dol-oalj-home", "https://www.dol.gov/agencies/oalj"),
    ("us-dol-oalj-notices", "https://www.dol.gov/agencies/oalj/PUBLIC/RULES_OF_PRACTICE/REFERENCES/"
                            "REFERENCE_WORKS/Notices"),
    ("us-dol-arb-si-page", "https://www.dol.gov/agencies/arb/resources/si"),
    ("us-eoir-pm-25-40", "https://www.justice.gov/eoir/media/1410621/dl?inline="),
    ("us-ocaho-wallcon-2025", "https://www.justice.gov/d9/2025-01/1630.pdf"),
    ("us-ftc-oalj-order-2026-01-08", "https://www.ftc.gov/system/files/ftc_gov/pdf/"
                                     "614613.2026.01.08_order_on_further_review_filings.pdf"),
    ("us-uspto-89fr25609", "https://www.federalregister.gov/documents/full_text/html/2024/04/11/2024-07629.html"),
    ("us-tx-soah-calj-advisory-2025",
     "https://www.soah.texas.gov/sites/default/files/2025-10/SOAH_CALJ_Advisory_AI_20251009.pdf"),
    ("us-id-oah-policy-25-1", "https://oah.idaho.gov/wp-content/uploads/2025/09/OAH-AI-Guidelines.pdf"),
    ("us-id-bulletin-2026-07", "https://proddfmmainsa.blob.core.windows.net/dfm-admin-website/bulletin/2026/07.pdf"),
    ("us-id-hr031-2026", "https://legislature.idaho.gov/wp-content/uploads/sessioninfo/2026/legislation/HR031.pdf"),
    ("us-mt-dor-mar-2026-169-2", "https://revenue.mt.gov/news/rules-hearing/MAR-Notice-2026-169-2"),
    ("us-mt-dor-mar-2026-169-1", "https://revenue.mt.gov/news/rules-hearing/MAR-Notice-2026-169-1"),
    ("us-ga-sbwc-ai-standing-order-2026",
     "https://sbwc.georgia.gov/document/publication/standing-order-ai-policy-procedure/download"),
    ("us-mn-puc-ai-policy", "https://mn.gov/puc/about-us/ai-policy/"),
    ("us-ma-cerb-ai-statement-2026",
     "https://www.mass.gov/doc/commonwealth-employment-relations-board-statement-regarding-the-use-of-"
     "artificial-intelligence/download"),
]
I = re.IGNORECASE
PATTERNS = [
    ("ai_term", r"(?i:artificial intelligence|generative|chatgpt|large language model)|\bAI\b|\bGenAI\b", 0),
    ("super_intel", r"super\s*intelligence|\bSI\b", 0),
    ("disclos", r"disclos", I),
    ("certif", r"certif", I),
    ("verif", r"verif", I),
    ("fictitious", r"fictitious|fabricat|hallucinat|do(?:es)? not exist", I),
    ("sanction", r"sanction|stricken|strike|dismiss", I),
    ("cfr", r"\b\d+\s+C\.?F\.?R\.?\s*(?:§|Part|section)?\s*\d+[\d.()a-z]*", I),
    ("state_rule", r"\b(?:155\.303|7829\.0250|42\.2\.6\d\d|62\.01\.01|SCR\s*128|Rule\s+0?1[12])\b", I),
    ("evidence", r"evidence", I),
    ("dated", r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
              r"\s+\d{1,2},\s+20\d\d", 0),
]
COMPILED = [(k, re.compile(p, f)) for k, p, f in PATTERNS]
TAG_RX = re.compile(r"<(script|style)\b.*?</\1>|<[^>]+>", re.IGNORECASE | re.DOTALL)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip()


def html_to_text(body_text):
    return normalize(html.unescape(TAG_RX.sub(" ", body_text or "")))


def find_hits(text, width=300, max_per=10):
    """(counts per pattern key, [(key, offset, excerpt)])."""
    counts, excerpts = {}, []
    for key, rx in COMPILED:
        found = list(rx.finditer(text))
        counts[key] = len(found)
        for m in found[:max_per]:
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            excerpts.append((key, m.start(), text[a:b]))
    return counts, excerpts


def is_pdf(body):
    return body.lstrip()[:5] == b"%PDF-"


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read(MAX_BYTES)


def get_retry(url, tries=2):
    err = None
    for i in range(tries):
        try:
            return get(url)
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 401, 403, 404, 410):
                raise
            err = exc
        except Exception as exc:
            err = exc
        time.sleep(20 * (i + 1))
    raise err


def pdf_text(data):
    from pypdf import PdfReader  # installed by the job's setup step
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages[:MAX_PAGES]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return len(reader.pages), "\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "texts"), exist_ok=True)
    status = {"started": now()}

    rows, excerpts, ok = [], [], 0
    for doc_id, url in DOCS[:MAX_DOCS]:
        time.sleep(DELAY_S)
        row = {"id": doc_id, "url": url}
        try:
            final_url, body = get_retry(url)
        except urllib.error.HTTPError as exc:
            row["status"] = "http_%s" % exc.code
            rows.append(row)
            print(now(), doc_id, row["status"], flush=True)
            continue
        except Exception as exc:
            row["status"] = "error: %s" % str(exc)[:200]
            rows.append(row)
            print(now(), doc_id, row["status"], flush=True)
            continue
        row.update({"final_url": final_url, "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(), "fetched_at": now()})
        try:
            if is_pdf(body):
                pages, raw = pdf_text(body)
                row.update({"type": "pdf", "pages": pages})
                text = normalize(raw)
            else:
                row["type"] = "html"
                text = html_to_text(body.decode("utf-8", "replace"))
        except Exception as exc:
            row["status"] = "extract_error: %s" % str(exc)[:200]
            rows.append(row)
            continue
        counts, ex = find_hits(text)
        row.update({"status": "ok", "chars": len(text), "counts": counts})
        ok += 1
        with open(os.path.join(priv, "texts", doc_id + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(text)
        for key, off, snippet in ex:
            excerpts.append("== %s | %s | @%d\n%s\n" % (doc_id, key, off, snippet))
        rows.append(row)
        print(now(), doc_id, "ok", row.get("type"), len(text), {k: v for k, v in counts.items() if v}, flush=True)

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(priv, "docs.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)
    public = [{k: r.get(k) for k in ("id", "status", "type", "bytes", "sha256", "pages", "chars", "counts")}
              for r in rows]
    with open(os.path.join(args.out_dir, "docs_public.json"), "w", encoding="utf-8") as fh:
        json.dump(public, fh, indent=1)
    status.update({"finished": now(), "docs": len(rows), "docs_ok": ok})
    with open(os.path.join(args.out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1)
    print(json.dumps(status))
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
