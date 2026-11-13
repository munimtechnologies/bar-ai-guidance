#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Addendum 1 to the USPTO OED discipline-archive census (census 1.0.0): OCR of the 27 decisions
that census 1.0.0 could not read because their PDFs carry no usable text layer.

Order enforced here:
1. wait until ADDENDUM-1.md and this file are public in munimtechnologies/bar-ai-guidance under
   analysis/uspto-oed-citations/ocr/ and the newest committed copy of this file matches the local one;
2. download census.py exactly as frozen in commit 200007c (SHA-256 checked) and use its listing
   parser, row ids and text patterns unchanged;
3. read the OED reading-room listing again and pick the 27 rows by their published row ids; stop
   before fetching any decision if fewer than MIN_FOUND are found;
4. fetch each PDF (one request at a time, DELAY_S seconds apart), compare its SHA-256 with the one
   census 1.0.0 recorded, measure poppler's text layer, OCR every page with Tesseract, classify,
   grade the eight addendum predictions.

Texts, excerpts, file names and respondents' names stay in out/private/ and are never published.
Information about public decisions of a federal agency, not legal advice.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

VERSION = "1.0.0"
REPO = "munimtechnologies/bar-ai-guidance"
DIR = "analysis/uspto-oed-citations/ocr"
CENSUS_COMMIT = "200007c20495c85f66c938e9b023e784953c9b0f"
CENSUS_PATH = "analysis/uspto-oed-citations/census.py"
CENSUS_SHA = "dfdf5dc3d74db5f6ea9b65fb2534e0a1fe12eb97b2a58883a86cecc6ab386053"  # CRLF -> LF first
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
DELAY_S = 3
MAX_BYTES = 60 * 1024 * 1024
MAX_PAGES = 60
DPI = 300
READABLE_CHARS = 300
MIN_FOUND = 25
MITCHELL = "D2026-16"

# The 27 rows census 1.0.0 recorded as unreadable: row id -> (proceeding, date, first 16 hex of the PDF's SHA-256)
TARGETS = {
    "ff5c878034fc": ("D2023-03", "2023-03-29", "a3fca6aed1d4bb3f"),
    "26035e73d3e4": ("D2020-17", "2023-04-11", "fe19c9840f9d6733"),
    "a965a9b9f94d": ("D2023-10", "2023-05-01", "018c07aa2f84e60a"),
    "a8bd88e09deb": ("D2023-14", "2023-05-03", "7bee81247c202504"),
    "22c8d8978700": ("D2023-09", "2023-05-15", "1e05a33f5a71b12f"),
    "bd5674591ab6": ("D2023-28", "2023-06-23", "fd0a0aa890034a68"),
    "30dcfe050838": ("D2020-10, D2024-15", "2024-08-13", "9d150968a937e9cd"),
    "c066e34d1a9d": ("D2019-38", "2024-09-05", "e14c23968892e9fd"),
    "720d419d0d7b": ("D2025-19", "2025-05-14", "c07e3a1c67034626"),
    "24a3e6baa16c": ("Tech_18", "2025-06-13", "3c7fdbca21dc99e8"),
    "0d518b6975ec": ("D2025-23", "2025-07-07", "dbb5bbd5a460f9f0"),
    "933eb4dbc7b6": ("D2025-33", "2026-01-06", "60eaf1bfdee4a2f2"),
    "661558f2d245": ("D2026-07", "2026-01-29", "fc1b1461f6b16308"),
    "75389a4ec864": ("D2026-06", "2026-02-03", "87dff268bf86610a"),
    "c5a537937df0": ("D2026-09", "2026-02-11", "555b2deb743aa9be"),
    "16ea120fe085": ("D2025-31", "2026-03-09", "509275d4bb64daa0"),
    "1e4e655ab136": ("D2026-13", "2026-03-13", "71551102d920b436"),
    "32ed1f246f00": ("D2025-22", "2026-04-08", "4f02342ab42f9919"),
    "75be47fbbc6d": ("D2026-23", "2026-04-14", "35f9ef7546fdd68c"),
    "d215dc2869ef": ("D2025-29", "2026-05-07", "907299e4ea2d9d5e"),
    "c41f0769bf5c": ("D2026-20", "2026-05-07", "2e4c769e0d3dcdb1"),
    "6c336b3cf58d": ("D2025-32", "2026-05-20", "f76f75553848267d"),
    "f031cc4e570e": ("D2026-8", "2026-05-26", "57311c3db0f20159"),
    "2f0c638e3a44": ("D2026-21", "2026-06-05", "935c18fe44f8d0d1"),
    "0c22fb2353a0": ("D2026-33", "2026-06-16", "73f763cfeccb765d"),
    "e3c6130e4aa4": ("D2026-32", "2026-07-07", "6ee8b40e237fe112"),
    "d2be0a280703": ("D2026-16", "2026-07-27", "a7f252b12617328d"),
}

# --- OCR-tolerant rule and guidance patterns (new in this addendum; census 1.0.0's stay as frozen) ---
_ONE = r"[1Il|]"
_SEC = r"(?<![\w.])" + _ONE + r"\s?" + _ONE + r"\s?\.\s?"
TOL_11_18 = re.compile(_SEC + _ONE + r"\s?8(?![\w])")
TOL_11_101 = re.compile(_SEC + _ONE + r"\s?[0Oo]\s?" + _ONE + r"(?![\w])")
TOL_11_804 = re.compile(_SEC + r"8\s?[0Oo]\s?4(?![\w])")
TOL_GUIDANCE = re.compile(r"\b8\s?9\s+(?:Fed\.?\s*Reg\.?|FR)\s+2\s?5\s?,?\s?6\s?(?:0\s?9|1\s?\d)\b"
                          r"|\bGuidance\s+on\s+(?:the\s+)?Use\s+of\s+Artificial[- ]Intelligence\b", re.I)
TOL_KEYS = ("r11_18_tol", "r11_101_tol", "r11_804_tol", "guidance_tol")
CENSUS_FLAGS = ("fake_cite", "ai_mention", "ai_citation", "guidance", "r11_18", "r11_101", "r11_804")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def collapse(text):
    return re.sub(r"\s+", " ", text or "").strip()


def tolerant_flags(text):
    t = collapse(text)
    return {"r11_18_tol": bool(TOL_11_18.search(t)), "r11_101_tol": bool(TOL_11_101.search(t)),
            "r11_804_tol": bool(TOL_11_804.search(t)), "guidance_tol": bool(TOL_GUIDANCE.search(t))}


def norm_sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def pages_from_pdfinfo(out):
    m = re.search(r"^Pages:\s+(\d+)", out or "", re.M)
    return int(m.group(1)) if m else 0


def select_targets(entries, row_id_fn, targets=TARGETS):
    """The listing entries whose row id is a target, first occurrence only, in listing order."""
    found, seen = [], set()
    for e in entries:
        rid = row_id_fn(e)
        if rid in targets and rid not in seen:
            seen.add(rid)
            e = dict(e)
            e["row_id"] = rid
            found.append(e)
    return found


def _verdict(ok):
    return "held" if ok else "failed"


def grade(docs, targets=TARGETS):
    """Eight addendum predictions (frozen in ADDENDUM-1.md)."""
    fetched = [d for d in docs if d.get("doc_status") == "ok"]
    ocr_ok = [d for d in fetched if d.get("ocr_chars", 0) >= READABLE_CHARS]
    mit = [d for d in ocr_ok if d.get("proceeding") == MITCHELL]
    others = [d for d in ocr_ok if d.get("proceeding") != MITCHELL]
    P = {}
    no_layer = [d for d in fetched if d.get("textlayer_chars", 0) < READABLE_CHARS]
    P["A1"] = {"text": "poppler's pdftotext also finds fewer than 300 characters in at least 25 of the 27 PDFs (check)",
               "detail": {"fetched": len(fetched), "no_text_layer": len(no_layer)},
               "verdict": "not testable" if not fetched else _verdict(len(no_layer) >= 25)}
    if mit:
        a2 = any(d.get("fake_cite") and d.get("ai_mention") for d in mit)
        a5 = any(d.get("r11_101") or d.get("r11_101_tol") for d in mit)
        a6 = any(d.get("r11_18") or d.get("r11_18_tol") for d in mit)
        a7 = any(d.get("guidance") or d.get("guidance_tol") for d in mit)
        v2, v5, v6, v7 = _verdict(a2), _verdict(a5), _verdict(a6), _verdict(a7)
    else:
        v2 = v5 = v6 = v7 = "not testable"
    P["A2"] = {"text": "OCR text of D2026-16 has a fabricated-citation phrase and an AI term, by census 1.0.0's own "
                       "patterns (pattern check, not blind)", "detail": {"ocr_readable": len(mit)}, "verdict": v2}
    fake_others = sorted({d["proceeding"] for d in others if d.get("fake_cite")})
    P["A3"] = {"text": "none of the other OCR-readable decisions has a fabricated-citation phrase",
               "detail": {"n": len(others), "fake_cite": fake_others},
               "verdict": "not testable" if not others else _verdict(not fake_others)}
    ai_others = sorted({d["proceeding"] for d in others if d.get("ai_mention")})
    P["A4"] = {"text": "at most one of the other OCR-readable decisions mentions an AI term",
               "detail": {"n": len(others), "ai_mention": ai_others},
               "verdict": "not testable" if not others else _verdict(len(ai_others) <= 1)}
    P["A5"] = {"text": "D2026-16 cites 37 C.F.R. 11.101, competence (OCR-tolerant; not blind)", "detail": {}, "verdict": v5}
    P["A6"] = {"text": "D2026-16 cites 37 C.F.R. 11.18, signature and certification (OCR-tolerant)", "detail": {}, "verdict": v6}
    P["A7"] = {"text": "D2026-16 cites the USPTO's April 2024 AI guidance (89 FR 25609 or its title; OCR-tolerant)",
               "detail": {}, "verdict": v7}
    P["A8"] = {"text": "all 27 PDFs are fetched and OCR to at least 300 characters",
               "detail": {"targets": len(targets), "fetched": len(fetched), "ocr_readable": len(ocr_ok)},
               "verdict": _verdict(len(fetched) == len(targets) and len(ocr_ok) == len(targets))}
    counts = {"targets": len(targets), "found_in_listing": len(docs), "fetched": len(fetched),
              "sha_match": sum(1 for d in fetched if d.get("sha_match")), "no_text_layer": len(no_layer),
              "ocr_readable": len(ocr_ok),
              "fake_cite_proceedings": sorted({d["proceeding"] for d in ocr_ok if d.get("fake_cite")}),
              "ai_mention_proceedings": sorted({d["proceeding"] for d in ocr_ok if d.get("ai_mention")}),
              "by_year": {}}
    for d in docs:
        y = (d.get("date") or "")[:4]
        b = counts["by_year"].setdefault(y, {"targets": 0, "ocr_readable": 0, "fake_cite": 0, "ai_mention": 0})
        b["targets"] += 1
        if d in ocr_ok:
            b["ocr_readable"] += 1
            b["fake_cite"] += int(bool(d.get("fake_cite")))
            b["ai_mention"] += int(bool(d.get("ai_mention")))
    return {"addendum_version": VERSION, "predictions": P, "counts": counts}


ROW_COLS = ["row_id", "proceeding", "date", "doc_status", "sha_match", "pages", "textlayer_chars", "ocr_chars",
            "ocr_readable"] + list(CENSUS_FLAGS) + list(TOL_KEYS)


def rows_csv(docs):
    lines = [",".join(ROW_COLS)]
    for d in docs:
        vals = []
        for k in ROW_COLS:
            v = d.get(k, "")
            if k == "ocr_readable":
                v = d.get("ocr_chars", 0) >= READABLE_CHARS
            s = str(v)
            vals.append('"%s"' % s.replace('"', '""') if ("," in s or '"' in s) else s)
        lines.append(",".join(vals))
    return "\n".join(lines) + "\n"


def results_md(res, sources):
    out = ["# USPTO OED census, Addendum 1 (OCR of the 27 decisions with no text layer): results", "",
           "Information about public decisions of a federal agency, not legal advice. Made with AI agents working "
           "in MV2's name.", "", "Sources: `%s`" % json.dumps(sources), "",
           "Counts: `%s`" % json.dumps(res["counts"]), "",
           "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        out.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    return "\n".join(out) + "\n"


# --- network and tools (not unit-tested) -------------------------------------------------------
def get(url, timeout=180, accept="*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(MAX_BYTES)


def get_retry(url, tries=3, timeout=180, accept="*/*"):
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


def commits_for(path):
    url = "https://api.github.com/repos/%s/commits?path=%s&per_page=100" % (REPO, path)
    data = json.loads(get(url).decode("utf-8"))
    return [{"sha": c["sha"], "date": c["commit"]["committer"]["date"]} for c in data]


def wait_for_plan(max_minutes, local_sha, step_minutes=5):
    deadline = time.time() + max_minutes * 60
    me = os.path.basename(__file__)
    while True:
        try:
            plan = commits_for(DIR + "/ADDENDUM-1.md")
            code = commits_for(DIR + "/" + me)
            if plan and code:
                committed = get("https://raw.githubusercontent.com/%s/%s/%s/%s" % (REPO, code[0]["sha"], DIR, me))
                if norm_sha(committed) == local_sha:
                    return plan[-1], code[0]
                print(now(), "newest committed addendum code differs from local; waiting", flush=True)
            else:
                print(now(), "addendum or code not public yet", flush=True)
        except Exception as exc:
            print(now(), "github check failed:", exc, flush=True)
        if time.time() > deadline:
            return None, None
        time.sleep(step_minutes * 60)


def load_census(tmpdir):
    data = get_retry("https://raw.githubusercontent.com/%s/%s/%s" % (REPO, CENSUS_COMMIT, CENSUS_PATH))
    if norm_sha(data) != CENSUS_SHA:
        raise RuntimeError("census.py at %s does not match the frozen SHA-256" % CENSUS_COMMIT[:7])
    path = os.path.join(tmpdir, "census.py")
    with open(path, "wb") as fh:
        fh.write(data)
    spec = importlib.util.spec_from_file_location("census", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["census"] = mod
    spec.loader.exec_module(mod)
    if getattr(mod, "VERSION", "") != "1.0.0":
        raise RuntimeError("unexpected census version")
    return mod


def run(cmd, timeout=600):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def pdf_meta(path):
    rc, out, _ = run(["pdfinfo", path], timeout=120)
    meta = {"pages": pages_from_pdfinfo(out)}
    for key in ("Producer", "Creator"):
        m = re.search(r"^%s:\s+(.*)$" % key, out or "", re.M)
        meta[key.lower()] = m.group(1).strip()[:120] if m else ""
    return meta


def text_layer(path):
    rc, out, _ = run(["pdftotext", "-l", str(MAX_PAGES), path, "-"], timeout=300)
    return out if rc == 0 else ""


def ocr(path, workdir):
    prefix = os.path.join(workdir, "p")
    rc, _, err = run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-l", str(MAX_PAGES), path, prefix], timeout=1200)
    pages = sorted(glob.glob(prefix + "-*.png"))
    parts = []
    for png in pages:
        try:
            rc2, out, _ = run(["tesseract", png, "stdout", "-l", "eng"], timeout=600)
            parts.append(out if rc2 == 0 else "")
        except subprocess.TimeoutExpired:
            parts.append("")
        os.remove(png)
    return "\n".join(parts), len(pages)


def fetch_pdf(links):
    last = "no_link"
    for i, url in enumerate(links or []):
        if i:
            time.sleep(DELAY_S)
        try:
            body = get_retry(url)
        except urllib.error.HTTPError as exc:
            last = "http_%s" % exc.code
            continue
        except Exception:
            last = "error"
            continue
        if body.lstrip()[:5] == b"%PDF-":
            return body, "ok"
        last = "not_pdf"
    return None, last


def finish(out_dir, status, rc):
    status["finished"] = now()
    with open(os.path.join(out_dir, "status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=1, default=str)
    print(json.dumps(status, default=str)[:4000])
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--wait-minutes", type=int, default=180)
    args = ap.parse_args(argv)
    priv = os.path.join(args.out_dir, "private")
    os.makedirs(os.path.join(priv, "ocr"), exist_ok=True)
    status = {"started": now(), "addendum_version": VERSION, "log": []}
    for tool in ("pdfinfo", "pdftotext", "pdftoppm", "tesseract"):
        if not shutil.which(tool):
            status["result"] = "stopped: %s not installed" % tool
            return finish(args.out_dir, status, 4)
    rc, out, err = run(["tesseract", "--version"], timeout=60)
    status["tesseract"] = (out or err).splitlines()[0][:80] if (out or err) else ""

    with open(os.path.abspath(__file__), "rb") as fh:
        local_sha = norm_sha(fh.read())
    plan, code = wait_for_plan(args.wait_minutes, local_sha)
    status["code_sha256_local"] = local_sha
    if not plan:
        status["result"] = "stopped: ADDENDUM-1.md and matching code not public; nothing downloaded"
        return finish(args.out_dir, status, 3)
    status.update({"plan_commit": plan, "code_commit": code})
    tmp = tempfile.mkdtemp(prefix="oedocr-")
    try:
        census = load_census(tmp)
    except Exception as exc:
        status["result"] = "stopped: census.py could not be loaded: %s" % str(exc)[:200]
        return finish(args.out_dir, status, 5)

    try:
        body = get_retry(census.PAGE_URL, accept="text/html")
    except Exception as exc:
        status["result"] = "stopped: listing failed: %s" % str(exc)[:200]
        return finish(args.out_dir, status, 6)
    entries, info = census.parse_listing(body, census.PAGE_URL)
    sources = {"plan_commit": plan, "code_commit": code,
               "census": {"commit": CENSUS_COMMIT, "sha256": CENSUS_SHA},
               "listing": {"url": census.PAGE_URL, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                           "entries": info.get("entries"), "fetched_at": now()}}
    docs = select_targets([e for e in entries if census.in_window(e)], census.row_id)
    status["found"] = len(docs)
    if len(docs) < MIN_FOUND:
        status["result"] = "stopped: only %d of %d target rows found in the listing; nothing fetched" % (len(docs), len(TARGETS))
        with open(os.path.join(args.out_dir, "sources.json"), "w", encoding="utf-8") as fh:
            json.dump(sources, fh, indent=1)
        return finish(args.out_dir, status, 7)

    excerpts, meta_lines = [], []
    for i, d in enumerate(docs):
        time.sleep(DELAY_S)
        exp = TARGETS[d["row_id"]]
        pdf, d["doc_status"] = fetch_pdf(d.get("links"))
        if pdf is None:
            print(now(), i + 1, d["proceeding"], d["doc_status"], flush=True)
            continue
        sha = hashlib.sha256(pdf).hexdigest()
        d["sha_match"] = sha.startswith(exp[2])
        work = tempfile.mkdtemp(prefix="doc-", dir=tmp)
        path = os.path.join(work, "d.pdf")
        with open(path, "wb") as fh:
            fh.write(pdf)
        try:
            meta = pdf_meta(path)
            d["pages"] = meta["pages"]
            d["textlayer_chars"] = len(collapse(text_layer(path)))
            text, n = ocr(path, work)
        except Exception as exc:
            print("ocr error", d["row_id"], exc, flush=True)
            text, meta = "", {}
            d["doc_status"] = "ocr_error"
        shutil.rmtree(work, ignore_errors=True)
        meta_lines.append(json.dumps({"row_id": d["row_id"], "sha256": sha, **meta}))
        with open(os.path.join(priv, "ocr", "%s.txt" % d["row_id"]), "w", encoding="utf-8") as fh:
            fh.write(text)
        c = census.classify(text)
        d["ocr_chars"] = c["chars"]
        for k in CENSUS_FLAGS:
            d[k] = bool(c.get(k))
        d.update(tolerant_flags(text))
        for key, ex in sorted(c.get("excerpts", {}).items()):
            excerpts.append("== %s | %s | %s | %s\n%s\n" % (d["row_id"], d["proceeding"], d.get("date"), key, ex))
        print(now(), i + 1, "/", len(docs), d["proceeding"], d["doc_status"], d.get("pages"), d.get("textlayer_chars"),
              d["ocr_chars"], sorted(k for k in CENSUS_FLAGS + TOL_KEYS if d.get(k)), flush=True)

    with open(os.path.join(priv, "excerpts.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(excerpts))
    with open(os.path.join(priv, "meta.jsonl"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(meta_lines) + "\n")
    public = [{k: d.get(k) for k in ROW_COLS if k in d} for d in docs]
    res = grade(docs)
    res["sources"] = sources
    for fname, payload in (("results.json", json.dumps(res, indent=1, default=str)),
                           ("results.md", results_md(res, sources)),
                           ("rows.csv", rows_csv(public)),
                           ("sources.json", json.dumps(sources, indent=1))):
        with open(os.path.join(args.out_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(payload)
    status["result"] = "graded"
    status["predictions"] = {k: v["verdict"] for k, v in res["predictions"].items()}
    status["counts"] = res["counts"]
    return finish(args.out_dir, status, 0)


if __name__ == "__main__":
    sys.exit(main())
