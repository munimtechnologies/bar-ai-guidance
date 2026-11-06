# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. Made with AI agents working in MV2's name.
"""Tests for analyze.py on synthetic rows only (no real data)."""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze  # noqa: E402

HEADER = ["case_id", "Case Name", "Court", "State(s)", "Date", "Party(ies)", "AI Tool", "Hallucination Items",
          "Outcome", "Monetary Penalty", "Professional Sanction", "Alleged", "Vendor Disputed",
          "Vendor Disputed Explanation", "Pointer", "Source", "Details", "Legal Field Primary",
          "Legal Field Secondary"]


def row(i, date, party, penalty="", prof="No", state="USA", alleged="No"):
    r = {h: "" for h in HEADER}
    r.update({"case_id": str(i), "Case Name": "Synthetic %d" % i, "Court": "Test Court", "State(s)": state,
              "Date": date, "Party(ies)": party, "Monetary Penalty": penalty, "Professional Sanction": prof,
              "Alleged": alleged, "Details": "x, y"})
    return r


def synthetic():
    rows, i = [], 0

    def add(n, date, party, fined, amount, prof_n=0, prof_on_fined=True):
        nonlocal i
        for k in range(n):
            i += 1
            pen = ("%d USD" % (amount + 100 * k)) if k < fined else ""
            prof = "Yes" if (k < prof_n) else "No"
            rows.append(row(i, date, party, pen, prof))

    add(40, "2025-03-01", "Lawyer", fined=10, amount=1000, prof_n=5)
    add(40, "2025-09-01", "Lawyer", fined=10, amount=1500, prof_n=5)
    add(40, "2026-02-01", "Lawyer", fined=12, amount=5000, prof_n=8)
    for d in ("2025-02-01", "2025-08-01", "2026-03-01"):
        add(40, d, "Pro Se Litigant", fined=2, amount=200)
    rows.append(row(9001, "2026-04-01", "Lawyer", "100 EUR", state="Canada"))
    return rows


def write_csv(rows, path, truncate_tail=False):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
        if truncate_tail:
            fh.write('9999,"Cut off case,Court')


class ParseTests(unittest.TestCase):
    def test_amounts(self):
        self.assertEqual(analyze.parse_amount("5000 USD"), ("ok", 5000.0, "USD"))
        self.assertEqual(analyze.parse_amount("5,000 USD"), ("ok", 5000.0, "USD"))
        self.assertEqual(analyze.parse_amount("40 "), ("ok", 40.0, None))
        self.assertEqual(analyze.parse_amount(""), ("none", None, None))
        self.assertEqual(analyze.parse_amount("—"), ("none", None, None))
        self.assertEqual(analyze.parse_amount("2500 ILS"), ("ok", 2500.0, "ILS"))
        self.assertEqual(analyze.parse_amount("costs to follow")[0], "unparsed")

    def test_periods(self):
        self.assertEqual(analyze.parse_period("2025-06-30"), ("2025H1", "2025"))
        self.assertEqual(analyze.parse_period("2025-07-01"), ("2025H2", "2025"))
        self.assertEqual(analyze.parse_period(""), (None, None))
        self.assertEqual(analyze.parse_period("30-06-2025"), (None, None))

    def test_classify(self):
        r = analyze.classify(row(1, "2026-01-05", "Expert; Lawyer", "1 USD", "Yes"))
        self.assertTrue(r["us"] and r["lawyer"] and r["fined"] and r["placeholder"] and r["prof"])
        self.assertIsNone(r["usd_amount"])
        self.assertFalse(r["fined_strict"])
        g = analyze.classify(row(2, "2026-01-05", "Government Lawyer", "2500 USD"))
        self.assertFalse(g["lawyer"])
        self.assertTrue(g["lawyer_broad"])
        self.assertEqual(g["usd_amount"], 2500.0)
        c = analyze.classify(row(3, "2026-01-05", "Pro Se Litigant", "2500 ILS", state="Israel"))
        self.assertFalse(c["us"])
        self.assertTrue(c["pro_se"])
        self.assertIsNone(c["usd_amount"])
        u = analyze.classify(row(4, "2026-01-05", "Lawyer", "pending"))
        self.assertTrue(u["fined"])
        self.assertFalse(u["fined_strict"])
        z = analyze.classify(row(5, "2026-01-05", "Lawyer", "0 USD"))
        self.assertFalse(z["fined"])
        self.assertTrue(analyze.classify(row(6, "2026-01-05", "Lawyer", state="Canada; USA"))["us"])
        self.assertTrue(analyze.is_us_token("USA (Texas)"))
        self.assertFalse(analyze.is_us_token("USAF"))


class GradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "d.csv")
        write_csv(synthetic(), self.path, truncate_tail=True)

    def test_read_skips_truncated_row(self):
        header, rows, bad = analyze.read_csv(self.path)
        self.assertEqual(header, HEADER)
        self.assertEqual(len(rows), 241)
        self.assertEqual(bad, 1)

    def test_predictions(self):
        header, rows, bad = analyze.read_csv(self.path)
        recs, res = analyze.analyze(header, rows, bad)
        p = res["primary"]
        self.assertEqual(p["P1"]["verdict"], "held")          # 0.30 - 0.25 = 0.05, on the margin
        self.assertAlmostEqual(p["P1"]["diff"], 0.05, places=6)
        self.assertEqual(p["P2"]["verdict"], "held")
        self.assertLess(p["P2"]["perm_p_rise"], 0.01)
        self.assertEqual(p["P3"]["verdict"], "held")
        self.assertEqual(p["P4"]["verdict"], "held")
        self.assertEqual(p["P5"]["verdict"], "held")          # prof rows overlap fined rows: 12/40
        self.assertEqual(res["n_us"], 240)
        self.assertEqual(res["table_lawyer"]["2026H1"]["n_usd_amounts"], 12)
        self.assertEqual(res["sensitivity"]["S4_years_2025_vs_2026"]["P1"]["verdict"], "held")

    def test_not_testable_when_small(self):
        rows = [r for r in synthetic() if not r["Date"].startswith("2026")]
        recs = [analyze.classify(r) for r in rows]
        ev = analyze.evaluate(recs)
        for k in ("P1", "P2", "P3", "P4", "P5"):
            self.assertEqual(ev[k]["verdict"], "not testable", k)

    def test_p1_fails_on_big_rise(self):
        rows = synthetic()
        for r in rows:
            if r["Date"] == "2026-02-01" and r["Party(ies)"] == "Lawyer" and not r["Monetary Penalty"]:
                r["Monetary Penalty"] = "300 USD"
        recs = [analyze.classify(r) for r in rows]
        ev = analyze.evaluate(recs)
        self.assertEqual(ev["P1"]["verdict"], "failed")
        self.assertEqual(ev["P5"]["verdict"], "failed")
        self.assertEqual(ev["P2"]["verdict"], "failed")       # many small fines pull the median down

    def test_outputs(self):
        main_rc = analyze.main(["--csv", self.path, "--out-dir", os.path.join(self.tmp, "out")])
        self.assertEqual(main_rc, 0)
        for f in ("results.json", "results.md", "us_rows.csv"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp, "out", f)), f)
        with open(os.path.join(self.tmp, "out", "results.md"), encoding="utf-8") as fh:
            md = fh.read()
        self.assertIn("**P1: held**", md)
        self.assertIn("not legal advice", md)


class WrapperTests(unittest.TestCase):
    def test_norm_sha_ignores_crlf(self):
        import run_job
        self.assertEqual(run_job.norm_sha(b"a\r\nb\n"), run_job.norm_sha(b"a\nb\n"))
        self.assertNotEqual(run_job.norm_sha(b"a\nb\n"), run_job.norm_sha(b"a\nc\n"))


if __name__ == "__main__":
    unittest.main()
