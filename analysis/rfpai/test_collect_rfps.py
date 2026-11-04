# Apache-2.0. MV2 of Munim, Inc. Offline tests for collect_rfps.py.
import io
import unittest
import zipfile

import collect_rfps as c

LISTING = """<html><body>
<a href="/jobs-rfps/rfp-intake-system-assessment-and-improvement-project">(RFP) Intake</a>
<a href="https://www.lsntap.org/jobs-rfps/mlsa-rebrand">MLSA Rebrand</a>
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

    def test_docx_text(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", "<w:document><w:p><w:r><w:t>Hello &amp; bye</w:t></w:r></w:p></w:document>")
        self.assertIn("Hello & bye", c.docx_text(buf.getvalue()))


if __name__ == "__main__":
    unittest.main()
