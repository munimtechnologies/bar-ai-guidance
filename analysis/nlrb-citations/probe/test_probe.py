# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe  # noqa: E402

HTML = ('<table><tr><th>Issuance Date</th></tr>'
        '<tr class="odd"><td>10/30/2026</td><td>375 NLRB No. 67</td>'
        '<td><a href="https://apps.nlrb.gov/link/document.aspx/09031d45843d4761">X Inc.</a></td>'
        '<td><a href="/case/05-CA-300367">05-CA-300367</a></td></tr>'
        '<tr><td>01/28/2026</td><td>374 NLRB No. 30</td><td>no link</td></tr></table>')


class TestProbe(unittest.TestCase):
    def test_parse_rows(self):
        rows = probe.parse_rows(HTML)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], {"year": 2026, "volume": 375, "slip": 67,
                                   "doc": "09031d45843d4761", "case": "05-CA-300367"})
        self.assertEqual(rows[1]["volume"], 374)
        self.assertEqual(rows[1]["slip"], 30)
        self.assertIsNone(rows[1]["doc"])
        self.assertIsNone(rows[1]["case"])

    def test_tally(self):
        t = probe.tally(probe.parse_rows(HTML))
        self.assertEqual(t["rows"], 2)
        self.assertEqual(t["by_volume"], {"374": 1, "375": 1})
        self.assertEqual(t["by_year"], {"2026": 2})
        self.assertEqual((t["no_doc"], t["no_case"], t["no_year"]), (1, 1, 0))

    def test_should_stop(self):
        self.assertTrue(probe.should_stop([]))
        self.assertTrue(probe.should_stop([{"year": 2023}, {"year": 2022}]))
        self.assertFalse(probe.should_stop([{"year": 2026}, {"year": 2023}]))
        self.assertFalse(probe.should_stop([{"year": None}]))

    def test_hits(self):
        text = ("The request for review cites to cases that, as far as the Board can determine, do not exist. "
                "Such ghost citations may be AI output. Aid was paid.")
        counts, ex = probe.find_hits(text)
        self.assertEqual(counts["not_exist"], 1)
        self.assertEqual(counts["ghost"], 1)
        self.assertEqual(counts["ai_term"], 1)
        self.assertEqual(counts["fabricat"], 0)
        self.assertTrue(any(k == "not_exist" and "do not exist" in s for k, _, s in ex))

    def test_is_pdf(self):
        self.assertTrue(probe.is_pdf(b"%PDF-1.7 x"))
        self.assertFalse(probe.is_pdf(b"<!DOCTYPE html>"))

    def test_never_requests_disallowed_host(self):
        self.assertNotIn("apps.nlrb.gov", probe.MIRROR)
        self.assertNotIn("apps.nlrb.gov", probe.LISTING)
        self.assertTrue(probe.MIRROR.startswith("https://nlrbresearch.com/pdfs/"))


if __name__ == "__main__":
    unittest.main()
