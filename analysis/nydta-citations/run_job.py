#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Job wrapper for the pre-registered New York Division of Tax Appeals census (census 1.0.0).

Order enforced here:
1. wait until analysis/nydta-citations/PLAN.md and census.py are public in
   munimtechnologies/bar-ai-guidance and the newest committed census.py is identical
   (line endings aside) to the local one;
2. download the AI Hallucination Cases Database CSV (for P6);
3. read the four listing pages (ALJ determinations, ALJ orders, Tribunal decisions, Tribunal
   orders) and build the frame; stop before any document is fetched if a page failed, if the
   frame holds fewer than MIN_FRAME or more than MAX_FRAME documents, or if the parser looks wrong
   (a page without the expected header, too many rows without a DTA number, or without a link);
4. fetch each document (one request at a time, DELAY_S seconds apart), extract text (PDF with
   pypdf, .docx with the standard library), classify, grade. Stop politely after
   MAX_CONSECUTIVE_FAILURES failures in a row.

Texts, excerpts, file names and petitioners' names stay in out/private/ and are never published.
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
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402

REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/nydta-citations"
CSV_URL = "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv"
DELAY_S = 3
MAX_BYTES = 60 * 1024 * 1024
MAX_CONSECUTIVE_FAILURES = 15
MAX_NO_NUMBER = 10
MAX_NO_LINK = 10


def get(url, timeout=120, limit=MAX_BYTES, accept="*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": census.UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit), r.headers.get("Content-Type", "")


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
        time.sleep(30 * (i + 1))
    raise err


def norm_sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url)[0].decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def wait_for_plan(max_minutes, local_sha, step_minutes=5):
    """(plan, code, committed_sha) once both are public and census.py matches; else Nones."""
    deadline = time.time() + max_minutes * 60
    while True:
        try:
            plan = commits_for(DIR + "/PLAN.md")
            code = commits_for(DIR + "/census.py")
            if plan and code:
                committed = get("https://raw.githubusercontent.com/%s/%s/%s/census.py" % (REPO, code[0]["sha"], DIR))[0]
                if norm_sha(committed) == local_sha:
                    return plan[-1], code[0], norm_sha(committed)
                print(census.now(), "newest committed census.py differs from local; waiting", flush=True)
            else:
                print(census.now(), "plan or census.py not public yet", flush=True)
        except Exception as exc:
            print(census.now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None, None
        time.sleep(step_minutes * 60)


def finish(out_dir, status, rc):
    status["finished"] = census.now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def build_frame(log, fetch=None):
    """(docs in the frame, listing info, failed pages). Every listed row is in the frame; rows whose
    first link was already taken by an earlier row are skipped and counted."""
    fetch = fetch or (lambda u: get_retry(u, timeout=180, accept="text/html")[0])
    info = {"pages": []}
    entries, failed = [], 0
    for i, (page, url) in enumerate(census.PAGES):
        if i:
            time.sleep(DELAY_S)
        try:
            body = fetch(url)
        except Exception as exc:
            info["pages"].append({"url": url, "error": str(exc)[:200]})
            log.append("listing failed: %s %s" % (url, str(exc)[:200]))
            failed += 1
            continue
        rows, pinfo = census.parse_listing(body, url, page)
        pinfo.update({"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        info["pages"].append(pinfo)
        entries.extend(rows)
    docs, seen, dup, occ = [], set(), 0, {}
    for e in entries:
        key = e["links"][0] if e["links"] else None
        if key and key in seen:
            dup += 1
            continue
        if key:
            seen.add(key)
        k = census.row_key(e)
        e["row_id"] = census.row_id(e, occ.get(k, 0))
        occ[k] = occ.get(k, 0) + 1
        docs.append(e)
    nums = [d["number"] for d in docs if d["number"]]
    info.update({"entries": len(entries), "in_frame": len(docs), "same_link_skipped": dup,
                 "no_number": sum(1 for d in docs if not d["number"]),
                 "no_year": sum(1 for d in docs if not d["year"]),
                 "no_link_in_frame": sum(1 for d in docs if not d["links"]),
                 "duplicate_numbers": len(nums) - len(set(nums)),
                 "headers_missing": sum(1 for p in info["pages"] if "error" not in p and not p.get("header_found"))})
    log.append("listing: %d entries, %d in frame, %d pages failed" % (len(entries), len(docs), failed))
    return docs, info, failed


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


def docx_text(data):
    """Text of a .docx file (word/document.xml), paragraphs separated by newlines."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")):
        text = text.replace(a, b)
    return text


def kind_of(body):
    head = body.lstrip()[:5]
    if head == b"%PDF-":
        return "pdf"
    if body[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(io.BytesIO(body)) as z:
                if "word/document.xml" in z.namelist():
                    return "docx"
        except Exception:
            return None
    return None


def fetch_document(d):
    """(bytes or None, status, url, kind). Tries the entry's links in order until one is a PDF or .docx."""
    last = "no_link"
    for i, url in enumerate(d.get("links") or []):
        if i:
            time.sleep(DELAY_S)
        try:
            body = get_retry(url, timeout=180)[0]
        except urllib.error.HTTPError as exc:
            last = "http_%s" % exc.code
            continue
        except Exception:
            last = "error"
            continue
        kind = kind_of(body)
        if kind:
            return body, "ok", url, kind
        last = "not_document"
    return None, last, "", None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=120)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "texts"), exist_ok=True)
    status = {"started": census.now(), "census_version": census.VERSION, "log": []}

    with open(os.path.join(HERE, "census.py"), "rb") as fh:
        local_sha = norm_sha(fh.read())
    plan, code, committed_sha = wait_for_plan(args.wait_minutes, local_sha)
    status["census_sha256_local"] = local_sha
    if not plan:
        status["result"] = "stopped: PLAN.md and a matching census.py not public; nothing downloaded"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "census_commit": code, "census_sha256_committed": committed_sha})

    sources = {"plan_commit": plan, "census_commit": code}
    db = None
    try:
        data = get_retry(CSV_URL, timeout=300)[0]
        with open(os.path.join(priv, "download.csv"), "wb") as fh:
            fh.write(data)
        sources["database"] = {"url": CSV_URL, "fetched_at": census.now(), "bytes": len(data),
                               "sha256": hashlib.sha256(data).hexdigest(),
                               "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}
        db = census.db_check(data.decode("utf-8-sig", "replace"))
        status["db_ny_tax_rows"] = len(db["ny_tax_rows"])
    except Exception as exc:
        status["log"].append("database CSV failed: %s" % exc)
        sources["database"] = {"url": CSV_URL, "error": str(exc)}

    docs, info, failed = build_frame(status["log"])
    sources["dta"] = {"pages": [p[1] for p in census.PAGES], "failed": failed, "in_frame": len(docs),
                      "built_at": census.now()}
    with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
        json.dump(sources, fh, indent=1)
    with open(os.path.join(args.out_dir, "listing.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
    with open(os.path.join(priv, "frame.json"), "w", encoding="utf-8") as fh:
        json.dump(docs, fh, indent=1)
    if failed:
        status["result"] = "stopped: %d listing page(s) failed; no document fetched" % failed
        return finish(args.out_dir, status, 5)
    if len(docs) < census.MIN_FRAME:
        status["result"] = "stopped: frame holds %d documents; no document fetched" % len(docs)
        return finish(args.out_dir, status, 6)
    if len(docs) > census.MAX_FRAME:
        status["result"] = "stopped: frame holds %d documents (over %d); no document fetched" % (len(docs),
                                                                                               census.MAX_FRAME)
        return finish(args.out_dir, status, 8)
    if info["headers_missing"] or info["no_number"] > MAX_NO_NUMBER or info["no_link_in_frame"] > MAX_NO_LINK:
        status["result"] = "stopped: parser check failed (%d pages without the header, %d rows without a DTA " \
                           "number, %d rows without a link); no document fetched" % (
                               info["headers_missing"], info["no_number"], info["no_link_in_frame"])
        return finish(args.out_dir, status, 7)
    status["in_frame"] = len(docs)
    print(census.now(), "frame:", len(docs), flush=True)

    excerpts, fails = [], 0
    prog = open(os.path.join(priv, "progress.jsonl"), "w", encoding="utf-8")
    for i, d in enumerate(docs):
        time.sleep(DELAY_S)
        body, d["doc_status"], d["url"], kind = fetch_document(d)
        d["readable"] = False
        d["in_db"] = census.in_db(db, d)
        if body is None:
            if d["doc_status"] != "no_link":
                fails += 1
            prog.write(json.dumps({"row_id": d["row_id"], "doc_status": d["doc_status"]}) + "\n")
            if fails >= MAX_CONSECUTIVE_FAILURES:
                prog.close()
                status["result"] = "stopped: %d documents failed in a row at %d of %d" % (fails, i + 1, len(docs))
                return finish(args.out_dir, status, 9)
            continue
        fails = 0
        d["file_sha256"] = hashlib.sha256(body).hexdigest()
        try:
            text = census.normalize(pdf_text(body) if kind == "pdf" else docx_text(body))
        except Exception as exc:
            text, d["doc_status"] = "", "extract_error"
            print("extract error", d["row_id"], exc, flush=True)
        d.update(census.classify(text))
        d["readable"] = d["doc_status"] == "ok" and d["chars"] >= census.READABLE_CHARS
        if any(d.get(k) for k in census.FLAG_KEYS):
            with open(os.path.join(priv, "texts", "%s.txt" % d["row_id"]), "w", encoding="utf-8") as fh:
                fh.write(text)
        for key, ex in sorted(d.pop("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s | %s | %s\n%s\n" % (d["row_id"], d["page"], d["number"], d.get("year"),
                                                                 key, ex))
        prog.write(json.dumps({k: d.get(k) for k in ("row_id", "number", "doc_status", "chars") + census.FLAG_KEYS})
                   + "\n")
        prog.flush()
        if any(d.get(k) for k in census.FLAG_KEYS) or i % 50 == 0:
            print(census.now(), i + 1, "/", len(docs), d["page"], d["number"], d["doc_status"], d.get("chars"),
                  sorted(k for k in census.FLAG_KEYS if d.get(k)), flush=True)
    prog.close()

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    res = census.grade(docs, db, info)
    res["sources"] = sources
    for fname, payload in (("results.json", json.dumps(res, indent=1, default=str)),
                           ("results.md", census.results_md(res, sources)),
                           ("rows.csv", census.rows_csv(docs))):
        with open(os.path.join(args.out_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(payload)
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    status["counts"] = {k: v for k, v in res["counts"].items() if k != "by_year"}
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
