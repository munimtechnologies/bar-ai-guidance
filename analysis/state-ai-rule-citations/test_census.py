# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Tests for census.py (standard library only, no network)."""
import csv
import io
import unittest

import census

HEADER = ["case_id", "Case Name", "Court", "State(s)", "Date", "Party(ies)", "AI Tool",
          "Hallucination Items", "Outcome", "Monetary Penalty", "Professional Sanction", "Alleged",
          "Vendor Disputed", "Vendor Disputed Explanation", "Pointer", "Source", "Details",
          "Legal Field Primary", "Legal Field Secondary"]


def make_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for r in rows:
        full = dict.fromkeys(HEADER, "")
        full.update(r)
        w.writerow([full[h] for h in HEADER])
    return buf.getvalue()


FILLER = " The court considered the motion and the record in full." * 40


class CourtTest(unittest.TestCase):
    def test_state_courts(self):
        for court, st in (("SC New York", "NY"), ("CA NY (2d)", "NY"), ("App. Div. 1st Dept (NY)", "NY"),
                          ("Family Court New York", "NY"), ("CA Florida (6d)", "FL"),
                          ("Florida (1d)", "FL"), ("DCA Florida", "FL"), ("SC Connecticut", "CT"),
                          ("CA Indiana", "IN"), ("Indiana Tax Court", "IN")):
            self.assertEqual(census.state_of(court), (st, "state court"), court)

    def test_federal_and_other(self):
        for court in ("S.D. New York", "E.D. New York", "N.D. Indiana (Bankruptcy)", "D. Connecticut",
                      "M.D. Florida", "D. Connecticut (Bankruptcy)", "2d Cir. (New York)",
                      "C.D. California"):
            st, why = census.state_of(court)
            self.assertIsNone(st, court)
        self.assertEqual(census.state_of("C.D. California")[1], "other state")
        self.assertEqual(census.state_of("S.D. New York")[1], "federal")

    def test_ambiguous(self):
        self.assertEqual(census.state_of("SC New York / Florida")[1], "ambiguous")


class SelectTest(unittest.TestCase):
    def test_periods_and_filters(self):
        text = make_csv([
            {"case_id": "1", "Court": "SC New York", "State(s)": "USA", "Date": "2026-06-01",
             "Party(ies)": "Lawyer", "Source": "/documents/1/a b.pdf"},
            {"case_id": "2", "Court": "SC New York", "State(s)": "USA", "Date": "2026-05-31",
             "Party(ies)": "Pro Se Litigant", "Source": "/documents/2/x.pdf"},
            {"case_id": "3", "Court": "SC New York", "State(s)": "USA", "Date": "2025-10-31",
             "Party(ies)": "Lawyer", "Source": "/documents/3/x.pdf"},
            {"case_id": "4", "Court": "SC New York", "State(s)": "USA", "Date": "2026-11-09",
             "Party(ies)": "Lawyer", "Source": "/documents/4/x.pdf"},
            {"case_id": "5", "Court": "S.D. New York", "State(s)": "USA", "Date": "2026-07-01",
             "Party(ies)": "Lawyer", "Source": "/documents/5/x.pdf"},
            {"case_id": "6", "Court": "CA Indiana", "State(s)": "USA", "Date": "2026-07-31",
             "Party(ies)": "Pro Se Litigant", "Source": ""},
            {"case_id": "7", "Court": "CA Indiana", "State(s)": "USA", "Date": "",
             "Party(ies)": "Lawyer", "Source": "/documents/7/x.pdf"},
            {"case_id": "8", "Court": "SC New York", "State(s)": "Canada", "Date": "2026-07-01",
             "Party(ies)": "Lawyer", "Source": "/documents/8/x.pdf"},
            {"case_id": "9", "Court": "CA Florida (4d)", "State(s)": "USA", "Date": "2026-06-15",
             "Party(ies)": "Expert", "Pointer": "https://example.org/d.pdf"},
        ])
        rows, courts = census.select_rows(text)
        got = {r["case_id"]: (r["state"], r["period"], r["party"]) for r in rows}
        self.assertEqual(got, {"1": ("NY", "post", "lawyer"), "2": ("NY", "pre", "pro_se"),
                               "6": ("IN", "pre", "pro_se"), "9": ("FL", "post", "other")})
        by_id = {r["case_id"]: r for r in rows}
        self.assertEqual(by_id["1"]["url"], census.SITE + "/documents/1/a%20b.pdf")
        self.assertIsNone(by_id["6"]["url"])
        self.assertEqual(by_id["9"]["url"], "https://example.org/d.pdf")
        table = {(c["court"], c["classified"]): c["rows"] for c in courts}
        self.assertEqual(table[("S.D. New York", "federal")], 1)
        self.assertEqual(table[("SC New York", "state court")], 4)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            census.select_rows("case_id,Court\n1,SC New York\n")


class PatternTest(unittest.TestCase):
    def hit(self, state, snippet):
        return census.classify_text(state, FILLER + " " + snippet + " " + FILLER)

    def test_new_rule_hits(self):
        cases = (
            ("NY", "sanctions under 22 NYCRR Part 161 are warranted"),
            ("NY", "see 22 NYCRR part 161"),
            ("NY", "Uniform Rules (22 NYCRR) § 161.2 requires review"),
            ("NY", "22 NYCRR 161.1"),
            ("FL", "violated Fla. R. Gen. Prac. & Jud. Admin. 2.515(d)(2)"),
            ("FL", "rule 2.515"),
            ("CT", "Practice Book § 4-9 requires"),
            ("CT", "Practice Book Section 4-9"),
            ("CT", "Practice Book §§ 4-2 and 4-9"),
            ("CT", "under § 4-\n9 of the rules"),
            ("IN", "Ind. Trial Rule 11(B)"),
            ("IN", "Trial Rule 11.2 allows"),
            ("IN", "T.R. 11"),
        )
        for st, snip in cases:
            self.assertTrue(self.hit(st, snip)["cites_new_rule"], (st, snip))

    def test_new_rule_misses(self):
        cases = (
            ("NY", "Part 1610 and 161 N.Y.S.3d 12"),
            ("NY", "22 NYCRR 130-1.1"),
            ("FL", "$12.515 and 32.5151"),
            ("FL", "section 57.105"),
            ("CT", "Practice Book § 4-90 and § 14-9 and § 4-9a"),
            ("IN", "Trial Rule 110 and Appellate Rule 11"),
            ("NY", "Practice Book § 4-9"),   # another state's rule does not count
        )
        for st, snip in cases:
            self.assertFalse(self.hit(st, snip)["cites_new_rule"], (st, snip))

    def test_secondary(self):
        r = self.hit("NY", "22 NYCRR 130-1.1 and part 130")
        self.assertTrue(r["ny_part_130"])
        self.assertFalse(r["fl_57105"])
        r = self.hit("FL", "Rule 2.515(d)(2) and section 57.105")
        self.assertTrue(r["fl_2515_d2"] and r["fl_57105"])
        r = self.hit("CT", "Practice Book § 85-2 (11)")
        self.assertTrue(r["ct_85_2_or_62_6"])
        r = self.hit("IN", "Trial Rule 11.1")
        self.assertTrue(r["in_11_1_or_11_2"])

    def test_unreadable_never_counts(self):
        r = census.classify_text("NY", "22 NYCRR Part 161")
        self.assertFalse(r["readable"])
        self.assertFalse(r["cites_new_rule"])

    def test_excerpt_only_on_hit(self):
        self.assertIn("Part 161", self.hit("NY", "22 NYCRR Part 161")["excerpt"])
        self.assertEqual(self.hit("NY", "nothing here")["excerpt"], "")


def row(cid, st, per, party, cites, date=None, **kw):
    d = {"case_id": cid, "state": st, "period": per, "party": party, "doc_status": "ok",
         "readable": True, "cites_new_rule": cites,
         "date": date or ("2026-09-01" if per == "post" else "2026-01-01")}
    d.update(kw)
    return d


class GradeTest(unittest.TestCase):
    def test_all_not_testable_when_empty(self):
        res = census.grade([])
        p = res["predictions"]
        for k in ("H1", "H2", "H3", "H4", "H5"):
            self.assertEqual(p[k]["verdict"], "not testable", k)
        self.assertEqual(p["H6"]["verdict"], "held")

    def test_verdicts(self):
        rows = []
        # NY post: 8 lawyer rows, 2 cite Part 161, 5 cite Part 130
        for i in range(8):
            rows.append(row("ny%d" % i, "NY", "post", "lawyer", i < 2, ny_part_130=i < 5))
        # FL: post 4 rows (3 cite), pre 4 rows (1 cites)
        for i in range(4):
            rows.append(row("flp%d" % i, "FL", "post", "pro_se", i < 3))
            rows.append(row("flq%d" % i, "FL", "pre", "pro_se", i < 1))
        # IN: post 4 (0 cite), pre 4 (1 cites)
        for i in range(4):
            rows.append(row("inp%d" % i, "IN", "post", "pro_se", False))
            rows.append(row("inq%d" % i, "IN", "pre", "pro_se", i < 1))
        # an unreadable and a missing document never count
        rows.append(row("u1", "NY", "post", "lawyer", True, readable=False))
        rows.append({"case_id": "m1", "state": "NY", "period": "post", "party": "lawyer",
                     "doc_status": "no_document", "date": "2026-09-01"})
        # placebo: NY pre rows before 25 March 2026, one match; a later one does not count
        rows.append(row("nyq1", "NY", "pre", "lawyer", True, date="2026-02-01"))
        rows.append(row("nyq2", "NY", "pre", "lawyer", True, date="2026-04-01"))
        res = census.grade(rows)
        p = {k: v["verdict"] for k, v in res["predictions"].items()}
        # post readable: 8 NY (2) + 4 FL (3) + 4 IN (0) = 16 rows, 5 cite: share 0.3125 < 0.5
        self.assertEqual(res["predictions"]["H1"]["detail"], {"n": 16, "cites": 5, "share": 0.312})
        self.assertEqual(p["H1"], "held")
        self.assertEqual(p["H2"], "held")      # 5 > 2
        self.assertEqual(p["H3"], "held")      # 0.75 > 0.25
        self.assertEqual(p["H4"], "failed")    # 0 < 0.25
        # lawyers: 8 rows 2 cite (0.25); pro se: 8 rows 3 cite (0.375)
        self.assertEqual(p["H5"], "failed")
        self.assertEqual(res["predictions"]["H6"]["detail"], {"n": 1, "matches": 1})
        self.assertEqual(p["H6"], "held")
        self.assertEqual(res["counts"]["unreadable"], 1)
        self.assertEqual(res["counts"]["by_doc_status"]["no_document"], 1)
        md = census.results_md(res, {"sha256": "abc", "fetched_at": "t"})
        self.assertIn("| NY | 22 NYCRR Part 161 | 2026-06-01 | 2 / 8 | 2 / 2 |", md)

    def test_public_csv_has_no_names_or_excerpts(self):
        r = row("1", "NY", "post", "lawyer", True, case_name="Doe v. Roe", excerpt="secret text",
                court="SC New York", chars=5000, ai_words=True)
        out = census.rows_csv([r])
        self.assertNotIn("Doe v. Roe", out)
        self.assertNotIn("secret text", out)
        self.assertTrue(out.startswith("case_id,state,court,date,period,party,doc_status"))


if __name__ == "__main__":
    unittest.main()
