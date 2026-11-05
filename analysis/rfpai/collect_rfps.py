# Apache-2.0. MV2 of Munim, Inc. Made with AI agents working in his name.
"""Collect the frame for the pre-registered study 'How 2026 legal-aid RFPs treat a vendor's own use of AI'.

Version 2 (amendment 1 to analysis/legal-aid-rfp-ai-prereg.md, written 5 Nov 2026 before any
posting text was read for AI language). Sources:
  (a) the live listing https://www.lsntap.org/jobs-rfps
  (b) the Wayback CDX index for the prefix lsntap.org/jobs-rfps/ (1 Sep 2025 - 5 Nov 2026)
  (c) every Wayback capture of the listing page from 1 Jan to 5 Nov 2026, including the text the
      listing shows next to each posting (title, Posted, Closing, teaser) -> listing_teasers
  (d) NEW: the Wayback CDX index for files under lsntap.org/sites/default/files/2026- (PDF, DOCX);
      files not attached to any collected posting page become 'orphan_file' records
  (e) NEW: seeds.json, slugs and file URLs found by web search on 5 Nov 2026 (recorded as such)
Wayback errors (rate limits, 'connection refused') are retried with back-off. PDFs whose text layer
is (nearly) empty are OCR'd with tesseract when it is installed, and OCR use is recorded.
This script only COLLECTS. It does not search the texts for AI terms and computes no counts.

Usage: python collect_rfps.py --out /out [--seeds seeds.json] [--ocr]
"""
import argparse
import hashlib
import html
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (research; MV2 of Munim, Inc.; mv2@munimtech.com)"
BASE = "https://www.lsntap.org"
LISTING = BASE + "/jobs-rfps"
TO = "20261105"
CDX = ("https://web.archive.org/cdx/search/cdx?url=lsntap.org/jobs-rfps/&matchType=prefix"
       f"&from=20250901&to={TO}&output=json&fl=original,timestamp,statuscode&collapse=urlkey")
CDX_LISTING = ("https://web.archive.org/cdx/search/cdx?url=lsntap.org/jobs-rfps&from=20260101"
               f"&to={TO}&output=json&fl=timestamp,statuscode&filter=statuscode:200&collapse=digest")
CDX_FILES = ("https://web.archive.org/cdx/search/cdx?url=lsntap.org/sites/default/files/2026-"
             f"&matchType=prefix&from=20260101&to={TO}&output=json&fl=original,timestamp,statuscode"
             "&filter=statuscode:200&collapse=urlkey")
SLUG_RE = re.compile(r"/jobs-rfps/([a-z0-9][a-z0-9\-]{2,200})(?=[\"'?#/\s<]|$)")
ATTACH_RE = re.compile(r"""href=["']([^"']*/sites/default/files/[^"']+\.(?:pdf|docx))["']""", re.I)
FILE_RE = re.compile(r"/sites/default/files/(20\d\d-\d\d/[^?#\s\"']+\.(?:pdf|docx))$", re.I)
POSTED_RE = re.compile(r"Posted:\s*(\d{1,2}/\d{1,2}/\d{2,4})")
CLOSING_RE = re.compile(r"Closing Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})")
SKIP_SLUGS = {"feed", "rss", "page", "search"}
OCR_MIN_CHARS = 200


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag in ("p", "br", "div", "li", "h1", "h2", "h3", "h4", "tr", "span"):
            self.parts.append("\n" if tag != "span" else " ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(src: str) -> str:
    p = _Text()
    p.feed(src)
    text = html.unescape("".join(p.parts))
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t\r\f\v]+", " ", text)).strip()


def slugs_in(src: str) -> set:
    out = set()
    for m in SLUG_RE.finditer(src):
        s = m.group(1).strip("-")
        if s and s not in SKIP_SLUGS:
            out.add(s)
    return out


def strip_wayback(url: str) -> str:
    """Turn a Wayback-rewritten link back into the original URL."""
    return re.sub(r"^(?:https?://web\.archive\.org)?/web/\d+[a-z_]*/", "", url)


def canon_file(url: str):
    """Canonical https://www.lsntap.org/sites/default/files/YYYY-MM/name.pdf form, or None."""
    u = strip_wayback(html.unescape(url)).split("?")[0].split("#")[0]
    u = re.sub(r":80(?=/)", "", u)
    m = FILE_RE.search(u)
    if not m:
        return None
    return BASE + "/sites/default/files/" + m.group(1)


def parse_posting(src: str) -> dict:
    text = html_to_text(src)
    title = ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S | re.I)
    if m:
        title = html_to_text(m.group(1))
    if not title or title == "Jobs & RFPs":
        m2 = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
        t2 = html_to_text(m2.group(1)) if m2 else ""
        t2 = re.sub(r"\s*\|.*$", "", t2)
        if t2 and t2 != "Jobs & RFPs":
            title = t2
        elif not title:
            title = t2
    posted = POSTED_RE.search(text)
    closing = CLOSING_RE.search(text)
    attachments = []
    for a in ATTACH_RE.findall(src):
        a = strip_wayback(html.unescape(a))
        url = urllib.parse.urljoin(BASE + "/", a)
        c = canon_file(url) or url
        if c not in attachments:
            attachments.append(c)
    return {"title": title, "posted": posted.group(1) if posted else None,
            "closing": closing.group(1) if closing else None,
            "attachments": attachments, "page_text": text}


def listing_teasers(src: str) -> dict:
    """For a listing page, the text shown with each posting: {slug: {'text', 'posted', 'closing'}}.
    Each segment runs from a posting's first link to the next different posting's first link."""
    marks = []
    seen = set()
    for m in SLUG_RE.finditer(src):
        s = m.group(1).strip("-")
        if s in SKIP_SLUGS or s in seen:
            continue
        seen.add(s)
        start = src.rfind("<", 0, m.start())
        marks.append((start if start >= 0 else m.start(), s))
    out = {}
    for i, (pos, s) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else min(len(src), pos + 6000)
        seg = html_to_text(src[pos:end])
        p, c = POSTED_RE.search(seg), CLOSING_RE.search(seg)
        out[s] = {"text": seg[:4000], "posted": p.group(1) if p else None, "closing": c.group(1) if c else None}
    return out


def docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "".join(f"\n===== PAGE {i} =====\n{(p.extract_text() or '')}" for i, p in enumerate(reader.pages, 1))


def ocr_pdf(data: bytes) -> str:
    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        raise RuntimeError("OCR tools not installed")
    with tempfile.TemporaryDirectory() as d:
        pdf = Path(d) / "in.pdf"
        pdf.write_bytes(data)
        subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf), str(Path(d) / "p")], check=True,
                       capture_output=True, timeout=600)
        parts = []
        for i, img in enumerate(sorted(Path(d).glob("p-*.png")), 1):
            r = subprocess.run(["tesseract", str(img), "-", "-l", "eng"], capture_output=True, timeout=300)
            parts.append(f"\n===== PAGE {i} (OCR) =====\n" + r.stdout.decode("utf-8", "replace"))
        return "".join(parts)


def is_archive(url: str) -> bool:
    return "web.archive.org" in url


def get(url: str, tries: int = None, pause: float = None):
    """Fetch with retries. Wayback gets a longer pause and more tries (it rate-limits)."""
    arch = is_archive(url)
    tries = tries or (6 if arch else 3)
    pause = pause if pause is not None else (4.0 if arch else 1.0)
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            time.sleep(pause)
            return data, None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                break
        except Exception as e:  # network errors are recorded, not fatal
            last = f"{type(e).__name__}: {e}"
        time.sleep(pause * (2 ** k) if arch else pause * (k + 2))
    return None, last


def wayback(url: str, ts: str = TO + "000000") -> str:
    return f"https://web.archive.org/web/{ts}id_/{url}"


def cdx_rows(url: str, log: dict, key: str) -> list:
    data, err = get(url)
    log["sources"][key] = err or "ok"
    if not data:
        return []
    try:
        rows = json.loads(data.decode("utf-8") or "[]")
    except ValueError as e:
        log["sources"][key] = f"bad json: {e}"
        return []
    return rows[1:] if rows else []


def fetch_file(url: str, ts: str, out: Path, stem: str, ocr: bool) -> dict:
    f = {"url": url}
    b, e = get(url)
    f["source"] = "live"
    if not b:
        f["live_error"] = e
        b, e = get(wayback(url, ts or TO + "000000"))
        f["source"] = "wayback" if b else None
    if not b:
        f["error"] = e
        return f
    ext = url.rsplit(".", 1)[-1].lower()
    f["sha256"] = hashlib.sha256(b).hexdigest()
    f["bytes"] = len(b)
    (out / "files" / f"{stem}.{ext}").write_bytes(b)
    try:
        t = docx_text(b) if ext == "docx" else pdf_text(b)
    except Exception as ex:
        f["text_error"] = f"{type(ex).__name__}: {ex}"
        t = ""
    f["ocr"] = False
    if ext == "pdf" and len(t.strip()) < OCR_MIN_CHARS and ocr:
        try:
            t2 = ocr_pdf(b)
            if len(t2.strip()) > len(t.strip()):
                t, f["ocr"] = t2, True
        except Exception as ex:
            f["ocr_error"] = f"{type(ex).__name__}: {ex}"
    f["text_chars"] = len(t.strip())
    (out / "texts" / f"{stem}.txt").write_text(t, encoding="utf-8")
    return f


def safe_stem(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s)[:150]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="seeds.json")
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--max-postings", type=int, default=400)
    ap.add_argument("--max-files", type=int, default=400)
    a = ap.parse_args(argv)
    out = Path(a.out)
    (out / "texts").mkdir(parents=True, exist_ok=True)
    (out / "files").mkdir(parents=True, exist_ok=True)
    log = {"sources": {}, "errors": []}

    slugs, teasers = {}, {}

    def add_teasers(src: str, where: str):
        for s, t in listing_teasers(src).items():
            t["where"] = where
            old = teasers.get(s)
            if old is None or (t["posted"] and not old.get("posted")) or len(t["text"]) > len(old["text"]):
                teasers[s] = t

    data, err = get(LISTING)
    log["sources"]["live_listing"] = err or "ok"
    if data:
        src = data.decode("utf-8", "replace")
        for s in slugs_in(src):
            slugs.setdefault(s, set()).add("live_listing")
        add_teasers(src, "live_listing")

    for row in cdx_rows(CDX, log, "cdx_prefix"):
        for s in slugs_in(row[0]):
            slugs.setdefault(s, set()).add("cdx_prefix")

    snaps = [r[0] for r in cdx_rows(CDX_LISTING, log, "cdx_listing")]
    log["listing_snapshots"] = len(snaps)
    for ts in snaps:
        d, e = get(wayback(LISTING, ts))
        if d:
            src = d.decode("utf-8", "replace")
            for s in slugs_in(src):
                slugs.setdefault(s, set()).add(f"snapshot:{ts}")
            add_teasers(src, f"snapshot:{ts}")
        else:
            log["errors"].append({"snapshot": ts, "error": e})

    seeds = {"slugs": [], "files": []}
    sp = Path(a.seeds)
    if sp.exists():
        seeds = json.loads(sp.read_text(encoding="utf-8"))
        log["sources"]["seeds"] = f"ok ({len(seeds.get('slugs', []))} slugs, {len(seeds.get('files', []))} files)"
    for s in seeds.get("slugs", []):
        slugs.setdefault(s["slug"], set()).add("web_search_seed")

    file_rows = cdx_rows(CDX_FILES, log, "cdx_files")
    archived_files = {}
    for row in file_rows:
        c = canon_file(row[0])
        if c and c not in archived_files:
            archived_files[c] = row[1]
    for f in seeds.get("files", []):
        c = canon_file(f["url"])
        if c:
            archived_files.setdefault(c, None)
    file_found_via = {c: ("cdx_files" if ts else "web_search_seed") for c, ts in archived_files.items()}
    for f in seeds.get("files", []):
        c = canon_file(f["url"])
        if c and file_found_via.get(c) == "cdx_files":
            file_found_via[c] = "cdx_files+web_search_seed"

    frame, attached = [], set()
    for slug in sorted(slugs)[: a.max_postings]:
        url = f"{LISTING}/{slug}"
        rec = {"slug": slug, "kind": "posting", "url": url, "found_via": sorted(slugs[slug])}
        if slug in teasers:
            rec["listing_teaser"] = teasers[slug]
        d, e = get(url)
        rec["page_source"] = "live"
        if not d:
            rec["live_error"] = e
            d, e = get(wayback(url))
            rec["page_source"] = "wayback" if d else None
        if not d:
            rec["page_error"] = e
            if slug in teasers:
                t = teasers[slug]["text"]
                (out / "texts" / f"{slug}__teaser.txt").write_text(t, encoding="utf-8")
                rec["teaser_text_sha256"] = hashlib.sha256(t.encode()).hexdigest()
                rec["posted"] = teasers[slug]["posted"]
                rec["closing"] = teasers[slug]["closing"]
            frame.append(rec)
            continue
        info = parse_posting(d.decode("utf-8", "replace"))
        rec.update({k: info[k] for k in ("title", "posted", "closing", "attachments")})
        if not rec["posted"] and slug in teasers:
            rec["posted"], rec["posted_from"] = teasers[slug]["posted"], "listing_teaser"
        page_txt = out / "texts" / f"{slug}__page.txt"
        page_txt.write_text(info["page_text"], encoding="utf-8")
        rec["page_text_sha256"] = hashlib.sha256(info["page_text"].encode()).hexdigest()
        rec["files"] = []
        for i, att in enumerate(info["attachments"]):
            attached.add(canon_file(att) or att)
            rec["files"].append(fetch_file(att, archived_files.get(canon_file(att) or att), out, f"{slug}__{i}", a.ocr))
        frame.append(rec)

    n = 0
    for c in sorted(archived_files):
        if c in attached or n >= a.max_files:
            continue
        n += 1
        month = re.search(r"/files/(20\d\d-\d\d)/", c).group(1)
        rec = {"slug": "file:" + c.split("/sites/default/files/", 1)[1], "kind": "orphan_file", "url": c,
               "found_via": [file_found_via[c]], "upload_folder": month, "posted": None,
               "files": [fetch_file(c, archived_files[c], out, "file__" + safe_stem(c.split("/files/", 1)[1].rsplit(".", 1)[0]), a.ocr)]}
        frame.append(rec)

    (out / "frame.json").write_text(json.dumps({"collector": "v2", "collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                               "postings": frame, "log": log}, indent=1), encoding="utf-8")
    print(json.dumps({"records": len(frame), "postings": sum(r["kind"] == "posting" for r in frame),
                      "orphan_files": sum(r["kind"] == "orphan_file" for r in frame),
                      "pages_missing": sum(r["kind"] == "posting" and not r.get("page_source") for r in frame),
                      "log_sources": log["sources"], "listing_snapshots": log["listing_snapshots"],
                      "errors": len(log["errors"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
