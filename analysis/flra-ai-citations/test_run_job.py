# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for run_job.build_frame (FLRA archive AI-citation census 1.0.1); no network."""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_job  # noqa: E402
from test_census import DRUPAL_HTML  # noqa: E402

OLD_PAGE = """<table><tr><th>Citation #</th></tr>
<tr class="group-one first"><td>72 FLRA 300</td><td>60</td><td>Dec. 20, 2021</td></tr>
<tr class="group-one last"><td><a href="https://www.flra.gov/decisions/v72/72-60.html">HTML</a></td></tr>
</table>"""


def fake_site(pages):
    def get_retry(url, **kw):
        page = int(url.rsplit("=", 1)[1])
        return pages.get(page, b"<html>empty</html>"), "text/html"
    return get_retry


class TestBuildFrame(unittest.TestCase):
    def run_frame(self, pages, max_pages=10):
        log = []
        with tempfile.TemporaryDirectory() as priv, \
                mock.patch.object(run_job, "get_retry", side_effect=fake_site(pages)), \
                mock.patch.object(run_job.time, "sleep"):
            out = run_job.build_frame(priv, log, max_pages=max_pages)
            saved = sorted(os.listdir(priv))
        return out, log, saved

    def test_empty_page_is_skipped_and_start_reached(self):
        pages = {0: DRUPAL_HTML.encode(), 2: OLD_PAGE.encode()}
        (frame, npages, undated, reached), log, saved = self.run_frame(pages)
        self.assertEqual([r["citation"] for r in frame], ["74 FLRA No. 89", "74 FLRA No. 29"])
        self.assertEqual((npages, undated, reached), (3, 0, True))
        self.assertIn("listing page 1: no rows parsed", log)
        self.assertIn("reached 2022-01-01 on page 2", log)
        self.assertEqual(saved, ["listing_empty_1.html", "listing_page0.html"])

    def test_two_empty_pages_stop_without_reaching_start(self):
        pages = {0: DRUPAL_HTML.replace("Jul. 01, 2021", "Jul. 01, 2022").encode()}
        (frame, npages, undated, reached), log, saved = self.run_frame(pages)
        self.assertFalse(reached)
        self.assertEqual(npages, 3)
        self.assertEqual(len(frame), 3)
        self.assertIsNone(frame[2]["url"])
        self.assertIn("two empty listing pages in a row; listing stopped", log)
        self.assertTrue(log[-1].startswith("3 listing pages, 3 in frame (1 without an HTML link)"))


if __name__ == "__main__":
    unittest.main()
