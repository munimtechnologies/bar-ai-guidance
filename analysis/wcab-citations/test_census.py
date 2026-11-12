# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the California WCAB fabricated-citation census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import census
import run_job

HEAD = ('<thead><tr><th class="headerSort">Date</th><th class="headerSort">Panel Decision</th></tr></thead>')
HEAD_STRONG = ('<thead><tr><th class="headerSort"><strong>Date</strong></th>'
               '<th class="headerSort">Panel Decision</th></tr></thead>')
ROW = ('<tr>\n\t<td>%s</td>\n  <td><a href="%s">%s</a>,  Applicant <br>\n vs.<br>\n  ACME INC.; '
       'ZURICH, Defendants </td>\n</tr>')
TEMPLATE = '<!--\n<tr>\n<td>&nbsp;</td>\n<td>,  Applicant <br>\n vs.<br></td>\n</tr>\n-->'
P = "/wcab/Panel-Decisions-"
T2026 = ROW % ("10/20/2026", P + "2026/Ann-SMITH-ADJ11111111.pdf", "Smith, Ann") + \
    ROW % ("6/26/2026", P + "2026/Gilberto-LOPEZ-MENDOZA-ADJ17889413.pdf", "Lopez Mendoza,  Gilberto") + \
    ROW % ("10/21/2026", P + "2026/Ann-SMITH-ADJ11111111.pdf", "Smith, Ann")
T2025 = ROW % ("12/1/2025", P + "2025/Bob-JONES-ADJ22222222-ADJ33333333.pdf", "Jones, Bob") + \
    '<tr><td>3/3/2025</td><td>Nolink, Carl, Applicant <br> vs.<br> ACME</td></tr>'
T2024 = ROW % ("7/7/2024", P + "2024/Dee-ROE-ADJ55555555.pdf", "Roe, Dee") + \
    ROW % ("&nbsp;", P + "2024/Eve-NODATE-ADJ66666666.pdf", "Nodate, Eve") + \
    ROW % ("5/5/2023", P + "2023/Old-CASE-ADJ44444444.pdf", "Case, Old")
PAGE = ("<html><head><script>var x = '1/1/2026';</script></head><body><h1>Panel decisions</h1>"
        "<table class='table'>" + HEAD + TEMPLATE + T2026 + "</table>"
        "<table class='table'>" + HEAD_STRONG + T2025 + "</table>"
        "<table class='table'>" + HEAD + T2024 + "</table></body></html>")

FILLER = " The petition for reconsideration is denied." * 15
FAKE_TEXT = ("OPINION AND DECISION. Petitioner cited cases that do not exist. There is no excuse for filing documents "
             "that contain fabricated citations. Sanctions under Labor Code section 5813. See Sedano v. Live Action "
             "General Engineering." + FILLER)
AI_TEXT = ("OPINION. Defendant admits that an artificial intelligence (AI) chatbot called ChatSOC generated the "
           "fabricated quotations. We issue a Notice of Intention to impose sanctions." + FILLER)
OTHER_TEXT = ("OPINION. The petition is denied. The fictitious business name statement was filed late. Labor Code "
              "section 5813 was not invoked." + FILLER)
CSV_PLAIN = ("case_id,Case Name,Court,State(s),Date\n"
             "2625,In the Matter of X,USPTO,USA,2026-07-27\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08\n")
CSV_ADJ = CSV_PLAIN + "11,Appeal citing ADJ11111111,Cal. Ct. App.,USA,2026-09-01\n"
CSV_WCAB = CSV_PLAIN + "12,Jones v. Acme,California Workers' Compensation Appeals Board,USA,2026-10-01\n"
URL = "https://www.dir.ca.gov/wcab/Panel-Decisions-"


class Listing(unittest.TestCase):
    def setUp(self):
        self.e, self.info = census.parse_listing(PAGE.encode("utf-8"))

    def test_rows_and_info(self):
        self.assertEqual([x["date"] for x in self.e],
                         ["2026-10-20", "2026-06-26", "2026-10-21", "2025-12-01", "2025-03-03", "2024-07-07", None,
                          "2023-05-05"])
        self.assertEqual((self.info["table_rows"], self.info["entries"], self.info["headers"]), (11, 8, 3))
        self.assertEqual((self.info["no_date"], self.info["no_link"], self.info["no_folder_year"],
                          self.info["no_adj"], self.info["date_folder_mismatch"]), (1, 1, 0, 0, 0))

    def test_fields(self):
        s = self.e[0]
        self.assertEqual((s["url"], s["folder_year"], s["adj"], s["name"], s["pdf_links"]),
                         (URL + "2026/Ann-SMITH-ADJ11111111.pdf", 2026, ["ADJ11111111"], "Smith, Ann", 1))
        self.assertEqual(self.e[3]["adj"], ["ADJ22222222", "ADJ33333333"])
        self.assertEqual((self.e[4]["url"], self.e[4]["folder_year"], self.e[4]["name"]), ("", None, "Nolink, Carl"))
        self.assertEqual(self.e[1]["name"], "Lopez Mendoza, Gilberto")

    def test_dates_window_known(self):
        self.assertEqual([census.parse_date(x) for x in ("6/26/2026", " 1/2/2025 ", "13/1/2026", "", "2026-01-01")],
                         ["2026-06-26", "2025-01-02", None, None, None])
        self.assertTrue(census.in_window({"folder_year": 2024}))
        self.assertFalse(census.in_window({"folder_year": 2023, "date": "2024-01-05"}))
        self.assertTrue(census.in_window({"folder_year": None, "date": "2025-03-03"}))
        self.assertFalse(census.in_window({}))
        self.assertTrue(census.is_known(self.e[1]))
        self.assertFalse(census.is_known(self.e[0]))
        self.assertFalse(census.is_known({"folder_year": 2024, "adj": ["ADJ17889413"]}))

    def test_row_id(self):
        self.assertNotEqual(census.row_id(self.e[0], 0), census.row_id(self.e[0], 1))
        self.assertEqual(len(census.row_id(self.e[0])), 12)

    def test_build_frame(self):
        log = []
        docs, info, failed = run_job.build_frame(log, lambda u: PAGE.encode("utf-8"))
        self.assertEqual(failed, 0)
        self.assertEqual([d["date"] for d in docs],
                         ["2026-10-20", "2026-06-26", "2025-12-01", "2025-03-03", "2024-07-07", None])
        self.assertEqual((info["entries"], info["in_frame"], info["same_link_skipped"], info["outside_years"]),
                         (8, 6, 1, 1))
        self.assertEqual((info["no_date_in_frame"], info["no_link_in_frame"], info["known_in_frame"]), (1, 1, 1))
        self.assertEqual(info["in_frame_by_year"], {"2024": 2, "2025": 2, "2026": 2})
        self.assertEqual(len({d["row_id"] for d in docs}), 6)

    def test_build_frame_failure(self):
        def boom(url):
            raise OSError("down")
        docs, info, failed = run_job.build_frame([], boom)
        self.assertEqual((docs, failed), ([], 1))
        self.assertIn("error", info)


class Classify(unittest.TestCase):
    def test_fake(self):
        r = census.classify(FAKE_TEXT)
        for k in ("fake_cite", "sedano", "lc5813"):
            self.assertTrue(r[k], k)
        for k in ("ai_mention", "ai_citation", "hallucination", "noland", "nit"):
            self.assertFalse(r[k], k)
        self.assertIn("fake_cite", r["excerpts"])

    def test_ai(self):
        r = census.classify(AI_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation", "nit"):
            self.assertTrue(r[k], k)
        for k in ("sedano", "lc5813", "noland"):
            self.assertFalse(r[k], k)

    def test_other_not_flagged(self):
        r = census.classify(OTHER_TEXT)
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)
        self.assertTrue(r["lc5813"])

    def test_phrases(self):
        self.assertTrue(census.classify("The petition appeared to create citations that did not exist.")["fake_cite"])
        self.assertTrue(census.classify("We are perturbed by such apparently fake citations.")["fake_cite"])
        self.assertTrue(census.classify("It used ChatSOC.")["ai_mention"])
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertTrue(census.classify("a Notice of Intent to Impose Sanctions issued")["nit"])
        self.assertTrue(census.classify("notice of intention to impose sanction")["nit"])
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS + census.EXTRA_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_PLAIN)
        self.assertEqual((len(db["wcab_rows"]), len(db["joined"])), (0, 2))
        self.assertEqual(len(census.db_check(CSV_WCAB)["wcab_rows"]), 1)

    def test_tokens(self):
        self.assertEqual(census.name_tokens("Lopez Mendoza, Gilberto"), ["Lopez", "Mendoza", "Gilberto"])
        self.assertEqual(census.name_tokens("Smith, Ann"), ["Smith"])

    def test_in_db(self):
        e1 = {"adj": ["ADJ11111111"], "name": "Smith, Ann"}
        e1b = {"adj": ["ADJ1111111"], "name": "Smith, Ann"}
        e3 = {"adj": ["ADJ22222222", "ADJ33333333"], "name": "Jones, Bob"}
        self.assertTrue(census.in_db(census.db_check(CSV_ADJ), e1))
        self.assertFalse(census.in_db(census.db_check(CSV_ADJ), e1b))
        self.assertTrue(census.in_db(census.db_check(CSV_WCAB), e3))
        self.assertFalse(census.in_db(census.db_check(CSV_WCAB), e1))
        self.assertFalse(census.in_db(census.db_check(CSV_PLAIN), e3))
        self.assertFalse(census.in_db(None, e3))


def _doc(year, adj, text, known=False, readable=True, status="ok"):
    d = {"folder_year": year, "date": "%d-06-01" % year, "adj": [adj], "name": "Secret Name", "readable": readable,
         "doc_status": status, "in_db": False, "row_id": "r-%d-%s" % (year, adj[3:]), "known": known}
    if text is not None:
        d.update({k: v for k, v in census.classify(text).items() if k != "excerpts"})
    return d


def _docs():
    docs = [_doc(int(y), a, FAKE_TEXT, known=True) for y, a in census.KNOWN]
    docs += [_doc(2026, "ADJ9000000%d" % i, FAKE_TEXT) for i in range(6)]
    docs += [_doc(2024, "ADJ80000000", OTHER_TEXT)]
    return docs


class Grade(unittest.TestCase):
    def verdicts(self, docs, db):
        return {k: v["verdict"] for k, v in census.grade(docs, db, {})["predictions"].items()}

    def test_all_hold(self):
        v = self.verdicts(_docs(), census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P%d" % i: "held" for i in range(1, 10)})

    def test_db_variants(self):
        self.assertEqual(self.verdicts(_docs(), None)["P7"], "not testable")
        self.assertEqual(self.verdicts(_docs(), census.db_check(CSV_WCAB))["P7"], "failed")

    def test_no_fake(self):
        v = self.verdicts(_docs()[-1:], census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P2"], v["P3"], v["P8"], v["P9"]), ("failed", "failed", "held", "failed", "held"))
        self.assertEqual((v["P4"], v["P5"], v["P6"], v["P7"]), ("not testable",) * 4)

    def test_readability(self):
        docs = _docs() + [_doc(2024, "ADJ70000000", None, readable=False, status="http_404")]
        self.assertEqual(self.verdicts(docs, census.db_check(CSV_PLAIN))["P9"], "failed")

    def test_counts_and_outputs(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), {"entries": 13})
        c = res["counts"]
        self.assertEqual((c["in_frame"], c["readable"], c["fake_cite"], c["fake_cite_cases"], c["lc5813"]),
                         (13, 13, 12, 10, 13))
        self.assertNotIn("Secret", json.dumps(res))
        md = census.results_md(res, {"x": 1})
        self.assertIn("ADJ17550375", md)
        self.assertNotIn("Secret", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["row_id", "folder_year"])
        self.assertEqual(len(rows), 14)
        self.assertNotIn("Secret", "\n".join(rows))
        self.assertNotIn("ADJ80000000", "\n".join(rows))


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_get(self, url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PLAIN.encode("utf-8"), "text/csv"
        if url == census.LISTING_URL:
            return PAGE.encode("utf-8"), "text/html"
        return b"%PDF-" + url.encode("utf-8"), "application/pdf"

    @staticmethod
    def fake_text(data):
        if b"SMITH" in data or b"LOPEZ" in data:
            return FAKE_TEXT
        if b"JONES" in data:
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
        self.assertEqual(v, {"P1": "failed", "P2": "failed", "P3": "held", "P4": "held", "P5": "held",
                             "P6": "failed", "P7": "held", "P8": "failed", "P9": "failed"})
        c = res["counts"]
        self.assertEqual((c["in_frame"], c["readable"], c["fake_cite"], c["fake_cite_cases"]), (6, 5, 3, 3))
        for name in ("Smith", "SMITH", "Jones", "Lopez", "LOPEZ", "Nolink", "Secret"):
            self.assertNotIn(name, body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        for name in ("Smith", "SMITH", "Jones", "Lopez", "Roe", ".pdf", "ADJ55555555"):
            self.assertNotIn(name, rows)
        self.assertIn("ADJ11111111", rows)
        self.assertIn("ADJ22222222+ADJ33333333", rows)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        self.assertEqual(self.run_main(), 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))

    def test_main_stops_parser_check(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1), mock.patch.object(run_job, "MIN_HEADERS", 4)])
        self.assertEqual(rc, 7)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
