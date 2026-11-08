# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Tests for the pre-registered procurement-tribunal analysis. Synthetic rows only."""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402

HEADER = ["case_id", "Case Name", "Court", "State(s)", "Date", "Party(ies)", "AI Tool", "Hallucination Items",
          "Outcome", "Monetary Penalty", "Professional Sanction", "Alleged", "Vendor Disputed",
          "Vendor Disputed Explanation", "Pointer", "Source", "Details", "Legal Field Primary",
          "Legal Field Secondary"]


def row(cid, court, date, parties="Pro Se Litigant", name="Acme, LLC", penalty="", prof="No", alleged="No",
        field="contract", details="bid protest of an award", tool=""):
    r = {h: "" for h in HEADER}
    r.update({"case_id": cid, "Case Name": name, "Court": court, "State(s)": "USA", "Date": date,
              "Party(ies)": parties, "Monetary Penalty": penalty, "Professional Sanction": prof,
              "Alleged": alleged, "Legal Field Primary": field, "Details": details, "AI Tool": tool})
    return r


class Forum(unittest.TestCase):
    def test_long_names_and_abbreviations(self):
        self.assertEqual(A.detect_forum("Government Accountability Office"), "GAO")
        self.assertEqual(A.detect_forum("GAO"), "GAO")
        self.assertEqual(A.detect_forum("U.S. Court of Federal Claims"), "COFC")
        self.assertEqual(A.detect_forum("Armed Services Board of Contract Appeals"), "ASBCA")
        self.assertEqual(A.detect_forum("CBCA"), "CBCA")
        self.assertEqual(A.detect_forum("Court of Appeals for the Federal Circuit"), "FEDCIR")
        self.assertEqual(A.detect_forum("Federal Circuit (appeal from Court of Federal Claims)"), "FEDCIR")

    def test_no_false_matches(self):
        for c in ("N.D. Cal.", "Ninth Circuit", "Sagaona court", "Supreme Court of Georgia", "Board of Immigration Appeals",
                  "gaol", ""):
            self.assertIsNone(A.detect_forum(c), c)

    def test_cofc_non_procurement_excluded_unless_s1(self):
        r = row("1", "Court of Federal Claims", "2026-02-01", field="tort", details="vaccine injury petition",
                name="Doe v. Secretary of Health and Human Services")
        self.assertFalse(A.classify(r)["core"])
        self.assertTrue(A.classify(r, cofc_all=True)["core"])
        r2 = row("2", "Court of Federal Claims", "2026-02-01", field="administrative", details="post-award bid protest")
        self.assertTrue(A.classify(r2)["core"])

    def test_s2_uses_b_number(self):
        r = row("3", "", "2026-03-01", name="Acme, LLC, B-424064")
        self.assertIsNone(A.classify(r)["forum"])
        self.assertEqual(A.classify_s2(r)["forum"], "GAO")


class Keys(unittest.TestCase):
    def test_protester_key(self):
        self.assertEqual(A.protester_key("Oready, LLC"), "oready")
        self.assertEqual(A.protester_key("Oready, LLC--Reconsideration"), "oready")
        self.assertEqual(A.protester_key("Matter of: Oready LLC, B-423649.2"), "oready")
        self.assertEqual(A.protester_key("SAVE THE AMERICAN COMMUNITIES LLC--Reconsideration"),
                         "save the american communities")
        self.assertEqual(A.protester_key("NDCHealth Corporation (d/b/a RelayHealth)"), "ndchealth")


class Parsing(unittest.TestCase):
    def test_amounts_and_dates(self):
        self.assertEqual(A.parse_amount("1000 USD")[0:2], ("ok", 1000.0))
        self.assertEqual(A.parse_amount("")[0], "none")
        self.assertEqual(A.parse_amount("see order")[0], "unparsed")
        self.assertEqual(A.parse_date("2026-7-3"), "2026-07-03")
        self.assertIsNone(A.parse_date("July 2026"))
        self.assertEqual(A.half_year("2026-07-03"), "2026H2")

    def test_money_flag(self):
        self.assertFalse(A.classify(row("1", "GAO", "2026-01-01", penalty="1"))["money"])
        self.assertTrue(A.classify(row("1", "GAO", "2026-01-01", penalty="5000 USD"))["money"])


def build(n_gao_25, n_gao_26, lawyer_25=0, lawyer_26=0, serial=0, money=0):
    rows, i = [], 0
    for k in range(n_gao_25):
        i += 1
        rows.append(row(str(i), "GAO", "2025-0%d-15" % (1 + k % 9), parties="Lawyer" if k < lawyer_25 else "Pro Se Litigant",
                        name="Serial, LLC" if k < serial else "Firm%d, Inc." % i))
    for k in range(n_gao_26):
        i += 1
        rows.append(row(str(i), "Government Accountability Office", "2026-0%d-10" % (1 + k % 7),
                        parties="Lawyer" if k < lawyer_26 else "Pro Se Litigant", name="Firm%d, Inc." % i,
                        penalty="2000 USD" if k < money else ""))
    return rows


class Predictions(unittest.TestCase):
    def test_all_hold(self):
        rows = build(20, 16, lawyer_25=2, lawyer_26=5, serial=10)
        recs = [A.classify(r) for r in rows]
        ev = A.evaluate(recs)
        self.assertEqual(ev["A1"]["n"], 16)
        self.assertEqual(ev["A1"]["verdict"], "held")
        self.assertEqual(ev["A2"]["verdict"], "held")
        self.assertEqual(ev["A3"]["verdict"], "held")
        self.assertEqual(ev["A4"]["verdict"], "held")   # 29 of 36 pro se
        self.assertEqual(ev["A5"]["verdict"], "held")
        self.assertEqual(ev["A6"]["verdict"], "held")   # 10 of 36 = 27.8%
        self.assertEqual(ev["A6"]["top_key"], "serial")

    def test_failures(self):
        rows = build(10, 10, lawyer_25=6, lawyer_26=2, serial=1, money=2)
        ev = A.evaluate([A.classify(r) for r in rows])
        self.assertEqual(ev["A1"]["verdict"], "failed")
        self.assertEqual(ev["A2"]["verdict"], "failed")
        self.assertEqual(ev["A3"]["verdict"], "failed")
        self.assertEqual(ev["A4"]["verdict"], "held")    # 12 of 20 = 60%
        self.assertEqual(ev["A5"]["verdict"], "failed")
        self.assertEqual(ev["A6"]["verdict"], "failed")

    def test_not_testable(self):
        ev = A.evaluate([A.classify(r) for r in build(3, 3)])
        for k in ("A3", "A4", "A5", "A6"):
            self.assertEqual(ev[k]["verdict"], "not testable", k)

    def test_windows(self):
        rows = [row("1", "GAO", "2026-08-01"), row("2", "GAO", "2026-11-02"), row("3", "GAO", "2024-12-31")]
        ev = A.evaluate([A.classify(r) for r in rows])
        self.assertEqual(ev["A1"]["n"], 0)
        self.assertEqual(ev["A2"]["n"], 0)


class EndToEnd(unittest.TestCase):
    def test_main_writes_outputs_without_names(self):
        rows = build(20, 16, lawyer_25=2, lawyer_26=5, serial=10)
        rows.append(row("900", "S.D.N.Y.", "2026-01-01", parties="Lawyer", name="Someone v. Other"))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "in.csv")
            with open(p, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=HEADER)
                w.writeheader()
                w.writerows(rows)
            out = os.path.join(d, "out")
            self.assertEqual(A.main(["--csv", p, "--out-dir", out]), 0)
            for f in ("results.json", "results.md", "procurement_rows.csv"):
                self.assertTrue(os.path.exists(os.path.join(out, f)), f)
            with open(os.path.join(out, "procurement_rows.csv"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("Firm", text)
            self.assertNotIn("900,", text)
            self.assertEqual(len(text.strip().splitlines()), 37)

    def test_missing_column_stops(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "in.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("case_id,Date\n1,2026-01-01\n")
            with self.assertRaises(SystemExit):
                A.read_csv(p)


if __name__ == "__main__":
    unittest.main()
