# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the California Office of Tax Appeals census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import census
import run_job

BASE = "https://ota.ca.gov/2026-franchise-income-tax-opinions/"
UP = "https://ota.ca.gov/wp-content/uploads/sites/54/"
HEAD = ("<tr><th>Decisions</th><th>Month</th><th>Year</th><th>Cite</th><th>Decision Type</th>"
        "<th>Issues</th></tr>")
PAGE = """<html><head><script>var c = "2026-OTA-999";</script></head><body>
<table><thead>""" + HEAD + """</thead>
<tbody>
<tr><td><a href="UP2026/11/N.-Yacoub.pdf">N. Yacoub</a></td><td>November</td><td>2026</td><td>2026-OTA-564</td><td>Nonprecedential</td><td>Statute of limitations</td></tr>
<tr><td><a href="/wp-content/uploads/sites/54/2026/07/A Smith.pdf">A. Smith</a></td><td>July</td><td>2026</td><td>2026-OTA-311P</td><td>Pending Precedential</td><td>Fake cites</td></tr>
<tr><td><a href="UP2026/10/Zaragoza.pdf">M. Zaragoza</a></td><td>Oct</td><td>2026</td><td>2026=OTA=551</td><td>Nonprecedential</td><td>x</td></tr>
<tr><td>B. Nolink</td><td>March</td><td>2026</td><td>2026-OTA-100</td><td>Nonprecedential</td><td>y</td></tr>
<tr><td><a href="UP2023/12/Old-Co.pdf">Old Co</a></td><td>December</td><td>2023</td><td>2023-OTA-700</td><td>Nonprecedential</td><td>z</td></tr>
<tr><td><a href="UP2026/11/N.-Yacoub.pdf">N. Yacoub (dup)</a></td><td>November</td><td>2026</td><td>2026-OTA-564</td><td>Nonprecedential</td><td>dup</td></tr>
<tr><td><a href="UP2026/06/No-Cite.pdf">No Cite</a></td><td>June</td><td>2026</td><td>pending</td><td>Nonprecedential</td><td>w</td></tr>
</tbody></table></body></html>""".replace("UP", UP)
EMPTY = "<html><body><table>" + HEAD + "</table></body></html>"

FILLER = " The action of respondent is sustained." * 15
FAKE_TEXT = ("OPINION. Appellant's brief cites several cases that do not exist. These hallucinated or fictitious "
             "citations are concerning and inappropriate. See Noland v. Land of the Free, L.P. (2025) 114 "
             "Cal.App.5th 426." + FILLER)
AI_TEXT = ("OPINION. Appellant states that the brief was drafted with generative AI and that the fabricated case "
           "law was not checked." + FILLER)
OTHER_TEXT = ("OPINION. Appellant failed to show error in the proposed assessment. The fictitious business name "
              "statement was filed late." + FILLER)
CSV_PLAIN = ("case_id,Case Name,Court,State(s),Date\n"
             "2625,In the Matter of X,USPTO,USA,2026-07-27\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08\n")
CSV_CITE = CSV_PLAIN + "11,Appeal citing 2026-OTA-311P,N.D. Cal.,USA,2026-09-01\n"
CSV_OTA = CSV_PLAIN + "12,Appeal of Zaragoza,California Office of Tax Appeals,USA,2026-10-01\n"


class Listing(unittest.TestCase):
    def setUp(self):
        self.e, self.info = census.parse_listing(PAGE.encode("utf-8"), BASE, "fit", 2026)

    def test_rows_and_header(self):
        self.assertEqual([x["cite"] for x in self.e],
                         ["2026-OTA-564", "2026-OTA-311P", "2026-OTA-551", "2026-OTA-100", "2023-OTA-700",
                          "2026-OTA-564", ""])
        self.assertTrue(self.info["header_found"])
        self.assertEqual((self.info["table_rows"], self.info["entries"]), (8, 7))
        self.assertEqual((self.info["no_cite"], self.info["no_month"]), (1, 0))
        self.assertEqual((self.info["year_mismatch"], self.info["page_year_mismatch"]), (0, 1))

    def test_fields(self):
        s = self.e[1]
        self.assertEqual((s["name"], s["month"], s["year"], s["suffix"], s["decision_type"], s["issues"]),
                         ("A. Smith", 7, 2026, "P", "Pending Precedential", "Fake cites"))
        self.assertEqual(self.e[2]["month"], 10)
        self.assertEqual(self.e[6]["year"], 2026)
        self.assertIsNone(self.e[6]["cite_year"])

    def test_links(self):
        self.assertEqual(self.e[0]["links"], [UP + "2026/11/N.-Yacoub.pdf"])
        self.assertEqual(self.e[1]["links"], [UP + "2026/07/A%20Smith.pdf"])
        self.assertEqual(self.e[3]["links"], [])

    def test_cite_month_window(self):
        self.assertEqual(census.parse_cite("2026=OTA=551"), ("2026-OTA-551", 2026, 551, ""))
        self.assertEqual(census.parse_cite("2025-OTA-619SCP"), ("2025-OTA-619SCP", 2025, 619, "SCP"))
        self.assertEqual(census.parse_cite("2026-OTA-001"), ("2026-OTA-001", 2026, 1, ""))
        self.assertEqual(census.parse_cite("2024 – OTA – 685"), ("2024-OTA-685", 2024, 685, ""))
        self.assertIsNone(census.parse_cite("pending"))
        self.assertEqual([census.parse_month(m) for m in ("May", "Sept.", "Oct", "", "Ma")], [5, 9, 10, None, None])
        self.assertTrue(census.in_window({"cite_year": 2024}))
        self.assertFalse(census.in_window({"cite_year": 2027}))
        self.assertTrue(census.in_window({"cite_year": None, "year": 2025}))
        self.assertFalse(census.in_window({}))
        self.assertEqual([census.is_precedential({"decision_type": t}) for t in
                          ("Precedential", "Pending Precedential", "Nonprecedential", "")], [True, True, False, False])

    def test_row_id(self):
        self.assertNotEqual(census.row_id(self.e[0], 0), census.row_id(self.e[0], 1))
        self.assertEqual(len(census.row_id(self.e[0])), 12)

    def test_build_frame(self):
        log = []
        fetch = lambda u: (PAGE if u == census.PAGES[0][2] else EMPTY).encode("utf-8")
        with mock.patch.object(run_job, "DELAY_S", 0):
            docs, info, failed = run_job.build_frame(log, fetch)
        self.assertEqual(failed, 0)
        self.assertEqual([d["cite"] for d in docs], ["2026-OTA-564", "2026-OTA-311P", "2026-OTA-551", "2026-OTA-100", ""])
        self.assertEqual((info["entries"], info["in_frame"], info["same_link_skipped"], info["outside_years"]), (7, 5, 1, 1))
        self.assertEqual((info["no_cite"], info["no_link_in_frame"], info["duplicate_cites"], info["headers_missing"]),
                         (1, 1, 0, 0))
        self.assertEqual(len({d["row_id"] for d in docs}), 5)

    def test_build_frame_failure(self):
        def boom(url):
            raise OSError("down")
        with mock.patch.object(run_job, "DELAY_S", 0):
            docs, info, failed = run_job.build_frame([], boom)
        self.assertEqual((docs, failed), ([], 6))
        self.assertIn("error", info["pages"][0])


class Classify(unittest.TestCase):
    def test_fake(self):
        r = census.classify(FAKE_TEXT)
        for k in ("fake_cite", "hallucination", "noland"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["ai_mention"])
        self.assertFalse(r["ai_citation"])
        self.assertIn("fake_cite", r["excerpts"])

    def test_ai(self):
        r = census.classify(AI_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["noland"])

    def test_other_not_flagged(self):
        r = census.classify(OTHER_TEXT)
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)

    def test_phrases(self):
        self.assertTrue(census.classify("The OTA could not locate the cases appellant cited.")["fake_cite"])
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertTrue(census.classify("An AI-generated brief.")["ai_mention"])
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_PLAIN)
        self.assertEqual((len(db["ota_rows"]), len(db["joined"])), (0, 2))
        self.assertEqual(len(census.db_check(CSV_OTA)["ota_rows"]), 1)

    def test_tokens(self):
        self.assertEqual(census.name_tokens("Kimco Realty Corporation and Subsidiaries, PFR Opinion"), ["Kimco", "Realty"])

    def test_in_db(self):
        e311 = {"name": "A. Smith", "cite_year": 2026, "cite_num": 311}
        e31 = {"name": "A. Smith", "cite_year": 2026, "cite_num": 31}
        ez = {"name": "M. Zaragoza", "cite_year": 2026, "cite_num": 551}
        self.assertTrue(census.in_db(census.db_check(CSV_CITE), e311))
        self.assertFalse(census.in_db(census.db_check(CSV_CITE), e31))
        self.assertTrue(census.in_db(census.db_check(CSV_OTA), ez))
        self.assertFalse(census.in_db(census.db_check(CSV_OTA), e311))
        self.assertFalse(census.in_db(census.db_check(CSV_PLAIN), ez))
        self.assertFalse(census.in_db(None, ez))
        self.assertFalse(census.in_db(census.db_check(CSV_CITE), {"name": "x", "cite_year": None}))


def _doc(cite, page, dtype, text, readable=True, status="ok"):
    c = census.parse_cite(cite)
    d = {"cite": cite, "cite_year": c[1], "cite_num": c[2], "year": c[1], "month": 7, "page": page,
         "decision_type": dtype, "name": "Secret Name", "issues": "", "readable": readable, "doc_status": status,
         "in_db": False, "row_id": "r-" + cite}
    if text is not None:
        d.update({k: v for k, v in census.classify(text).items() if k != "excerpts"})
    return d


def _docs():
    return [_doc("2026-OTA-311P", "fit", "Pending Precedential", FAKE_TEXT),
            _doc("2026-OTA-400", "bt", "Nonprecedential", AI_TEXT),
            _doc("2025-OTA-100", "fit", "Nonprecedential", FAKE_TEXT),
            _doc("2024-OTA-50", "fit", "Nonprecedential", OTHER_TEXT)]


class Grade(unittest.TestCase):
    def verdicts(self, docs, db):
        return {k: v["verdict"] for k, v in census.grade(docs, db, {})["predictions"].items()}

    def test_all_hold(self):
        v = self.verdicts(_docs(), census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P%d" % i: "held" for i in range(1, 10)})

    def test_db_variants(self):
        self.assertEqual(self.verdicts(_docs(), None)["P8"], "not testable")
        self.assertEqual(self.verdicts(_docs(), census.db_check(CSV_OTA))["P8"], "failed")

    def test_no_fake(self):
        v = self.verdicts(_docs()[3:], census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P2"], v["P3"], v["P9"]), ("failed", "failed", "held", "held"))
        self.assertEqual((v["P4"], v["P5"], v["P6"], v["P7"], v["P8"]), ("not testable",) * 5)

    def test_readability(self):
        docs = _docs() + [_doc("2024-OTA-60", "bt", "Nonprecedential", None, readable=False, status="http_404")]
        self.assertEqual(self.verdicts(docs, census.db_check(CSV_PLAIN))["P9"], "failed")

    def test_outputs_have_no_names(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), {"entries": 4})
        self.assertEqual(res["counts"]["fake_cite"], 3)
        self.assertNotIn("Secret", json.dumps(res))
        md = census.results_md(res, {"x": 1})
        self.assertIn("2026-OTA-311P", md)
        self.assertNotIn("Secret", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["row_id", "cite"])
        self.assertEqual(len(rows), 5)
        self.assertNotIn("Secret", "\n".join(rows))


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_get(self, url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PLAIN.encode("utf-8"), "text/csv"
        if url == census.PAGES[0][2]:
            return PAGE.encode("utf-8"), "text/html"
        if url in [p[2] for p in census.PAGES]:
            return EMPTY.encode("utf-8"), "text/html"
        return b"%PDF-" + url.encode("utf-8"), "application/pdf"

    @staticmethod
    def fake_text(data):
        if b"Smith" in data:
            return FAKE_TEXT
        if b"Zaragoza" in data:
            return AI_TEXT
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
        self.assertEqual((v["P1"], v["P2"], v["P8"], v["P9"]), ("held", "held", "held", "failed"))
        self.assertEqual((res["counts"]["in_frame"], res["counts"]["readable"], res["counts"]["fake_cite"]), (5, 4, 2))
        for name in ("Smith", "Zaragoza", "Yacoub"):
            self.assertNotIn(name, body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        for name in ("Smith", "Zaragoza", "Yacoub", ".pdf"):
            self.assertNotIn(name, rows)
        self.assertIn("2026-OTA-311P", rows)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        self.assertEqual(self.run_main(), 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))

    def test_main_stops_parser_check(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1), mock.patch.object(run_job, "MAX_NO_CITE", 0)])
        self.assertEqual(rc, 7)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
