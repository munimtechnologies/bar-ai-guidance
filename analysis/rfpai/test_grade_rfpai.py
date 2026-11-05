# SPDX-License-Identifier: Apache-2.0
"""Offline tests for grade_rfpai.py. MV2 of Munim, Inc.; made with AI agents working in his name."""
import json
import tempfile
import unittest
from pathlib import Path

import grade_rfpai as g

HERE = Path(__file__).resolve().parent


def rec(rid, posted, vendor=False, subs=(), tech="TECH", ais=False, **kw):
    r = {"id": rid, "posted": posted, "vendor_ai": vendor, "vendor_ai_subcodes": list(subs),
         "tech": tech, "ai_in_scope": ais, "borderline": [], "seed_only": False, "sensitivity_codable": True,
         "files": [{"url": f"u{rid}", "sha256": "0" * 64}], "quotes": []}
    r.update(kw)
    return r


class TextTests(unittest.TestCase):
    def test_ligature_and_whitespace(self):
        self.assertEqual(g.norm("before ﬁnalization.\n  x"), "before finalization. x")

    def test_quote_in_across_line_breaks(self):
        text = "Any use of AI in processing data under this contract must be disclosed, and any \ndeliverables"
        self.assertTrue(g.quote_in("must be disclosed, and any deliverables", text))
        self.assertFalse(g.quote_in("must not be disclosed", text))
        self.assertFalse(g.quote_in("", text))

    def test_word_per_line_text(self):
        text = "Lead  the  development  of\n \nAI\n \nand\n \nWeb\n"
        self.assertTrue(g.quote_in("development of AI and Web", text))


class DateTests(unittest.TestCase):
    def test_window(self):
        self.assertTrue(g.in_window("2026-01-01"))
        self.assertTrue(g.in_window("2026-11-04"))
        self.assertFalse(g.in_window("2026-11-05"))
        self.assertFalse(g.in_window("2025-12-31"))
        self.assertTrue(g.in_window("2026-08"))
        self.assertFalse(g.in_window("2026-12"))

    def test_half(self):
        self.assertEqual(g.half("2026-06-30"), "H1")
        self.assertEqual(g.half("2026-07-01"), "H2")
        self.assertEqual(g.half("2026-06"), "H1")
        self.assertEqual(g.half("2026-08"), "H2")


class GradeTests(unittest.TestCase):
    def test_p1_boundary_30_percent_holds(self):
        rs = [rec(f"a{i}", "2026-02-01", vendor=(i < 3), subs=("disclose",) if i < 3 else ()) for i in range(10)]
        self.assertEqual(g.grade(rs)["P1"]["result"], "held")
        rs[3]["vendor_ai"], rs[3]["vendor_ai_subcodes"] = True, ["disclose"]
        self.assertEqual(g.grade(rs)["P1"]["result"], "failed")

    def test_p2_not_testable_with_small_half(self):
        rs = [rec(f"a{i}", "2026-02-01") for i in range(5)] + [rec(f"b{i}", "2026-08-01") for i in range(4)]
        self.assertEqual(g.grade(rs)["P2"]["result"], "not testable")

    def test_p2_strict(self):
        h1 = [rec(f"a{i}", "2026-02-01", vendor=(i == 0), subs=("disclose",) if i == 0 else ()) for i in range(5)]
        h2 = [rec(f"b{i}", "2026-08-01", vendor=(i == 0), subs=("disclose",) if i == 0 else ()) for i in range(5)]
        self.assertEqual(g.grade(h1 + h2)["P2"]["result"], "failed")  # equal shares are not higher
        h2[1]["vendor_ai"], h2[1]["vendor_ai_subcodes"] = True, ["disclose"]
        self.assertEqual(g.grade(h1 + h2)["P2"]["result"], "held")

    def test_p3(self):
        rs = [rec("a", "2026-02-01", vendor=True, subs=("ban",))]
        self.assertEqual(g.grade(rs)["P3"]["result"], "failed")
        self.assertEqual(g.grade([rec("b", "2026-02-01")])["P3"]["result"], "held")

    def test_p4(self):
        rs = [rec(f"t{i}", "2026-02-01", ais=(i == 0)) for i in range(4)]
        self.assertEqual(g.grade(rs)["P4"]["result"], "not testable")
        rs.append(rec("t4", "2026-02-01", ais=False))
        self.assertEqual(g.grade(rs)["P4"]["result"], "failed")  # 1/5 = 20%
        rs.append(rec("t5", "2026-02-01", ais=True))
        rs.append(rec("t6", "2026-02-01", ais=False))
        rs.append(rec("t7", "2026-02-01", ais=False))
        self.assertEqual(g.grade(rs)["P4"]["result"], "held")  # 2/8 = 25%
        rs.append(rec("n", "2026-02-01", tech="NON_TECH", ais=True))
        self.assertEqual(g.grade(rs)["P4"]["n"], 8)

    def test_flip(self):
        rs = [rec("a", "2026-02-01", vendor=True, subs=("data",))]
        b = {"field": "vendor_ai", "alt": False, "alt_subcodes": []}
        f = g.flipped(rs, "a", b)
        self.assertFalse(f[0]["vendor_ai"])
        self.assertEqual(f[0]["vendor_ai_subcodes"], [])
        self.assertTrue(rs[0]["vendor_ai"])  # original untouched


class CodingFileTests(unittest.TestCase):
    def setUp(self):
        self.coding = json.loads((HERE / "coding.json").read_text(encoding="utf-8"))
        self.frame = json.loads((HERE / "frame_decisions.json").read_text(encoding="utf-8"))

    def test_structure_clean(self):
        self.assertEqual(g.check_structure(self.coding), [])

    def test_codable_list_matches(self):
        self.assertEqual(sorted(r["id"] for r in self.coding["records"]), sorted(self.frame["codable"]))

    def test_every_frame_record_decided_once(self):
        keys = [d["key"] for d in self.frame["decisions"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), self.frame["summary"]["records_in_frame"])

    def test_check_texts_reports_missing_quote(self):
        c = {"records": [rec("a", "2026-02-01", quotes=[{"codes": ["SCOPE"], "file": 0, "text": "hello world"}])]}
        rows = g.check_texts(c, {"ua": "x" * 1200 + " hello\nworld"})
        self.assertTrue(all(r["ok"] for r in rows))
        rows = g.check_texts(c, {"ua": "short"})
        self.assertFalse(any(r["ok"] for r in rows))

    def test_write_md_runs(self):
        rs = [rec(f"a{i}", "2026-02-01") for i in range(6)]
        res = {"coding_sha256": "x", "files_ok": 1, "files_total": 1, "quotes_ok": 0, "quotes_total": 0,
               "structure_problems": [], "verified": True, "full": g.grade(rs), "sensitivity": g.grade(rs),
               "robustness": [], "text_checks": []}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            g.write_md(p, res)
            self.assertIn("P1 VENDOR_AI share", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
