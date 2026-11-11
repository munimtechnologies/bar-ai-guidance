# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the BIA / A.G. precedent census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import census
import run_job

PAGE30 = """<html><head><script>var x = "ID 4100";</script></head><body>
<nav><a href="/eoir">EOIR</a></nav>
<div class="field">
<p><strong>G-M-T-,</strong> 30 I&amp;N Dec. 228 (BIA 2026)</p>
<p><a href="/eoir/media/1471311/dl?inline">ID 4273</a> (PDF)</p>
<p>Headnote cites Matter of Sethi, 30 I&amp;N Dec. 112 (BIA 2026).</p>
<hr>
<p><strong>Sethi</strong>, 30 I&amp;N Dec. 112 (BIA 2026)</p>
<p>ID <a href="/media/1463666/dl?inline">4254</a> (PDF)</p>
<p>The respondent is suspended from practice.</p>
<hr>
<p><strong>T-C-A-,</strong> 30 I&amp;N Dec. 99 (A.G. 2026)</p>
<p><a href="/file/1468491/download">ID</a> <a href="/media/1208956/dl?inline">4251</a> (PDF)<a href="/media/9999/dl?inline"></a></p>
<p>Headnote.</p>
<hr>
<p><strong>X-Y-,</strong> 30 I&amp;N Dec. 81 (BIA 2026)</p>
<p><a href="https://www.justice.gov/d9/2026-01/4249.pdf">ID 4249 (PDF)</a></p>
<p><strong>ID 4249</strong> duplicate mention</p>
<p>No ID here: Z-, 30 I&amp;N Dec. 70 (BIA 2026)</p>
</div></body></html>"""

URL30 = "https://www.justice.gov/eoir/volume-30"
FILLER = " The Board orders as follows." * 12
SETHI_TEXT = ("BOARD OF IMMIGRATION APPEALS. In re: Practitioner. ON BEHALF OF DISCIPLINARY COUNSEL. "
              "The respondent is suspended from practice before the Board for six months. The respondent's "
              "brief cited fictitious cases produced with artificial intelligence. See 8 C.F.R. "
              "§ 1003.106(a)(1)." + FILLER)
MERITS_TEXT = ("The respondent submitted a fabricated asylum claim and a fake court summons. "
               "He was granted suspension of deportation in 1995." + FILLER)
CSV_PLAIN = ("case_id,Case Name,Court,State,Date\n"
             "2,Lnu v. Blanche,9th Cir. CA,USA,2026-06-03\n"
             "3,USA v. Sethi,E.D. Texas,USA,2025-08-28\n")
CSV_BIA = CSV_PLAIN + "1,Matter of Q,Board of Immigration Appeals,USA,2026-10-01\n"
CSV_CITE = CSV_PLAIN + "4,\"Matter of Sethi, 30 I&N Dec. 112 (BIA 2026)\",9th Cir. CA,USA,2026-10-01\n"


class Listing(unittest.TestCase):
    def setUp(self):
        self.e = census.parse_listing(PAGE30.encode("utf-8"), 30, URL30)

    def test_ids_in_order_script_and_duplicates_skipped(self):
        self.assertEqual([x["id"] for x in self.e], [4273, 4254, 4251, 4249])

    def test_citations(self):
        self.assertEqual([x["cite"] for x in self.e],
                         ["30 I&N Dec. 228", "30 I&N Dec. 112", "30 I&N Dec. 99", "30 I&N Dec. 81"])
        self.assertEqual([x["issuer"] for x in self.e], ["BIA", "BIA", "AG", "BIA"])
        self.assertEqual(self.e[1]["year"], 2026)

    def test_links(self):
        self.assertEqual(self.e[0]["links"], ["https://www.justice.gov/eoir/media/1471311/dl?inline"])
        self.assertEqual(self.e[1]["links"], ["https://www.justice.gov/media/1463666/dl?inline"])
        self.assertEqual(self.e[2]["links"], ["https://www.justice.gov/file/1468491/download",
                                              "https://www.justice.gov/media/1208956/dl?inline"])
        self.assertEqual(self.e[3]["links"], ["https://www.justice.gov/d9/2026-01/4249.pdf"])

    def test_other_volume_gives_no_citation(self):
        e = census.parse_listing(PAGE30, 29, "https://www.justice.gov/eoir/volume-29")
        self.assertEqual(len(e), 4)
        self.assertTrue(all(x["cite"] == "" and x["page"] is None for x in e))

    def test_gaps(self):
        self.assertEqual(census.id_gaps([{"id": 5}, {"id": 8}, {"id": 6}]), [7])
        self.assertEqual(census.id_gaps([]), [])

    def test_issuer(self):
        self.assertEqual(census.issuer_of("A. G."), "AG")
        self.assertEqual(census.issuer_of("BIA"), "BIA")


class Classify(unittest.TestCase):
    def test_discipline_decision(self):
        r = census.classify(SETHI_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation", "disc_reg", "discipline"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["pm2540"])
        self.assertIn("fake_cite", r["excerpts"])

    def test_merits_decision_not_flagged(self):
        r = census.classify(MERITS_TEXT)
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)

    def test_singular_does_not_exist(self):
        self.assertTrue(census.classify("The brief cites a case that does not exist.")["fake_cite"])

    def test_pm_and_al(self):
        r = census.classify("EOIR Policy Memorandum 25-40 addresses Al-generated content.")
        self.assertTrue(r["pm2540"])
        self.assertTrue(r["ai_mention"])
        self.assertTrue(census.classify("The term (AI) is defined.")["ai_mention"])
        self.assertFalse(census.classify("Al Capone, an LLM graduate, testified.")["ai_mention"])

    def test_empty(self):
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_BIA)
        self.assertEqual(len(db["court_rows"]), 1)
        self.assertEqual(len(db["pfr_rows"]), 1)
        self.assertEqual(len(db["joined"]), 3)

    def test_in_db(self):
        db = census.db_check(CSV_CITE)
        self.assertTrue(census.in_db(db, "30 I&N Dec. 112"))
        self.assertFalse(census.in_db(db, "30 I&N Dec. 11"))
        self.assertFalse(census.in_db(census.db_check(CSV_PLAIN), "30 I&N Dec. 112"))
        self.assertFalse(census.in_db(None, "30 I&N Dec. 112"))


def _docs():
    sethi = {"id": 4254, "volume": 30, "page": 112, "cite": "30 I&N Dec. 112", "issuer": "BIA", "year": 2026,
             "readable": True, "doc_status": "ok"}
    sethi.update({k: v for k, v in census.classify(SETHI_TEXT).items() if k != "excerpts"})
    other = {"id": 4273, "volume": 30, "page": 228, "cite": "30 I&N Dec. 228", "issuer": "BIA", "year": 2026,
             "readable": True, "doc_status": "ok"}
    other.update({k: v for k, v in census.classify(MERITS_TEXT).items() if k != "excerpts"})
    lost = {"id": 4249, "volume": 30, "page": 81, "cite": "30 I&N Dec. 81", "readable": False, "doc_status": "http_404"}
    return [sethi, other, lost]


class Grade(unittest.TestCase):
    def verdicts(self, db):
        return {k: v["verdict"] for k, v in census.grade(_docs(), db, [])["predictions"].items()}

    def test_all_hold(self):
        v = self.verdicts(census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P1": "held", "P2": "held", "P3": "held", "P4": "held", "P5": "held",
                             "P6": "held", "P7": "held", "P8": "held"})

    def test_db_variants(self):
        self.assertEqual(self.verdicts(None)["P7"], "not testable")
        self.assertEqual(self.verdicts(None)["P8"], "not testable")
        v = self.verdicts(census.db_check(CSV_BIA))
        self.assertEqual((v["P7"], v["P8"]), ("failed", "not testable"))
        v = self.verdicts(census.db_check(CSV_CITE))
        self.assertEqual((v["P7"], v["P8"]), ("held", "failed"))

    def test_no_fake(self):
        docs = _docs()[1:]
        v = {k: x["verdict"] for k, x in census.grade(docs, None, [])["predictions"].items()}
        self.assertEqual((v["P1"], v["P2"], v["P4"], v["P5"]), ("not testable", "failed", "not testable", "not testable"))

    def test_outputs(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), [{"volume": 30, "entries": 3}])
        self.assertEqual(res["counts"]["fake_cite"], 1)
        self.assertNotIn("joined", res["database"])
        md = census.results_md(res, {"x": 1})
        self.assertIn("30 I&N Dec. 112", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["id", "cite"])
        self.assertEqual(len(rows), 4)


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_get(self, url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PLAIN.encode("utf-8"), "text/csv"
        if url == URL30:
            return PAGE30.encode("utf-8"), "text/html"
        if "/volume-" in url:
            return b"<html><body>No entries.</body></html>", "text/html"
        if url.endswith("/file/1468491/download"):
            return b"<html>not a pdf</html>", "text/html"
        if url.endswith("4249.pdf"):
            raise run_job.urllib.error.HTTPError(url, 404, "nf", None, None)
        return b"%PDF-" + url.encode("utf-8"), "application/pdf"

    @staticmethod
    def fake_text(data):
        return SETHI_TEXT if b"1463666" in data else MERITS_TEXT

    def test_build_frame_page_failure(self):
        def fetch(url):
            if url.endswith("29"):
                raise OSError("down")
            return PAGE30.encode("utf-8") if url == URL30 else b"<html></html>"
        with mock.patch.object(run_job, "DELAY_S", 0):
            docs, table, failed = run_job.build_frame([], fetch)
        self.assertEqual(failed, 1)
        self.assertEqual(len(docs), 4)
        self.assertEqual([t["volume"] for t in table], [28, 29, 30])

    def test_main(self):
        with mock.patch.object(run_job, "DELAY_S", 0), \
                mock.patch.object(run_job, "get_retry", self.fake_get), \
                mock.patch.object(run_job, "pdf_text", self.fake_text), \
                mock.patch.object(run_job, "wait_for_plan", lambda m, s: ({"sha": "a"}, {"sha": "b"}, s)), \
                mock.patch.object(census, "MIN_FRAME", 1):
            rc = run_job.main(["--out-dir", self.tmp])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.tmp, "results.json"), encoding="utf-8") as fh:
            res = json.load(fh)
        v = {k: x["verdict"] for k, x in res["predictions"].items()}
        self.assertEqual(v["P1"], "held")
        self.assertEqual(v["P2"], "held")
        self.assertEqual(res["counts"]["in_frame"], 4)
        self.assertEqual(res["counts"]["readable"], 3)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("https://www.justice.gov/media/1208956/dl?inline", body)
        self.assertNotIn("1468491", body)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        with mock.patch.object(run_job, "DELAY_S", 0), \
                mock.patch.object(run_job, "get_retry", self.fake_get), \
                mock.patch.object(run_job, "wait_for_plan", lambda m, s: ({"sha": "a"}, {"sha": "b"}, s)):
            rc = run_job.main(["--out-dir", self.tmp])
        self.assertEqual(rc, 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
