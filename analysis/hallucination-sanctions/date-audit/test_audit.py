# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for the date audit (no network, no PDFs needed)."""
import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit  # noqa: E402

D = datetime.date


def found(text, d):
    return audit.find_date(audit.norm_text(text), d) is not None


class DateMatching(unittest.TestCase):
    def test_written_forms(self):
        d = D(2026, 10, 27)
        for t in ("Dated: October 27, 2026", "SO ORDERED on Oct. 27, 2026.", "signed this 27th day of October, 2026",
                  "27 October 2026", "on October 27th, 2026", "Date: 10/27/2026", "Filed 10/27/26 Page 1 of 9",
                  "10-27-2026", "2026-10-27", "OCTOBER\n27,\n2026", "October 27 2026"):
            self.assertTrue(found(t, d), t)

    def test_leading_zero_and_single_digit(self):
        d = D(2026, 3, 9)
        for t in ("March 9, 2026", "March 09, 2026", "03/09/2026", "3/9/26", "9th day of March, 2026", "Mar. 9, 2026"):
            self.assertTrue(found(t, d), t)

    def test_boundaries(self):
        self.assertFalse(found("11/2/26", D(2026, 1, 2)))
        self.assertFalse(found("October 12, 2026", D(2026, 10, 1)))
        self.assertFalse(found("October 1, 20261", D(2026, 10, 1)))
        self.assertFalse(found("summary 5, 2026", D(2026, 3, 5)))
        self.assertFalse(found("10/27/2025", D(2026, 10, 27)))
        self.assertFalse(found("", D(2026, 10, 27)))
        self.assertIsNone(audit.find_date("october 27, 2026", None))

    def test_ecf(self):
        t = audit.norm_text("Case 1:25-cv-01 Document 40 Filed 10/27/26 Page 1 of 3\n... motion filed 3/4/25 ..."
                            "Case 1:25-cv-01 Document 40 Filed 10/27/26 Page 2 of 3")
        self.assertEqual(audit.ecf_date(t), (D(2026, 10, 27), 2))
        t2 = audit.norm_text("Entered on FLSD Docket 09/30/2026 Page 1 of 4")
        self.assertEqual(audit.ecf_date(t2), (D(2026, 9, 30), 1))
        self.assertEqual(audit.ecf_date("no header"), (None, 0))
        self.assertEqual(audit.ecf_date(audit.norm_text("Filed 13/45/26")), (None, 0))

    def test_filename(self):
        self.assertEqual(audit.filename_date("/documents/3381/Quzack_USA_09-03-2026.pdf"), D(2026, 3, 9))
        self.assertIsNone(audit.filename_date("/documents/3393/2026fc1346.pdf"))
        self.assertIsNone(audit.filename_date("/documents/1/x_31-02-2026.pdf"))

    def test_iso_and_period(self):
        self.assertEqual(audit.parse_iso("2026-10-27"), D(2026, 10, 27))
        self.assertIsNone(audit.parse_iso(""))
        self.assertEqual(audit.period_of(D(2026, 6, 30)), "2026H1")
        self.assertEqual(audit.period_of(D(2026, 7, 1)), "2026H2")
        self.assertEqual(audit.period_of(None), "")

    def test_doc_url(self):
        self.assertEqual(audit.doc_url("/documents/1/a b.pdf"), "https://www.damiencharlotin.com/documents/1/a%20b.pdf")
        self.assertIsNone(audit.doc_url("https://example.org/x.pdf"))
        self.assertIsNone(audit.doc_url("/documents/1/x.docx"))


class Corrections(unittest.TestCase):
    rec = D(2026, 10, 27)

    def test_ecf_far_wins_in_c1_only_if_not_found_in_c2(self):
        cc = audit.correct(self.rec, True, D(2026, 3, 9), None, False)
        self.assertEqual(cc["c1"], (D(2026, 3, 9), "ecf"))
        self.assertEqual(cc["c2"], (self.rec, "kept"))
        cc = audit.correct(self.rec, False, D(2026, 3, 9), None, False)
        self.assertEqual(cc["c2"], (D(2026, 3, 9), "ecf"))

    def test_ecf_close_kept(self):
        cc = audit.correct(self.rec, False, D(2026, 10, 24), D(2026, 3, 9), True)
        self.assertEqual(cc["c1"], (D(2026, 3, 9), "filename"))
        cc = audit.correct(self.rec, True, D(2026, 10, 24), D(2026, 3, 9), True)
        self.assertEqual(cc["c1"], (self.rec, "kept"))
        self.assertEqual(cc["c2"], (self.rec, "kept"))

    def test_filename_needs_text(self):
        cc = audit.correct(self.rec, False, None, D(2026, 3, 9), False)
        self.assertEqual(cc["c1"], (self.rec, "kept"))
        self.assertEqual(cc["c2"], (self.rec, "kept"))

    def test_undated(self):
        cc = audit.correct(None, False, None, D(2026, 6, 2), True)
        self.assertEqual(cc["c1"], (D(2026, 6, 2), "filename"))
        self.assertEqual(cc["c2"], (D(2026, 6, 2), "filename"))
        cc = audit.correct(None, False, None, None, False)
        self.assertEqual(cc["c1"], (None, "kept"))


class Rows(unittest.TestCase):
    def test_audit_row_no_pdf(self):
        r = audit.audit_row("1", "2026-10-27", "https://example.org/x.pdf", lambda u: b"")
        self.assertEqual(r["status"], "no_hosted_pdf")
        self.assertEqual(r["c1_period"], "2026H2")
        self.assertEqual(r["c1_rule"], "kept_unaudited")

    def test_audit_row_fetch_failure(self):
        def boom(url):
            raise OSError("down")
        r = audit.audit_row("1", "2026-10-27", "/documents/1/a_09-03-2026.pdf", boom)
        self.assertEqual(r["status"], "fetch_failed")
        self.assertEqual(r["filename_date"], "2026-03-09")
        self.assertEqual(r["c2_date"], "2026-10-27")

    def test_pseudo_raw(self):
        u = {"case_id": "7", "date": "2026-03-01", "period": "2026H1", "parties": "Lawyer; Pro Se Litigant",
             "penalty_raw": "1500 USD", "penalty_status": "ok", "amount": "1500.0", "currency": "USD",
             "fined": "True", "usd_amount": "1500.0", "prof": "True", "alleged": ""}
        p = audit.pseudo_raw(u)
        self.assertEqual(p["Date"], "2026-03-01")
        self.assertEqual(p["Professional Sanction"], "Yes")
        self.assertEqual(p["Alleged"], "")
        self.assertEqual(p["State(s)"], "USA")
        self.assertEqual(audit.pseudo_raw(u, "2026-09-01")["Date"], "2026-09-01")
        u["alleged"] = "True"
        self.assertEqual(audit.pseudo_raw(u)["Alleged"], "Yes")

    def test_summarise(self):
        base = {k: "" for k in audit.ROW_FIELDS}
        a = dict(base, case_id="1", status="text", recorded_date="2026-10-27", recorded_period="2026H2",
                 recorded_found=True, ecf_date="2026-10-27", c1_period="2026H2", c2_period="2026H2")
        b = dict(base, case_id="2", status="text", recorded_date="2026-10-27", recorded_period="2026H2",
                 recorded_found=False, ecf_date="2026-03-09", c1_period="2026H1", c2_period="2026H1")
        c = dict(base, case_id="3", status="no_text", recorded_date="2026-01-02", recorded_period="2026H1",
                 c1_period="2026H1", c2_period="2026H1")
        s = audit.summarise([a, b, c])
        self.assertEqual(s["D1"], {"n": 2, "found": 1, "share": 0.5})
        self.assertEqual(s["D2"]["within_7_days"], 1)
        self.assertEqual(s["D3"]["moved_c1"], 1)
        self.assertEqual(s["D3"]["flows_c1"], {"2026H2 -> 2026H1": 1})
        self.assertEqual(s["status_counts"], {"no_text": 1, "text": 2})


if __name__ == "__main__":
    unittest.main()
