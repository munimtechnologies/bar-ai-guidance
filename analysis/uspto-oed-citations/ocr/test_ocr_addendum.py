# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for ocr_addendum.py (no network, no OCR tools needed)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ocr_addendum as oa  # noqa: E402


class TolerantPatterns(unittest.TestCase):
    def test_ocr_variants_of_11_101(self):
        for s in ("37 C.F.R. § I I.IOI et seq.", "§ 11.101 (competence)", "§§ 11. 101 (a practitioner",
                  "§ l l.lOl", "violated 1 1.1O1"):
            self.assertTrue(oa.tolerant_flags(s)["r11_101_tol"], s)

    def test_ocr_variants_of_11_18_and_804(self):
        f = oa.tolerant_flags("rules l 1.18(b)(2)(ii) and § l 1.804(c) and § 11 .301")
        self.assertTrue(f["r11_18_tol"])
        self.assertTrue(f["r11_804_tol"])

    def test_no_false_matches(self):
        f = oa.tolerant_flags("211.18 and 11.180 and 1.11.101 and 11.1018 and page 11.10")
        self.assertFalse(f["r11_18_tol"])
        self.assertFalse(f["r11_101_tol"])
        self.assertFalse(oa.tolerant_flags("11.101")["r11_18_tol"])

    def test_guidance(self):
        self.assertTrue(oa.tolerant_flags("see 89 FR 25609 (Apr. 11, 2024)")["guidance_tol"])
        self.assertTrue(oa.tolerant_flags("89 Fed. Reg. 25,609")["guidance_tol"])
        self.assertTrue(oa.tolerant_flags("Guidance on Use of Artificial Intelligence-Based Tools in Practice")["guidance_tol"])
        self.assertFalse(oa.tolerant_flags("89 FR 10043 inventorship guidance")["guidance_tol"])


class Helpers(unittest.TestCase):
    def test_targets(self):
        self.assertEqual(len(oa.TARGETS), 27)
        self.assertIn("d2be0a280703", oa.TARGETS)
        self.assertEqual(oa.TARGETS["d2be0a280703"][0], oa.MITCHELL)
        for rid, (proc, date, sha) in oa.TARGETS.items():
            self.assertRegex(rid, r"^[0-9a-f]{12}$")
            self.assertRegex(date, r"^20(2[3-6])-\d\d-\d\d$")
            self.assertRegex(sha, r"^[0-9a-f]{16}$")

    def test_pdfinfo_pages(self):
        self.assertEqual(oa.pages_from_pdfinfo("Producer: x\nPages:          7\nEncrypted: no\n"), 7)
        self.assertEqual(oa.pages_from_pdfinfo(""), 0)

    def test_select_targets(self):
        entries = [{"proceeding": "A"}, {"proceeding": "B"}, {"proceeding": "A"}]
        ids = {"A": "ff5c878034fc", "B": "zzz"}
        got = oa.select_targets(entries, lambda e: ids[e["proceeding"]])
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["row_id"], "ff5c878034fc")


def doc(proc, date="2026-01-01", **kw):
    d = {"proceeding": proc, "date": date, "doc_status": "ok", "ocr_chars": 5000, "textlayer_chars": 1,
         "sha_match": True}
    d.update(kw)
    return d


class Grading(unittest.TestCase):
    def test_all_hold(self):
        docs = [doc("D2026-16", fake_cite=True, ai_mention=True, r11_101_tol=True, r11_18=True, guidance_tol=True)]
        docs += [doc("X%d" % i) for i in range(26)]
        P = oa.grade(docs)["predictions"]
        self.assertEqual({k: v["verdict"] for k, v in P.items()},
                         {"A1": "held", "A2": "held", "A3": "held", "A4": "held", "A5": "held", "A6": "held",
                          "A7": "held", "A8": "held"})

    def test_failures(self):
        docs = [doc("D2026-16", fake_cite=True, ai_mention=False)]
        docs += [doc("X1", fake_cite=True, ai_mention=True), doc("X2", ai_mention=True),
                 doc("X3", textlayer_chars=900), doc("X4", ocr_chars=10)]
        res = oa.grade(docs)
        P = res["predictions"]
        self.assertEqual(P["A1"]["verdict"], "failed")   # 4 of 5 lack a text layer, fewer than 25
        self.assertEqual(P["A2"]["verdict"], "failed")
        self.assertEqual(P["A3"]["verdict"], "failed")
        self.assertEqual(P["A4"]["verdict"], "failed")
        self.assertEqual(P["A5"]["verdict"], "failed")
        self.assertEqual(P["A7"]["verdict"], "failed")
        self.assertEqual(P["A8"]["verdict"], "failed")
        self.assertEqual(res["counts"]["ocr_readable"], 4)
        self.assertEqual(res["counts"]["fake_cite_proceedings"], ["D2026-16", "X1"])

    def test_mitchell_unreadable(self):
        P = oa.grade([doc("D2026-16", ocr_chars=5), doc("X1")])["predictions"]
        self.assertEqual(P["A2"]["verdict"], "not testable")
        self.assertEqual(P["A7"]["verdict"], "not testable")
        self.assertEqual(P["A3"]["verdict"], "held")

    def test_rows_csv(self):
        out = oa.rows_csv([{"row_id": "a", "proceeding": "D2020-10, D2024-15", "ocr_chars": 400}])
        lines = out.splitlines()
        self.assertEqual(lines[0].split(",")[0], "row_id")
        self.assertIn('"D2020-10, D2024-15"', lines[1])
        self.assertIn("True", lines[1])


if __name__ == "__main__":
    unittest.main()
