# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the ECAB fabricated-citation census (no network)."""
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

import census
import run_job

LABELS = {2024: ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"],
          2025: ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Nov", "Dec"],
          2026: ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct"]}
INDEX = ("<html><body><a href='#main'>skip</a><ul>"
         + "".join('<li><a href="/agencies/ecab/decisions/%d/%s">%s</a></li>' % (y, lab, lab)
                   for y in (2026, 2025, 2024) for lab in LABELS[y])
         + '<li><a href="/agencies/ecab/decisions/2023/Jun">Jun</a></li>'
         + '<li><a href="/agencies/ecab/decisions/2024/Jan">Jan again</a></li>'
         + '<li><a href="/agencies/ecab/decisions/fee_petition_orders">Fee petitions</a></li>'
         + '<li><a href="https://searchappeals.dol.gov/">Search</a></li></ul></body></html>')
HEADER = "<thead><tr><th>Docket No.</th><th>Date Issued</th><th>Parties</th></tr></thead>"
ROW = '<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>'
F = "/sites/dolgov/files/ecab/decisions/"


def page(rows):
    return ("<html><body><h1>Decisions</h1><table>" + HEADER + "<tbody>" + rows + "</tbody></table>"
            '<a href="/agencies/ecab/decisions">Return to index</a></body></html>')


def month_html(y, lab):
    up = lab[:3].upper()
    rows = ROW % (F + "%d/%s/24-0101.pdf" % (y, up), "24-0101", "%s 2, %d" % (lab, y), "A.B. and SECRET AGENCY") + \
        ROW % (F + "%d/%s/24-0102_O.pdf" % (y, up), "24-0102", "%s 9, %d" % (lab, y), "C.D. and SECRET AGENCY")
    if (y, lab) == (2024, "Jan"):     # a later page repeats a link from the first page read
        rows += ROW % (F + "2026/JAN/24-0101.pdf", "24-0101", "January 2, 2026", "A.B. and SECRET AGENCY")
    return page(rows)


JAN = {"year": 2026, "month": 1, "label": "Jan", "url": census.BASE + "/agencies/ecab/decisions/2026/Jan"}
JAN_PAGE = page(
    ROW % (F + "2026/JAN/23-0094.pdf", "23-0094", "January 5, 2026", "T.J. and U.S. POSTAL SERVICE, ATLANTA PR...")
    + ROW % (F + "2026/JAN/23-0477_O.pdf", "23-0477", "January 12, 2026", "S.C. and DEPARTMENT OF VETERANS AFFAIRS")
    + ROW % (F + "2026/JAN/22-0251_Reissue.pdf", "22-0251", "January 20, 2026", "G.F., widower of D.K. and X")
    + ROW % (F + "2026/JAN/25-898.pdf", "25-898", "December 30, 2025", "M.N. and Y")
    + ROW % (F + "2026/JAN/26-0261_O.pdf", "26-0261", "&nbsp;", "P.Q. and Z")
    + ROW % ("/sites/dolgov/files/other/form.pdf", "form", "January 1, 2026", "x")
    + '<tr><td colspan="3">There were no other decisions.</td></tr>')

FILLER = " The Board has duly considered the matter." * 15
FAKE_TEXT = ("Appearances: Appellant, pro se. On appeal, appellant cited cases that do not exist. The Board notes "
             "that appellant's brief relied on nonexistent decisions." + FILLER)
AI_TEXT = ("Appearances: Appellant, pro se. Appellant acknowledged that he used ChatGPT to draft his brief, and the "
           "Board was unable to locate the decisions he cited, which appear to be fabricated citations." + FILLER)
HALL_TEXT = "The medical report notes auditory hallucinations and depression. The claim was denied." + FILLER
LOCATE_TEXT = "Appellant, pro se. The Board could not find the case law appellant referenced." + FILLER
OTHER_TEXT = "ORDER DISMISSING APPEAL. Appellant, through counsel, requested dismissal." + FILLER
CSV_PLAIN = ("case_id,Case Name,Court,State(s),Date\n"
             "2625,In the Matter of X,USPTO,USA,2026-07-27\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08\n")
CSV_MENTION = CSV_PLAIN + '11,"Doe v. OPM (citing ECAB Docket No. 24-0101)",Fed. Cir.,USA,2026-09-01\n'
CSV_ECAB = CSV_PLAIN + "12,A.B. v. USPS,Employees' Compensation Appeals Board,USA,2026-10-01\n"


class Index(unittest.TestCase):
    def test_months(self):
        m = census.parse_index(INDEX.encode("utf-8"))
        self.assertEqual(len(m), 34)
        w = census.months_in_window(m)
        self.assertEqual(len(w), 33)
        self.assertEqual(w[0], {"year": 2026, "month": 1, "label": "Jan",
                                "url": "https://www.dol.gov/agencies/ecab/decisions/2026/Jan"})
        self.assertEqual([x["month"] for x in w if x["year"] == 2025], [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12])
        self.assertEqual(sum(1 for x in w if x["year"] == 2024), 12)


class Month(unittest.TestCase):
    def setUp(self):
        self.e, self.info = census.parse_month(JAN_PAGE.encode("utf-8"), JAN)

    def test_info(self):
        self.assertEqual((self.info["table_rows"], self.info["entries"], self.info["headers"]), (8, 5, 1))
        self.assertEqual((self.info["no_date"], self.info["no_docket"], self.info["date_month_mismatch"]), (1, 0, 1))
        self.assertEqual(self.info["kinds"], {"decision": 2, "order": 2, "reissue": 1})

    def test_fields(self):
        a = self.e[0]
        self.assertEqual((a["url"], a["stem"], a["docket"], a["kind"], a["date"], a["year"], a["month"]),
                         ("https://www.dol.gov" + F + "2026/JAN/23-0094.pdf", "23-0094", "23-0094", "decision",
                          "2026-01-05", 2026, 1))
        self.assertEqual(a["parties"], "T.J. and U.S. POSTAL SERVICE, ATLANTA PR...")
        self.assertEqual([x["kind"] for x in self.e], ["decision", "order", "reissue", "decision", "order"])
        self.assertEqual([x["docket"] for x in self.e], ["23-0094", "23-0477", "22-0251", "25-0898", "26-0261"])
        self.assertEqual((self.e[3]["date"], self.e[4]["date"]), ("2025-12-30", None))

    def test_dates(self):
        self.assertEqual([census.parse_date(x) for x in ("June 11, 2025", "Sept. 3, 2025", "6/11/2025",
                                                         "February 30, 2025", "Foo 3, 2025", "", None)],
                         ["2025-06-11", "2025-09-03", "2025-06-11", None, None, None, None])

    def test_row_id(self):
        self.assertEqual(len(census.row_id(self.e[0])), 12)
        self.assertNotEqual(census.row_id(self.e[0]), census.row_id(self.e[1]))


def fetch_pages(url):
    if url == census.INDEX_URL:
        return INDEX.encode("utf-8")
    m = re.search(r"/(\d{4})/([A-Za-z]+)$", url)
    return month_html(int(m.group(1)), m.group(2)).encode("utf-8")


class Frame(unittest.TestCase):
    def test_build_frame(self):
        log = []
        docs, info, failed = run_job.build_frame(log, fetch_pages, delay=0)
        self.assertEqual(failed, 0)
        self.assertEqual((info["months"], info["in_frame"], info["same_link_skipped"]), (33, 66, 1))
        self.assertEqual(info["in_frame_by_year"], {"2024": 24, "2025": 22, "2026": 20})
        self.assertEqual(info["kinds"], {"decision": 33, "order": 33})
        self.assertEqual((info["no_date_in_frame"], info["no_docket_in_frame"], info["empty_month_pages"]), (0, 0, 0))
        self.assertEqual(len({d["row_id"] for d in docs}), 66)

    def test_index_failure(self):
        def boom(url):
            raise OSError("down")
        docs, info, failed = run_job.build_frame([], boom, delay=0)
        self.assertEqual((docs, failed), ([], 1))
        self.assertIn("error", info)

    def test_month_failure(self):
        def some(url):
            if url.endswith("/2025/June"):
                raise OSError("down")
            return fetch_pages(url)
        log = []
        docs, info, failed = run_job.build_frame(log, some, delay=0)
        self.assertEqual((docs, failed), ([], 1))
        self.assertTrue(info["failed_month"].endswith("/2025/June"))

    def test_too_few_months(self):
        with mock.patch.object(census, "MIN_MONTHS", 40):
            docs, info, failed = run_job.build_frame([], fetch_pages, delay=0)
        self.assertEqual((docs, failed, info["months"]), ([], 1, 33))


class Classify(unittest.TestCase):
    def test_fake(self):
        r = census.classify(FAKE_TEXT)
        for k in ("fake_cite", "pro_se"):
            self.assertTrue(r[k], k)
        for k in ("ai_mention", "ai_citation", "hallucination", "hallucinated_cite", "not_located"):
            self.assertFalse(r[k], k)
        self.assertIn("fake_cite", r["excerpts"])

    def test_ai(self):
        r = census.classify(AI_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation", "not_located", "pro_se"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["hallucination"])

    def test_medical_hallucinations_not_flagged(self):
        r = census.classify(HALL_TEXT)
        self.assertTrue(r["hallucination"])
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)

    def test_phrases(self):
        r = census.classify("The brief contained hallucinated citations to Board precedent.")
        self.assertTrue(r["fake_cite"] and r["hallucinated_cite"])
        r = census.classify(LOCATE_TEXT)
        self.assertTrue(r["not_located"] and r["pro_se"])
        self.assertFalse(r["fake_cite"])
        self.assertFalse(census.classify("OWCP was unable to locate the claimant's file.")["not_located"])
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertFalse(census.classify(OTHER_TEXT)["pro_se"])
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS + census.EXTRA_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        self.assertEqual([(len(d["ecab_rows"]), len(d["mention"]), d["rows"]) for d in
                          (census.db_check(CSV_PLAIN), census.db_check(CSV_MENTION), census.db_check(CSV_ECAB))],
                         [(0, 0, 2), (0, 1, 3), (1, 1, 3)])

    def test_in_db(self):
        m = census.db_check(CSV_MENTION)
        self.assertTrue(census.in_db(m, {"docket": "24-0101"}))
        self.assertFalse(census.in_db(m, {"docket": "24-0102"}))
        self.assertFalse(census.in_db(census.db_check(CSV_ECAB), {"docket": "24-0101"}))
        self.assertFalse(census.in_db(None, {"docket": "24-0101"}))
        self.assertFalse(census.in_db(m, {"docket": None}))


def _doc(year, docket, text, kind="decision", readable=True, status="ok"):
    d = {"year": year, "month": 6, "date": "%d-06-01" % year, "docket": docket, "kind": kind,
         "parties": "Secret Agency", "url": "https://x/%s.pdf" % docket, "readable": readable, "doc_status": status,
         "in_db": False, "row_id": "r-" + docket}
    if text is not None:
        d.update({k: v for k, v in census.classify(text).items() if k != "excerpts"})
    return d


def _docs():
    return [_doc(2026, "26-0001", FAKE_TEXT), _doc(2025, "25-0001", AI_TEXT), _doc(2024, "24-0001", HALL_TEXT),
            _doc(2024, "24-0002", OTHER_TEXT, kind="order")]


class Grade(unittest.TestCase):
    def verdicts(self, docs, db):
        return {k: v["verdict"] for k, v in census.grade(docs, db, {})["predictions"].items()}

    def test_all_hold(self):
        self.assertEqual(self.verdicts(_docs(), census.db_check(CSV_PLAIN)), {"P%d" % i: "held" for i in range(1, 9)})

    def test_db_variants(self):
        self.assertEqual(self.verdicts(_docs(), None)["P1"], "not testable")
        self.assertEqual(self.verdicts(_docs(), census.db_check(CSV_ECAB))["P1"], "failed")
        docs = _docs()
        docs[0]["in_db"] = True
        self.assertEqual(self.verdicts(docs, census.db_check(CSV_PLAIN))["P1"], "failed")

    def test_no_fake(self):
        v = self.verdicts(_docs()[2:], census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P1": "held", "P2": "failed", "P3": "held", "P4": "held", "P5": "held", "P6": "failed",
                             "P7": "not testable", "P8": "held"})

    def test_many(self):
        v = self.verdicts([_doc(2026, "26-%04d" % i, AI_TEXT) for i in range(10)], census.db_check(CSV_PLAIN))
        self.assertEqual((v["P3"], v["P4"], v["P5"], v["P7"]), ("failed", "held", "failed", "held"))

    def test_readability(self):
        docs = _docs() + [_doc(2024, "24-0003", None, readable=False, status="http_404")]
        self.assertEqual(self.verdicts(docs, census.db_check(CSV_PLAIN))["P8"], "failed")

    def test_counts_and_outputs(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), {"in_frame": 4})
        c = res["counts"]
        self.assertEqual((c["in_frame"], c["readable"], c["fake_cite"], c["ai_mention"], c["ai_citation"],
                          c["hallucinated_cite"], c["not_located"], c["hallucination"], c["pro_se"]),
                         (4, 4, 2, 1, 1, 0, 1, 1, 2))
        self.assertEqual(res["other_flagged_decisions"], [])
        self.assertNotIn("Secret", json.dumps(res))
        md = census.results_md(res, {"x": 1})
        self.assertIn("26-0001", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["row_id", "year"])
        self.assertEqual(len(rows), 5)
        self.assertNotIn("Secret", "\n".join(rows))
        self.assertNotIn(".pdf", "\n".join(rows))
        res2 = census.grade(_docs() + [_doc(2025, "25-0002", LOCATE_TEXT)], census.db_check(CSV_PLAIN), {})
        self.assertEqual([r["docket"] for r in res2["other_flagged_decisions"]], ["25-0002"])


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def fake_get(url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PLAIN.encode("utf-8"), "text/csv"
        if url.endswith(".pdf"):
            return b"%PDF-" + url.encode("utf-8"), "application/pdf"
        return fetch_pages(url), "text/html"

    @staticmethod
    def fake_text(data):
        if b"2026/JAN/24-0101.pdf" in data:
            return AI_TEXT
        if b"2025/JUN/24-0101.pdf" in data:
            return FAKE_TEXT
        if b"2024/MAR/24-0102_O.pdf" in data:
            return ""
        return OTHER_TEXT

    def run_main(self, extra=()):
        ps = [mock.patch.object(run_job, "DELAY_S", 0),
              mock.patch.object(run_job, "get_retry", self.fake_get),
              mock.patch.object(run_job, "pdf_text", self.fake_text),
              mock.patch.object(run_job, "wait_for_plan", lambda m, s: ({"sha": "a"}, {"sha": "b"}, s))] + list(extra)
        for p in ps:
            p.start()
        try:
            return run_job.main(["--out-dir", self.tmp])
        finally:
            for p in reversed(ps):
                p.stop()

    def test_main(self):
        self.assertEqual(self.run_main([mock.patch.object(census, "MIN_FRAME", 1)]), 0)
        with open(os.path.join(self.tmp, "results.json"), encoding="utf-8") as fh:
            body = fh.read()
        v = {k: x["verdict"] for k, x in json.loads(body)["predictions"].items()}
        self.assertEqual(v, {"P1": "held", "P2": "held", "P3": "held", "P4": "held", "P5": "held", "P6": "failed",
                             "P7": "held", "P8": "held"})
        c = json.loads(body)["counts"]
        self.assertEqual((c["in_frame"], c["readable"], c["fake_cite"], c["ai_mention"]), (66, 65, 2, 1))
        self.assertNotIn("SECRET", body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        self.assertNotIn("SECRET", rows)
        self.assertNotIn(".pdf", rows)
        self.assertIn("24-0101", rows)
        self.assertEqual(len(os.listdir(os.path.join(self.tmp, "private", "texts"))), 2)

    def test_main_stops_small_frame(self):
        self.assertEqual(self.run_main(), 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))

    def test_main_stops_months(self):
        self.assertEqual(self.run_main([mock.patch.object(census, "MIN_MONTHS", 40)]), 5)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
