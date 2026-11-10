# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for run_job (MSPB fabricated-citation census 1.0.0); no network."""
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
from test_census import FAKE_AI, NONPREC, PLAIN, PREC, TABLE  # noqa: E402

PDF_HEAD = b"%PDF-1.7\n"
CSV_TEXT = ("case_id,Case Name,Court,State(s),Date\n"
            "2762,Thorogood v. Merit Systems Protection Board,Fed. Cir.,USA,2026-10-08\n").encode("utf-8")


def fake_site(fail_main=False):
    manifests = {census.BASE + census.MAIN_MANIFESTS[0]: NONPREC, census.BASE + census.MAIN_MANIFESTS[1]: PREC,
                 census.BASE + census.EXTRA_MANIFESTS[0]: TABLE}

    def get_retry(url, **kw):
        if url == run_job.CSV_URL:
            return CSV_TEXT, "text/csv"
        if url in manifests:
            if fail_main and url == census.BASE + census.MAIN_MANIFESTS[0]:
                raise urllib.error.HTTPError(url, 500, "boom", {}, None)
            return manifests[url].encode("utf-8"), "application/json"
        if url.endswith(".json"):
            raise urllib.error.HTTPError(url, 404, "gone", {}, None)
        if "Moreland" in url:
            return PDF_HEAD + FAKE_AI.encode("utf-8"), "application/pdf"
        if "Vann" in url:
            raise urllib.error.HTTPError(url, 404, "gone", {}, None)
        return PDF_HEAD + PLAIN.encode("utf-8"), "application/pdf"
    return get_retry


def text_of(data):
    return data[len(PDF_HEAD):].decode("utf-8")


class TestBuildFrame(unittest.TestCase):
    def run_frame(self, **kw):
        log = []
        with tempfile.TemporaryDirectory() as priv, \
                mock.patch.object(run_job, "get_retry", side_effect=fake_site(**kw)), \
                mock.patch.object(run_job.time, "sleep"):
            out = run_job.build_frame(priv, log)
        return out, log

    def test_frame_from_all_manifests(self):
        (frame, table, main_failed), log = self.run_frame()
        self.assertEqual(main_failed, 0)
        self.assertEqual(len(table), 6)
        self.assertEqual(len(frame), 6)
        self.assertEqual([t["manifest"] for t in table if "error" in t], list(census.EXTRA_MANIFESTS[1:]))
        self.assertEqual(table[0]["in_window"], 3)
        self.assertTrue(log[-1].startswith("6 manifests, 0 main failed, 6 decisions in frame"))

    def test_main_manifest_failure_counts(self):
        (frame, table, main_failed), log = self.run_frame(fail_main=True)
        self.assertEqual(main_failed, 1)
        self.assertIn("manifest failed: " + census.MAIN_MANIFESTS[0], log[0])


class TestFetchDocument(unittest.TestCase):
    doc = {"collection": "nonprecedential", "file_name": "Moreland_Todd_DA-3330-25-1121-I-1_4200901.pdf"}

    def test_statuses(self):
        with mock.patch.object(run_job, "get_retry", return_value=(b"%PDF-1.7 x", "application/pdf")):
            self.assertEqual(run_job.fetch_document(self.doc), (b"%PDF-1.7 x", "ok"))
        with mock.patch.object(run_job, "get_retry", return_value=(b"<html>", "text/html")):
            self.assertEqual(run_job.fetch_document(self.doc), (None, "not_pdf"))

        def gone(url, **kw):
            raise urllib.error.HTTPError(url, 404, "gone", {}, None)
        with mock.patch.object(run_job, "get_retry", side_effect=gone):
            self.assertEqual(run_job.fetch_document(self.doc), (None, "pdf_http_404"))
        with mock.patch.object(run_job, "get_retry", side_effect=OSError("reset")):
            self.assertEqual(run_job.fetch_document(self.doc), (None, "pdf_error"))


class TestMain(unittest.TestCase):
    def run_main(self, min_frame=1, **kw):
        out = tempfile.mkdtemp()
        with mock.patch.object(run_job, "get_retry", side_effect=fake_site(**kw)), \
                mock.patch.object(run_job, "wait_for_plan", return_value=({"sha": "p"}, {"sha": "c"}, "x")), \
                mock.patch.object(run_job, "pdf_text", side_effect=text_of), \
                mock.patch.object(run_job.time, "sleep"), \
                mock.patch.object(census, "MIN_FRAME", min_frame):
            rc = run_job.main(["--out-dir", out])
        return rc, out

    def read(self, out, *parts):
        with open(os.path.join(out, *parts), encoding="utf-8") as fh:
            return fh.read()

    def test_end_to_end(self):
        rc, out = self.run_main()
        self.assertEqual(rc, 0)
        status = json.loads(self.read(out, "status.json"))
        self.assertEqual(status["result"], "graded")
        self.assertEqual(status["counts"]["in_frame"], 6)
        self.assertEqual(status["counts"]["readable"], 5)
        self.assertEqual(status["counts"]["fake_cite"], 1)
        self.assertEqual(status["predictions"]["P1"], "failed")
        self.assertEqual(status["predictions"]["P8"], "held")
        rows = self.read(out, "rows.csv")
        self.assertEqual(len(rows.strip().splitlines()), 7)
        for name in ("Moreland", "Vann", "Medina", "Laboy", "Shows", "Unpadded"):
            self.assertNotIn(name, rows + self.read(out, "results.md") + self.read(out, "results.json"))
        names = json.loads(self.read(out, "private", "file_names.json"))
        self.assertEqual(list(names.values()), ["Moreland_Todd_DA-3330-25-1121-I-1_4200901.pdf"])
        self.assertIn("pdf_http_404", self.read(out, "private", "progress.jsonl"))

    def test_small_frame_stops_before_pdfs(self):
        rc, out = self.run_main(min_frame=census.MIN_FRAME)
        self.assertEqual(rc, 6)
        self.assertFalse(os.path.exists(os.path.join(out, "private", "progress.jsonl")))

    def test_main_manifest_failure_stops(self):
        rc, out = self.run_main(fail_main=True)
        self.assertEqual(rc, 5)


if __name__ == "__main__":
    unittest.main()
