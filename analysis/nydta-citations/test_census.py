# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the New York Division of Tax Appeals census (no network)."""
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from unittest import mock

import census
import run_job

BASE = "https://www.dta.ny.gov/determinations/"
PDF = "https://www.dta.ny.gov/pdf/determinations/"
HEAD = ('<tr><td><a href="/pdf/determinations/852742.det.pdf">Name</a></td>'
        '<td><a href="/pdf/determinations/852742.det.pdf">Number</a></td>'
        '<td><a href="/pdf/determinations/852742.det.pdf">Date</a></td></tr>')
PAGE = """<html><head><script>var x = "851000 Name Date";</script></head><body>
<table><tr><td><a href="/x">Home</a></td><td>About</td><td>Contact</td></tr></table>
<table>""" + HEAD + """
<tr><td><a href="/pdf/determinations/851687.det.pdf">Bianca Smith</a></td><td>851687</td><td>October 29, 2026</td></tr>
<tr><td><a href="/pdf/determinations/831253%20and%20831264.det.pdf">Jacob Gutman et al</a></td><td>831253 and 831264</td><td>Apil 6, 2023</td></tr>
<tr><td><a href="/pdf/determinations/829765. det.pdf">Zed Corp.</a></td><td>829765</td><td>May 29, 2925</td></tr>
<tr><td>No Link Person</td><td>830000</td><td>October 9. 2025</td></tr>
<tr><td><a href="/pdf/determinations/851687.det.pdf">Bianca Smith (dup)</a></td><td>851687</td><td>October 29, 2026</td></tr>
<tr><td><a href="/pdf/determinations/850725.ord.2.docx">Docx Petitioner</a></td><td>pending</td><td>November 24,2021</td></tr>
</table></body></html>"""
EMPTY = "<html><body><table>" + HEAD + "</table></body></html>"

FILLER = " The notice of determination is sustained." * 15
FAKE_TEXT = ("DETERMINATION. Petitioner's brief cites several cases that do not exist. These hallucinated or "
             "fictitious citations are concerning." + FILLER)
AI_TEXT = ("DETERMINATION. Petitioner states that the brief was drafted with generative AI and that the fabricated "
           "case law was not checked." + FILLER)
OTHER_TEXT = ("DETERMINATION. Petitioner failed to show error in the notice of deficiency. The fictitious business "
              "name statement was filed late." + FILLER)
CSV_PLAIN = ("case_id,Case Name,Court,State(s),Date\n"
             "2625,In the Matter of X,USPTO,USA,2026-07-27\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08\n")
CSV_NUM = CSV_PLAIN + "11,Appeal from DTA No. 851687,SC New York,USA,2026-09-01\n"
CSV_MULTI = CSV_PLAIN + "13,Review of DTA Nos. 831253 and 831264,SC New York,USA,2026-09-02\n"
CSV_TRIB = CSV_PLAIN + "12,Matter of Zaragoza v Tax Appeals Tribunal,App. NY (3d),USA,2026-10-01\n"


def make_docx(xml_body):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<w:document><w:body>" + xml_body + "</w:body></w:document>")
    return buf.getvalue()


class Listing(unittest.TestCase):
    def setUp(self):
        self.e, self.info = census.parse_listing(PAGE.encode("utf-8"), BASE, "det")

    def test_rows_and_header(self):
        self.assertEqual([x["number"] for x in self.e], ["851687", "831253", "829765", "830000", "851687", ""])
        self.assertTrue(self.info["header_found"])
        self.assertEqual((self.info["table_rows"], self.info["entries"]), (8, 6))
        self.assertEqual((self.info["no_number"], self.info["no_year"], self.info["no_month"], self.info["no_link"]),
                         (1, 1, 0, 1))

    def test_fields(self):
        g = self.e[1]
        self.assertEqual((g["name"], g["numbers"], g["year"], g["month"], g["day"], g["page"]),
                         ("Jacob Gutman et al", ["831253", "831264"], 2023, 4, 6, "det"))
        self.assertEqual((self.e[2]["year"], self.e[2]["month"]), (None, 5))
        self.assertEqual((self.e[3]["year"], self.e[3]["month"], self.e[3]["day"]), (2025, 10, 9))
        self.assertEqual((self.e[5]["year"], self.e[5]["month"], self.e[5]["day"]), (2021, 11, 24))

    def test_links(self):
        self.assertEqual(self.e[0]["links"], [PDF + "851687.det.pdf"])
        self.assertEqual(self.e[1]["links"], [PDF + "831253%20and%20831264.det.pdf"])
        self.assertEqual(self.e[2]["links"], [PDF + "829765.%20det.pdf"])
        self.assertEqual(self.e[3]["links"], [])
        self.assertEqual(self.e[5]["links"], [PDF + "850725.ord.2.docx"])

    def test_no_header(self):
        e, info = census.parse_listing("<table><tr><td>a</td><td>851687</td><td>May 1, 2026</td></tr></table>", BASE)
        self.assertEqual((e, info["header_found"]), ([], False))

    def test_dates_numbers(self):
        cases = {"October 29, 2026": (2026, 10, 29), "Apil 6, 2023": (2023, 4, 6), "May 29, 2925": (None, 5, 29),
                 "October 9. 2025": (2025, 10, 9), "November 24,2021": (2021, 11, 24), "June 05, 2025": (2025, 6, 5),
                 "Sept. 3, 2024": (2024, 9, 3), "": (None, None, None), "2026-10-29": (None, None, None)}
        for raw, want in cases.items():
            self.assertEqual(census.parse_date(raw), want, raw)
        self.assertEqual([census.parse_month(m) for m in ("Ma", "Febuary", "Xyz", "may")], [None, 2, None, 5])
        self.assertEqual(census.parse_numbers("850386/850388"), ["850386", "850388"])
        self.assertEqual(census.parse_numbers("DTA No. 851687 and 851687"), ["851687"])
        self.assertEqual(census.parse_numbers("8516870 pending"), [])
        self.assertTrue(census.is_tribunal({"page": "dec"}))
        self.assertTrue(census.is_tribunal({"page": "decord"}))
        self.assertFalse(census.is_tribunal({"page": "det"}))

    def test_row_id(self):
        self.assertNotEqual(census.row_id(self.e[0], 0), census.row_id(self.e[0], 1))
        self.assertEqual(len(census.row_id(self.e[0])), 12)

    def test_build_frame(self):
        log = []
        fetch = lambda u: (PAGE if u == census.PAGES[0][1] else EMPTY).encode("utf-8")
        with mock.patch.object(run_job, "DELAY_S", 0):
            docs, info, failed = run_job.build_frame(log, fetch)
        self.assertEqual(failed, 0)
        self.assertEqual([d["number"] for d in docs], ["851687", "831253", "829765", "830000", ""])
        self.assertEqual((info["entries"], info["in_frame"], info["same_link_skipped"]), (6, 5, 1))
        self.assertEqual((info["no_number"], info["no_year"], info["no_link_in_frame"], info["duplicate_numbers"],
                          info["headers_missing"]), (1, 1, 1, 0, 0))
        self.assertEqual(len({d["row_id"] for d in docs}), 5)

    def test_build_frame_failure(self):
        def boom(url):
            raise OSError("down")
        with mock.patch.object(run_job, "DELAY_S", 0):
            docs, info, failed = run_job.build_frame([], boom)
        self.assertEqual((docs, failed), ([], 4))
        self.assertIn("error", info["pages"][0])


class Files(unittest.TestCase):
    def test_docx(self):
        data = make_docx("<w:p><w:r><w:t>Hello &amp; world</w:t></w:r></w:p><w:p><w:r><w:t>Next</w:t></w:r></w:p>")
        self.assertEqual(run_job.kind_of(data), "docx")
        self.assertEqual(run_job.docx_text(data), "Hello & world\nNext\n")

    def test_kinds(self):
        self.assertEqual(run_job.kind_of(b"%PDF-1.4 x"), "pdf")
        self.assertIsNone(run_job.kind_of(b"<html>not found</html>"))
        self.assertIsNone(run_job.kind_of(b"PK\x03\x04broken"))


class Classify(unittest.TestCase):
    def test_fake(self):
        r = census.classify(FAKE_TEXT)
        self.assertTrue(r["fake_cite"])
        self.assertTrue(r["hallucination"])
        self.assertFalse(r["ai_mention"])
        self.assertFalse(r["ai_citation"])
        self.assertIn("fake_cite", r["excerpts"])

    def test_ai(self):
        r = census.classify(AI_TEXT)
        for k in ("fake_cite", "ai_mention", "ai_citation"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["hallucination"])

    def test_other_not_flagged(self):
        r = census.classify(OTHER_TEXT)
        for k in census.FLAG_KEYS:
            self.assertFalse(r[k], k)

    def test_phrases(self):
        self.assertTrue(census.classify("We could not locate the cases petitioner cited.")["fake_cite"])
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertTrue(census.classify("An AI-generated brief.")["ai_mention"])
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_PLAIN)
        self.assertEqual((len(db["ny_tax_rows"]), len(db["joined"])), (0, 2))
        self.assertEqual(len(census.db_check(CSV_TRIB)["ny_tax_rows"]), 1)
        self.assertEqual(len(census.db_check(CSV_NUM)["ny_tax_rows"]), 1)

    def test_tokens(self):
        self.assertEqual(census.name_tokens("Jacob Gutman et al"), ["Jacob", "Gutman"])
        self.assertEqual(census.name_tokens("Matter of Petition of Kimco Realty Corporation"), ["Kimco", "Realty"])

    def test_in_db(self):
        nobody = {"name": "Q. Nobody", "numbers": ["851687"]}
        self.assertTrue(census.in_db(census.db_check(CSV_NUM), nobody))
        self.assertFalse(census.in_db(census.db_check(CSV_NUM), {"name": "Q. Nobody", "numbers": ["851688"]}))
        self.assertTrue(census.in_db(census.db_check(CSV_MULTI), {"name": "Q. Nobody", "numbers": ["831264"]}))
        z = {"name": "M. Zaragoza", "numbers": ["850001"]}
        self.assertTrue(census.in_db(census.db_check(CSV_TRIB), z))
        self.assertFalse(census.in_db(census.db_check(CSV_TRIB), {"name": "A. Smith", "numbers": ["850002"]}))
        self.assertFalse(census.in_db(census.db_check(CSV_PLAIN), z))
        self.assertFalse(census.in_db(None, z))


def _doc(number, page, year, text, readable=True, status="ok"):
    d = {"number": number, "numbers": [number], "page": page, "year": year, "month": 7, "name": "Secret Name",
         "readable": readable, "doc_status": status, "in_db": False, "row_id": "r-" + number}
    if text is not None:
        d.update({k: v for k, v in census.classify(text).items() if k != "excerpts"})
    return d


def _docs():
    return [_doc("851687", "det", 2026, FAKE_TEXT),
            _doc("851688", "detord", 2025, AI_TEXT),
            _doc("851689", "dec", 2024, OTHER_TEXT),
            _doc("851690", "decord", 2026, OTHER_TEXT)]


class Grade(unittest.TestCase):
    def verdicts(self, docs, db):
        return {k: v["verdict"] for k, v in census.grade(docs, db, {})["predictions"].items()}

    def test_all_hold(self):
        v = self.verdicts(_docs(), census.db_check(CSV_PLAIN))
        self.assertEqual(v, {"P%d" % i: "held" for i in range(1, 9)})

    def test_db_variants(self):
        self.assertEqual(self.verdicts(_docs(), None)["P6"], "not testable")
        self.assertEqual(self.verdicts(_docs(), census.db_check(CSV_TRIB))["P6"], "failed")

    def test_failures(self):
        docs = _docs() + [_doc("851691", "dec", 2024, FAKE_TEXT), _doc("851692", "det", None, FAKE_TEXT)]
        v = self.verdicts(docs, census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P2"], v["P5"], v["P8"]), ("failed", "failed", "failed", "failed"))
        self.assertEqual((v["P3"], v["P4"], v["P6"], v["P7"]), ("held", "held", "held", "held"))

    def test_no_fake(self):
        v = self.verdicts(_docs()[2:], census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P2"], v["P3"], v["P5"], v["P6"]),
                         ("held", "held", "held", "held", "not testable"))

    def test_many_ai(self):
        docs = [_doc("8600%02d" % i, "det", 2026, AI_TEXT) for i in range(10)]
        v = self.verdicts(docs, census.db_check(CSV_PLAIN))
        self.assertEqual((v["P1"], v["P3"], v["P4"]), ("failed", "failed", "failed"))

    def test_readability(self):
        docs = _docs() + [_doc("851699", "det", 2026, None, readable=False, status="http_404")]
        self.assertEqual(self.verdicts(docs, census.db_check(CSV_PLAIN))["P7"], "failed")

    def test_outputs_have_no_names(self):
        res = census.grade(_docs(), census.db_check(CSV_PLAIN), {"entries": 4})
        self.assertEqual(res["counts"]["fake_cite"], 2)
        self.assertNotIn("Secret", json.dumps(res))
        md = census.results_md(res, {"x": 1})
        self.assertIn("851687", md)
        self.assertNotIn("Secret", md)
        rows = census.rows_csv(_docs()).splitlines()
        self.assertEqual(rows[0].split(",")[:2], ["row_id", "page"])
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
        if url == census.PAGES[0][1]:
            return PAGE.encode("utf-8"), "text/html"
        if url in [p[1] for p in census.PAGES]:
            return EMPTY.encode("utf-8"), "text/html"
        return b"%PDF-" + url.encode("utf-8"), "application/pdf"

    @staticmethod
    def fake_text(data):
        if b"851687" in data:
            return FAKE_TEXT
        if b"831253" in data:
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
        self.assertEqual(v, {"P1": "held", "P2": "failed", "P3": "held", "P4": "held", "P5": "held", "P6": "held",
                             "P7": "failed", "P8": "failed"})
        self.assertEqual((res["counts"]["in_frame"], res["counts"]["readable"], res["counts"]["fake_cite"]), (5, 4, 2))
        for name in ("Smith", "Gutman", "Zed", "Docx Petitioner"):
            self.assertNotIn(name, body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        for name in ("Smith", "Gutman", "Zed", ".pdf", ".docx"):
            self.assertNotIn(name, rows)
        self.assertIn("851687", rows)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        self.assertEqual(self.run_main(), 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))

    def test_main_stops_parser_check(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1), mock.patch.object(run_job, "MAX_NO_NUMBER", 0)])
        self.assertEqual(rc, 7)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
