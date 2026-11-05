# Apache-2.0. MV2 of Munim, Inc. Made with AI agents working in his name. Offline tests for collect_rfps.py (v2).
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import collect_rfps as c

LISTING = """<html><body>
<div class="views-row"><h3><a href="/jobs-rfps/rfp-intake-system-assessment-and-improvement-project">(RFP) Intake System</a></h3>
<div>Georgia Legal Services Program</div><div>Posted: 11/3/26</div><div>Closing Date: 11/22/26</div></div>
<div class="views-row"><h3><a href="https://www.lsntap.org/jobs-rfps/mlsa-rebrand">MLSA Rebrand</a></h3>
<div>Posted: 8/5/26</div><div>Closing Date: 9/14/26</div></div>
<a href="/jobs-rfps?page=1">next</a>
<a href="/jobs-rfps/feed">feed</a>
</body></html>"""

POSTING = """<html><head><title>(RFP) Intake | LSNTAP</title></head><body>
<h1>(RFP) Intake System Assessment and Improvement Project</h1>
<div>Posted: 11/3/26</div><div>Closing Date: 11/22/26</div>
<script>var x = "Posted: 1/1/99";</script>
<a href="/sites/default/files/2026-11/rfp-glsp-intake-bpa-final.pdf">RFP</a>
<a href="/web/20261001000000/https://www.lsntap.org/sites/default/files/2026-09/other.docx">doc</a>
</body></html>"""

POSTING_SECTION_H1 = """<html><head><title>MLSA Rebrand | LSNTAP</title></head><body>
<h1>Jobs &amp; RFPs</h1><div>Posted: 8/5/26</div></body></html>"""


class T(unittest.TestCase):
    def test_slugs(self):
        s = c.slugs_in(LISTING)
        self.assertEqual(s, {"rfp-intake-system-assessment-and-improvement-project", "mlsa-rebrand"})

    def test_slug_from_cdx_url(self):
        self.assertEqual(c.slugs_in("https://www.lsntap.org/jobs-rfps/abc-def"), {"abc-def"})

    def test_parse_posting(self):
        p = c.parse_posting(POSTING)
        self.assertEqual(p["title"], "(RFP) Intake System Assessment and Improvement Project")
        self.assertEqual(p["posted"], "11/3/26")
        self.assertEqual(p["closing"], "11/22/26")
        self.assertEqual(p["attachments"], [
            "https://www.lsntap.org/sites/default/files/2026-11/rfp-glsp-intake-bpa-final.pdf",
            "https://www.lsntap.org/sites/default/files/2026-09/other.docx"])
        self.assertNotIn("1/1/99", p["page_text"])

    def test_title_falls_back_from_section_heading(self):
        self.assertEqual(c.parse_posting(POSTING_SECTION_H1)["title"], "MLSA Rebrand")

    def test_listing_teasers(self):
        t = c.listing_teasers(LISTING)
        self.assertEqual(t["rfp-intake-system-assessment-and-improvement-project"]["posted"], "11/3/26")
        self.assertIn("Georgia Legal Services Program", t["rfp-intake-system-assessment-and-improvement-project"]["text"])
        self.assertNotIn("MLSA", t["rfp-intake-system-assessment-and-improvement-project"]["text"])
        self.assertEqual(t["mlsa-rebrand"]["closing"], "9/14/26")
        self.assertNotIn("feed", t)

    def test_canon_file(self):
        want = "https://www.lsntap.org/sites/default/files/2026-07/request-for-proposal-7.14.26.pdf"
        self.assertEqual(c.canon_file("http://lsntap.org:80/sites/default/files/2026-07/request-for-proposal-7.14.26.pdf"), want)
        self.assertEqual(c.canon_file("https://web.archive.org/web/20260801000000id_/" + want + "?x=1"), want)
        self.assertIsNone(c.canon_file("https://www.lsntap.org/sites/default/files/2026-07/logo.png"))

    def test_docx_text(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", "<w:document><w:p><w:r><w:t>Hello &amp; bye</w:t></w:r></w:p></w:document>")
        self.assertIn("Hello & bye", c.docx_text(buf.getvalue()))

    def test_main_offline_with_orphan_file_and_teaser_fallback(self):
        """End to end with a fake network: one live posting, one gone posting known from a listing
        snapshot, one orphan 2026 file from the files CDX, one seed file."""
        live_pdf = b"%PDF-fake"
        pages = {
            c.LISTING: LISTING.replace("mlsa-rebrand", "gone-posting").encode(),
            c.CDX: json.dumps([["original", "timestamp", "statuscode"]]).encode(),
            c.CDX_LISTING: json.dumps([["timestamp", "statuscode"], ["20260601000000", "200"]]).encode(),
            c.wayback(c.LISTING, "20260601000000"): LISTING.replace("mlsa-rebrand", "gone-posting").encode(),
            c.CDX_FILES: json.dumps([["original", "timestamp", "statuscode"],
                                     ["https://www.lsntap.org/sites/default/files/2026-11/rfp-glsp-intake-bpa-final.pdf", "20261104000000", "200"],
                                     ["https://www.lsntap.org/sites/default/files/2026-05/orphan.pdf", "20260520000000", "200"]]).encode(),
            c.LISTING + "/rfp-intake-system-assessment-and-improvement-project": POSTING.encode(),
            "https://www.lsntap.org/sites/default/files/2026-11/rfp-glsp-intake-bpa-final.pdf": live_pdf,
            "https://www.lsntap.org/sites/default/files/2026-09/other.docx": None,
            "https://www.lsntap.org/sites/default/files/2026-05/orphan.pdf": live_pdf,
            "https://www.lsntap.org/sites/default/files/2026-08/seeded.pdf": live_pdf,
        }

        def fake_get(url, tries=None, pause=None):
            d = pages.get(url)
            return (d, None) if d else (None, "HTTP 404")

        with tempfile.TemporaryDirectory() as d:
            seeds = Path(d) / "seeds.json"
            seeds.write_text(json.dumps({"slugs": [], "files": [{"url": "https://www.lsntap.org/sites/default/files/2026-08/seeded.pdf"}]}))
            with mock.patch.object(c, "get", fake_get), mock.patch.object(c, "pdf_text", lambda b: "x" * 300), \
                    mock.patch("builtins.print"):
                c.main(["--out", d, "--seeds", str(seeds)])
            fr = json.loads((Path(d) / "frame.json").read_text())
        recs = {r["slug"]: r for r in fr["postings"]}
        self.assertEqual(recs["rfp-intake-system-assessment-and-improvement-project"]["posted"], "11/3/26")
        gone = recs["gone-posting"]
        self.assertIsNone(gone["page_source"])
        self.assertEqual(gone["posted"], "8/5/26")
        self.assertIn("orphan_file", {r["kind"] for r in fr["postings"]})
        self.assertIn("file:2026-05/orphan.pdf", recs)
        self.assertEqual(recs["file:2026-08/seeded.pdf"]["found_via"], ["web_search_seed"])
        self.assertNotIn("file:2026-11/rfp-glsp-intake-bpa-final.pdf", recs)  # attached, so not an orphan


if __name__ == "__main__":
    unittest.main()
