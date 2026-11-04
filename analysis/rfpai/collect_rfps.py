# Apache-2.0. MV2 of Munim, Inc. Made with AI agents working in his name.
"""Collect the frame for the pre-registered study 'How 2026 legal-aid RFPs treat a vendor's own use of AI'.

Frame (fixed in analysis/legal-aid-rfp-ai-prereg.md before any text is read):
every posting under https://www.lsntap.org/jobs-rfps/<slug> that the Wayback Machine CDX index or
the live listing page shows. This script only COLLECTS: posting pages, their attachments and the
attachments' text. It does not search the texts for AI terms and computes no counts.

Usage: python collect_rfps.py --out /out [--max-postings 400]
"""
import argparse
import hashlib
import html
import io
import json
import re
import sys
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
CDX = ("https://web.archive.org/cdx/search/cdx?url=lsntap.org/jobs-rfps/&matchType=prefix"
       "&from=20250901&to=20261104&output=json&fl=original,timestamp,statuscode&collapse=urlkey")
CDX_LISTING = ("https://web.archive.org/cdx/search/cdx?url=lsntap.org/jobs-rfps&from=20260101"
               "&to=20261104&output=json&fl=timestamp,statuscode&filter=statuscode:200&collapse=digest")
SLUG_RE = re.compile(r"/jobs-rfps/([a-z0-9][a-z0-9\-]{2,200})(?=[\"'?#/\s]|$)")
ATTACH_RE = re.compile(r"""href=["']([^"']*/sites/default/files/[^"']+\.(?:pdf|docx))["']""", re.I)
POSTED_RE = re.compile(r"Posted:\s*(\d{1,2}/\d{1,2}/\d{2,4})")
CLOSING_RE = re.compile(r"Closing Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})")
SKIP_SLUGS = {"feed", "rss", "page", "search"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag in ("p", "br", "div", "li", "h1", "h2", "h3", "tr"):
            self.parts.append("\n")

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


def parse_posting(src: str) -> dict:
    text = html_to_text(src)
    title = ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S | re.I)
    if m:
        title = html_to_text(m.group(1))
    if not title:
        m = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
        title = html_to_text(m.group(1)) if m else ""
    posted = POSTED_RE.search(text)
    closing = CLOSING_RE.search(text)
    attachments = []
    for a in ATTACH_RE.findall(src):
        a = html.unescape(a)
        if "/web/" in a and "web.archive.org" in a or a.startswith("/web/"):
            a = re.sub(r"^.*?/web/\d+[a-z_]*/", "", a)
        url = urllib.parse.urljoin(BASE + "/", a)
        if url not in attachments:
            attachments.append(url)
    return {"title": title, "posted": posted.group(1) if posted else None,
            "closing": closing.group(1) if closing else None,
            "attachments": attachments, "page_text": text}


def docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "".join(f"\n===== PAGE {i} =====\n{(p.extract_text() or '')}" for i, p in enumerate(reader.pages, 1))


def get(url: str, tries: int = 3, pause: float = 1.0):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            time.sleep(pause)
            return data, None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                break
        except Exception as e:  # network errors are recorded, not fatal
            last = f"{type(e).__name__}: {e}"
        time.sleep(pause * (k + 2))
    return None, last


def wayback(url: str) -> str:
    return "https://web.archive.org/web/20261104000000id_/" + url


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-postings", type=int, default=400)
    a = ap.parse_args(argv)
    out = Path(a.out)
    (out / "texts").mkdir(parents=True, exist_ok=True)
    (out / "files").mkdir(parents=True, exist_ok=True)
    log = {"sources": {}, "errors": []}

    slugs = {}
    data, err = get(LISTING)
    log["sources"]["live_listing"] = err or "ok"
    if data:
        for s in slugs_in(data.decode("utf-8", "replace")):
            slugs.setdefault(s, set()).add("live_listing")
    data, err = get(CDX)
    log["sources"]["cdx_prefix"] = err or "ok"
    if data:
        rows = json.loads(data.decode("utf-8") or "[]")
        for row in rows[1:]:
            for s in slugs_in(row[0]):
                slugs.setdefault(s, set()).add("cdx_prefix")
    data, err = get(CDX_LISTING)
    log["sources"]["cdx_listing"] = err or "ok"
    snaps = []
    if data:
        rows = json.loads(data.decode("utf-8") or "[]")
        snaps = [r[0] for r in rows[1:]]
    log["listing_snapshots"] = len(snaps)
    for ts in snaps:
        d, e = get(f"https://web.archive.org/web/{ts}id_/{LISTING}")
        if d:
            for s in slugs_in(d.decode("utf-8", "replace")):
                slugs.setdefault(s, set()).add(f"snapshot:{ts}")
        else:
            log["errors"].append({"snapshot": ts, "error": e})

    frame = []
    for slug in sorted(slugs)[: a.max_postings]:
        url = f"{LISTING}/{slug}"
        rec = {"slug": slug, "url": url, "found_via": sorted(slugs[slug])}
        d, e = get(url)
        rec["page_source"] = "live"
        if not d:
            rec["live_error"] = e
            d, e = get(wayback(url))
            rec["page_source"] = "wayback" if d else None
        if not d:
            rec["page_error"] = e
            frame.append(rec)
            continue
        info = parse_posting(d.decode("utf-8", "replace"))
        rec.update({k: info[k] for k in ("title", "posted", "closing", "attachments")})
        page_txt = out / "texts" / f"{slug}__page.txt"
        page_txt.write_text(info["page_text"], encoding="utf-8")
        rec["page_text_sha256"] = hashlib.sha256(info["page_text"].encode()).hexdigest()
        rec["files"] = []
        for i, att in enumerate(info["attachments"]):
            f = {"url": att}
            b, e = get(att)
            f["source"] = "live"
            if not b:
                f["live_error"] = e
                b, e = get(wayback(att))
                f["source"] = "wayback" if b else None
            if not b:
                f["error"] = e
                rec["files"].append(f)
                continue
            ext = att.rsplit(".", 1)[-1].lower()
            f["sha256"] = hashlib.sha256(b).hexdigest()
            f["bytes"] = len(b)
            (out / "files" / f"{slug}__{i}.{ext}").write_bytes(b)
            try:
                t = docx_text(b) if ext == "docx" else pdf_text(b)
            except Exception as ex:
                f["text_error"] = f"{type(ex).__name__}: {ex}"
                t = ""
            f["text_chars"] = len(t.strip())
            (out / "texts" / f"{slug}__{i}.txt").write_text(t, encoding="utf-8")
            rec["files"].append(f)
        frame.append(rec)

    (out / "frame.json").write_text(json.dumps({"collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                               "postings": frame, "log": log}, indent=1), encoding="utf-8")
    print(json.dumps({"postings": len(frame), "log_sources": log["sources"],
                      "listing_snapshots": log["listing_snapshots"], "errors": len(log["errors"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
