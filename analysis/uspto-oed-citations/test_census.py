# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the USPTO OED discipline-archive census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import census
import run_job

PAGE = """<html><head><script>var t = "D2026-99";</script></head><body>
<h1>FOIA Documents</h1>
<table>
<thead><tr><th>Proceeding Number</th><th>Decision Related Text</th><th>Respondent Name</th><th>Decision Type</th><th>Decision Date</th></tr></thead>
<tbody>
<tr><td><a href="Mitchell-Final-Order-D2026-16.pdf">D2026-16</a></td><td><a href="Mitchell-Final-Order-D2026-16.pdf">Final Order</a></td><td>Mitchell, Brian E.</td><td>Discipline</td><td>07/27/2026</td></tr>
<tr><td><a href="Graham Final Order D2022-13.pdf">D2022-13</a></td><td>Final Order</td><td>Graham</td><td>Discipline</td><td>3/4/2022</td></tr>
<tr><td><a href="/oed/missing-D2025-13.pdf">D2025-13</a></td><td><a href="Matos (redacted).pdf">Final Order</a></td><td>Anthony Matos</td><td>Discipline</td><td>3/6/2025</td></tr>
<tr><td><a href="Tech-18-6-13-2025-(redacted).pdf">Tech-18</a></td><td>--</td><td>--</td><td>Technical</td><td>6/13/2025</td></tr>
<tr><td>D2019-20</td><td>Final Order</td><td>Lord</td><td>Discipline</td><td>01/02/2019</td></tr>
<tr><td><a href="Smith-D2024-8.pdf">D2024-8</a></td><td><a href="Smith-D2024-8.pdf">Initial Decision</a></td><td>Smith, John</td><td>Discipline</td><td>13/45/2024</td></tr>
<tr><td><a href="Mitchell-Final-Order-D2026-16.pdf">D2026-16</a></td><td>Notice</td><td>Mitchell</td><td>Discipline</td><td>2026-07-28</td></tr>
<tr><td><a href="Jones-D2023-5.pdf">D2023-5</a></td><td>Final Order</td><td>Jones, Ann</td><td>Discipline</td><td>01/15/2023</td></tr>
</tbody></table></body></html>"""

BASE = "https://foiadocuments.uspto.gov/oed/"
FILLER = " The Director so orders." * 15
MITCHELL_TEXT = ("BEFORE THE OFFICE OF ENROLLMENT AND DISCIPLINE. Proceeding No. D2026-16. FINAL ORDER. "
                 "Respondent used generative AI tools. The claim construction chart contained citations to "
                 "nonexistent portions of the specification. Respondent violated 37 C.F.R. 11.101 and "
                 "11.804(c). See Guidance on Use of Artificial Intelligence-Based Tools in Practice Before the "
                 "United States Patent and Trademark Office, 89 Fed. Reg. 25609 (Apr. 11, 2024)." + FILLER)
MATOS_TEXT = ("FINAL ORDER. Proceeding No. D2025-13. The trial brief contained citation to non-existent case "
              "law and inaccurate quotations. Respondent violated 37 C.F.R. 11.18(b) and 11.101." + FILLER)
OTHER_TEXT = ("FINAL ORDER. Respondent was suspended for neglecting client matters and failing to respond "
              "to fake invoices. 37 C.F.R. 11.103." + FILLER)
CSV_PLAIN = ("case_id,Case Name,Court,State,Date\n"
             "2625,In the Matter of Brian E. Mitchell,USPTO,USA,2026-07-27\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08\n")
CSV_PROC = CSV_PLAIN + "11,Re D2025-13 order,N.D. Cal.,USA,2025-05-01\n"
CSV_TWO = CSV_PLAIN + "12,X v. Y,Trademark Trial and Appeal Board,USA,2024-04-01\n"


class Listing(unittest.TestCase):
    def setUp(self):
        self.e, self.info = census.parse_listing(PAGE.encode("utf-8"), BASE)

    def test_rows_and_header(self):
        self.assertEqual([x["proceeding"] for x in self.e],
                         ["D2026-16", "D2022-13", "D2025-13", "Tech-18", "D2019-20", "D2024-8", "D2026-16", "D2023-5"])
        self.assertTrue(self.info["header_found"])
        self.assertEqual(self.info["table_rows"], 9)
        self.assertEqual(self.info["entries"], 8)
        self.assertEqual((self.info["bad_date"], self.info["bad_date_new"]), (1, 1))

    def test_fields(self):
        m = self.e[0]
        self.assertEqual((m["decision_text"], m["respondent"], m["decision_type"], m["date"]),
                         ("Final Order", "Mitchell, Brian E.", "Discipline", "2026-07-27"))
        self.assertEqual(self.e[1]["date"], "2022-03-04")
        self.assertEqual(self.e[6]["date"], "2026-07-28")
        self.assertIsNone(self.e[5]["date"])

    def test_links(self):
        self.assertEqual(self.e[0]["links"], [BASE + "Mitchell-Final-Order-D2026-16.pdf"])
        self.assertEqual(self.e[1]["links"], [BASE + "Graham%20Final%20Order%20D2022-13.pdf"])
        self.assertEqual(self.e[2]["links"], [BASE + "missing-D2025-13.pdf", BASE + "Matos%20(redacted).pdf"])
        self.assertEqual(self.e[3]["links"], [BASE + "Tech-18-6-13-2025-(redacted).pdf"])
        self.assertEqual(self.e[4]["links"], [])

    def test_dates_and_window(self):
        self.assertEqual(census.parse_date("1/2/2024"), "2024-01-02")
        self.assertEqual(census.parse_date("2024-01-02"), "2024-01-02")
        self.assertIsNone(census.parse_date("2/30/2024"))
        self.assertIsNone(census.parse_date("--"))
        self.assertTrue(census.in_window({"date": "2023-01-01"}))
        self.assertTrue(census.in_window({"date": "2026-11-10"}))
        self.assertFalse(census.in_window({"date": "2026-11-11"}))
        self.assertFalse(census.in_window({"date": None}))

    def test_has_proc(self):
        self.assertTrue(census.has_proc({"proceeding": "D2026-16"}, "D2026-16"))
        self.assertFalse(census.has_proc({"proceeding": "D2026-160"}, "D2026-16"))
        self.assertFalse(census.has_proc({"proceeding": "D2026-1"}, "D2026-16"))

    def test_build_frame(self):
        log = []
        docs, info, failed = run_job.build_frame(log, lambda u: PAGE.encode("utf-8"))
        self.assertEqual(failed, 0)
        self.assertEqual([d["proceeding"] for d in docs], ["D2026-16", "D2025-13", "Tech-18", "D2023-5"])
        self.assertEqual((info["in_window"], info["same_link_skipped"], info["no_link_in_window"]), (4, 1, 0))
        self.assertEqual(len({d["row_id"] for d in docs}), 4)

    def test_build_frame_failure(self):
        def boom(url):
            raise OSError("down")
        docs, info, failed = run_job.build_frame([], boom)
        self.assertEqual((docs, failed), ([], 1))
        self.assertIn("error", info)


class Classify(unittest.TestCase):
    def test_mitchell_style(self):
        r = census.classify(MITCHELL_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation", "guidance", "r11_101", "r11_804"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["r11_18"])
        self.assertIn("fake_cite", r["excerpts"])

    def test_matos_style(self):
        r = census.classify(MATOS_TEXT)
        self.assertTrue(r["fake_cite"])
        self.assertTrue(r["r11_18"])
        self.assertTrue(r["r11_101"])
        self.assertFalse(r["ai_mention"])
        self.assertFalse(r["guidance"])

    def test_other_not_flagged(self):
        r = census.classify(OTHER_TEXT)
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)

    def test_phrases(self):
        self.assertTrue(census.classify("The brief cited cases that do not exist.")["fake_cite"])
        self.assertFalse(census.classify("The record shows a conflict does not exist.")["fake_cite"])
        self.assertTrue(census.classify("Counsel filed an Al-generated brief.")["ai_mention"])
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertTrue(census.classify("See 89 FR 25,611.")["guidance"])

    def test_empty(self):
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_PLAIN)
        self.assertEqual(len(db["uspto_rows"]), 1)
        self.assertEqual(len(db["joined"]), 2)
        self.assertEqual(len(census.db_check(CSV_TWO)["uspto_rows"]), 2)

    def test_surname(self):
        self.assertEqual(census.surname("Mitchell, Brian E."), "Mitchell")
        self.assertEqual(census.surname("Brian E. Mitchell"), "Mitchell")
        self.assertEqual(census.surname("John Smith Jr."), "Smith")
        self.assertEqual(census.surname("--"), "")

    def test_in_db(self):
        db = census.db_check(CSV_PLAIN)
        self.assertTrue(census.in_db(db, {"respondent": "Mitchell, Brian E.", "proceeding": "D2026-16"}))
        self.assertFalse(census.in_db(db, {"respondent": "Anthony Matos", "proceeding": "D2025-13"}))
        dbp = census.db_check(CSV_PROC)
        self.assertTrue(census.in_db(dbp, {"respondent": "Anthony Matos", "proceeding": "D2025-13"}))
        self.assertFalse(census.in_db(dbp, {"respondent": "--", "proceeding": "D2025-1"}))
        self.assertFalse(census.in_db(None, {"respondent": "Mitchell", "proceeding": "D2026-16"}))


def _doc(proc, date, text, in_db, readable=True, status="ok"):
    d = {"proceeding": proc, "decision_text": "Final Order", "decision_type": "Discipline", "date": date,
         "respondent": "Mitchell, Brian E." if proc == "D2026-16" else "Someone Else", "readable": readable,
         "doc_status": status, "in_db": in_db, "row_id": "r-" + proc}
    if text is not None:
        d.update({k: v for k, v in census.classify(text).items() if k != "excerpts"})
    return d


def _docs():
    return [_doc("D2026-16", "2026-07-27", MITCHELL_TEXT, True),
            _doc("D2025-13", "2025-03-06", MATOS_TEXT, False),
            _doc("D2023-5", "2023-01-15", OTHER_TEXT, False),
            _doc("D2024-9", "2024-02-02", None, False, readable=False, status="http_404")]


class Grade(unittest.TestCase):
    def verdicts(self, docs, db):
        return {k: v["verdict"] for k, v in census.grade(docs, db, {})["predictions"].items()}

    def test_all_hold(self):
        v = self.verdicts(_docs(), census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P%d" % i: "held" for i in range(1, 10)})

    def test_db_variants(self):
        v = self.verdicts(_docs(), None)
        self.assertEqual((v["P8"], v["P9"]), ("not testable", "not testable"))
        v = self.verdicts(_docs(), census.db_check(CSV_TWO))
        self.assertEqual((v["P8"], v["P9"]), ("failed", "held"))

    def test_no_fake(self):
        v = self.verdicts(_docs()[2:], census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P2"], v["P3"], v["P4"]), ("not testable", "not testable", "failed", "held"))
        self.assertEqual((v["P5"], v["P6"], v["P7"], v["P9"]), ("not testable",) * 4)
        self.assertEqual(v["P8"], "failed")

    def test_outputs_have_no_names(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), {"entries": 4})
        self.assertEqual(res["counts"]["fake_cite"], 2)
        self.assertEqual(res["counts"]["fake_cite_proceedings"], 2)
        self.assertNotIn("Mitchell", json.dumps(res))
        md = census.results_md(res, {"x": 1})
        self.assertIn("D2026-16", md)
        self.assertNotIn("Mitchell", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["row_id", "proceeding"])
        self.assertEqual(len(rows), 5)
        self.assertNotIn("Mitchell", "\n".join(rows))


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_get(self, url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PLAIN.encode("utf-8"), "text/csv"
        if url == census.PAGE_URL:
            return PAGE.encode("utf-8"), "text/html"
        if url.endswith("missing-D2025-13.pdf"):
            raise run_job.urllib.error.HTTPError(url, 404, "nf", None, None)
        return b"%PDF-" + url.encode("utf-8"), "application/pdf"

    @staticmethod
    def fake_text(data):
        if b"Mitchell" in data:
            return MITCHELL_TEXT
        if b"Matos" in data:
            return MATOS_TEXT
        if b"Tech-18" in data:
            return "Petition denied."
        return OTHER_TEXT

    def patches(self):
        return [mock.patch.object(run_job, "DELAY_S", 0),
                mock.patch.object(run_job, "get_retry", self.fake_get),
                mock.patch.object(run_job, "pdf_text", self.fake_text),
                mock.patch.object(run_job, "wait_for_plan", lambda m, s: ({"sha": "a"}, {"sha": "b"}, s))]

    def run_main(self, extra=()):
        ps = self.patches() + list(extra)
        for p in ps:
            p.start()
        try:
            return run_job.main(["--out-dir", self.tmp])
        finally:
            for p in reversed(ps):
                p.stop()

    def test_main(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1)])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.tmp, "results.json"), encoding="utf-8") as fh:
            body = fh.read()
        res = json.loads(body)
        v = {k: x["verdict"] for k, x in res["predictions"].items()}
        self.assertEqual(v, {"P%d" % i: "held" for i in range(1, 10)})
        self.assertEqual(res["counts"]["in_frame"], 4)
        self.assertEqual(res["counts"]["readable"], 3)
        self.assertNotIn("Mitchell", body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        self.assertNotIn("Mitchell", rows)
        self.assertNotIn("redacted", rows)
        self.assertIn("D2025-13", rows)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        rc = self.run_main()
        self.assertEqual(rc, 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))

    def test_main_stops_parser_check(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1),
                            mock.patch.object(run_job, "MAX_BAD_DATE_NEW", 0)])
        self.assertEqual(rc, 7)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
