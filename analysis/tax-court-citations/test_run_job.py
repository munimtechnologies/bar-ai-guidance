# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for run_job (U.S. Tax Court fabricated-citation census 1.0.0); no network."""
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402
import run_job  # noqa: E402
from test_census import OPINION_RESPONSE, ORDER_RESPONSE  # noqa: E402


def fake_api(fail_queries=()):
    def get_retry(url, **kw):
        for q in fail_queries:
            if census.search_url("order", q) == url:
                raise urllib.error.HTTPError(url, 500, "boom", {}, None)
        if "/opinion-search?" in url:
            return OPINION_RESPONSE.encode(), "application/json"
        return ORDER_RESPONSE.encode(), "application/json"
    return get_retry


class TestBuildFrame(unittest.TestCase):
    def run_frame(self, **kw):
        log = []
        with tempfile.TemporaryDirectory() as priv, \
                mock.patch.object(run_job, "get_retry", side_effect=fake_api(**kw)), \
                mock.patch.object(run_job.time, "sleep"):
            out = run_job.build_frame(priv, log)
            saved = sorted(os.listdir(priv))
        return out, log, saved

    def test_frame_from_all_searches(self):
        (frame, table, failures), log, saved = self.run_frame()
        self.assertEqual(len(table), 2 * len(census.QUERIES))
        self.assertEqual(failures, 0)
        self.assertEqual(sorted(frame), ["723ad324-f176-4a2b-a6a8-27e7a75cdfaa", "e87a6f9d-54aa-42d6-9477-25440d55797e"])
        self.assertEqual(len(frame["e87a6f9d-54aa-42d6-9477-25440d55797e"]["queries"]), len(census.QUERIES))
        self.assertEqual(table[0], {"kind": "order", "query": census.QUERIES[0], "results": 2, "capped": False,
                                    "in_window": 1})
        self.assertEqual(saved, ["search_sample.json"])
        self.assertTrue(log[-1].startswith("%d searches, 0 failed, 2 documents" % (2 * len(census.QUERIES))))

    def test_failed_search_is_logged(self):
        (frame, table, failures), log, saved = self.run_frame(fail_queries=("ChatGPT",))
        self.assertEqual(failures, 1)
        bad = [r for r in table if "error" in r]
        self.assertEqual([(r["kind"], r["query"]) for r in bad], [("order", "ChatGPT")])
        self.assertIn("search failed: order ChatGPT", log[0])


class TestFetchDocument(unittest.TestCase):
    doc = {"docket_number": "10795-22", "docket_entry_id": "243294e3-e4f8-445b-bf9d-f05b74a43a67"}

    def test_ok(self):
        calls = []

        def get_retry(url, **kw):
            calls.append(url)
            if url.endswith("/public-document-download-url"):
                return json.dumps({"url": "https://s3.us-east-1.amazonaws.com/b/key?sig=1"}).encode(), "application/json"
            return b"%PDF-1.7 ...", "application/pdf"
        with mock.patch.object(run_job, "get_retry", side_effect=get_retry):
            body, st = run_job.fetch_document(self.doc)
        self.assertEqual((body, st), (b"%PDF-1.7 ...", "ok"))
        self.assertEqual(calls[0], census.API + "/10795-22/243294e3-e4f8-445b-bf9d-f05b74a43a67/public-document-download-url")

    def test_errors(self):
        def denied(url, **kw):
            raise urllib.error.HTTPError(url, 403, "no", {}, None)
        with mock.patch.object(run_job, "get_retry", side_effect=denied):
            self.assertEqual(run_job.fetch_document(self.doc), (None, "url_http_403"))
        with mock.patch.object(run_job, "get_retry", return_value=(b"{}", "application/json")):
            self.assertEqual(run_job.fetch_document(self.doc), (None, "no_url"))


if __name__ == "__main__":
    unittest.main()
