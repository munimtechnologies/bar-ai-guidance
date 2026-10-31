"""Tests for grade_aipo.py. Apache-2.0. MV2 of Munim, Inc.; made with AI agents working in his name."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade_aipo as g  # noqa: E402

POST = ("Example post\n2026-01-01T00:00:00\nhttps://example.org/post\n\nThe court said:\n"
        "> No party may use “public AI” tools\n"
        "> with Protected Material, and self-hosted models are allowed.\n"
        "The blog author's own comment.\n")


def good_case(**kw):
    case = {"case_id": "a", "status": "codable", "court": "D. X.",
            "spans": [{"doc": "post:1", "start": "No party may use", "end": "models are allowed."}],
            "tests": {"PUBLIC": "may use \"public AI\" tools"},
            "self_hosting_named": True, "self_hosting_quote": "self-hosted models are allowed",
            "openness_named": False, "setup_a": "permitted",
            "setup_a_quote": "No party may use ... self-hosted models are allowed"}
    case.update(kw)
    return case


def synthetic(n, shared_pair=True):
    """n codable cases: 2 name self-hosting, 5 use DATA, 3 use OPENNESS, 5 permit A, 2 forbid A."""
    cases, texts = [], {}
    common = ["shared%d" % j for j in range(30)]
    for i in range(n):
        own = ["w%dx%d" % (i, j) for j in range(40)]
        cid = "c%02d" % i
        tests = {"DATA": "q"} if i < 5 else {"NOTICE": "q"}
        if 5 <= i < 8:
            tests["OPENNESS"] = "q"
        cases.append({"case_id": cid, "status": "codable", "court": "court%d" % i, "tests": tests,
                      "self_hosting_named": i < 2, "openness_named": False,
                      "setup_a": "permitted" if i < 5 else ("forbidden" if i < 7 else "unclear")})
        if shared_pair and i == 0:
            own = common + own
        elif shared_pair and i == 1:
            own = own + common
        texts[cid] = " ".join(own)
    return cases, texts


class TestText(unittest.TestCase):
    def test_norm(self):
        self.assertEqual(g.norm("> a “b”\n>  c’s…"), "a \"b\" c's...")

    def test_extract(self):
        span = g.extract(POST, "No party may use", "models are allowed.")
        self.assertEqual(span, "No party may use \"public AI\" tools with Protected Material, "
                               "and self-hosted models are allowed.")
        self.assertNotIn("blog author", span)

    def test_extract_refuses_missing_or_repeated_anchor(self):
        with self.assertRaises(ValueError):
            g.extract(POST, "not in the post", "allowed.")
        with self.assertRaises(ValueError):
            g.extract("abc abc def", "abc", "def")
        with self.assertRaises(ValueError):
            g.extract(POST, "No party may use", "missing end")

    def test_quote_in(self):
        span = g.extract(POST, "No party may use", "models are allowed.")
        self.assertTrue(g.quote_in("Protected Material, and self-hosted", span))
        self.assertTrue(g.quote_in("No party … self-hosted models", span))
        self.assertFalse(g.quote_in("self-hosted models ... No party", span))
        self.assertFalse(g.quote_in("", span))


class TestCheck(unittest.TestCase):
    docs = {"post:1": POST}

    def test_good_case_passes(self):
        self.assertEqual(g.check_case(good_case(), self.docs), [])

    def test_bad_quote_and_fields_fail(self):
        self.assertEqual(len(g.check_case(good_case(tests={"DATA": "trains on inputs"}), self.docs)), 1)
        self.assertEqual(len(g.check_case(good_case(tests={"MAGIC": "No party"}), self.docs)), 1)
        self.assertEqual(len(g.check_case(good_case(setup_a="unclear"), self.docs)), 1)
        self.assertEqual(len(g.check_case(good_case(openness_named=None), self.docs)), 1)
        self.assertEqual(len(g.check_case(good_case(spans=[{"doc": "post:9", "start": "a", "end": "b"}]),
                                          self.docs)), 1)

    def test_not_codable_and_refusal(self):
        self.assertEqual(len(g.check_case({"case_id": "b", "status": "not_codable"}, self.docs)), 1)
        self.assertEqual(g.check_case({"case_id": "b", "status": "not_codable",
                                       "reason": "described, not quoted"}, self.docs), [])
        self.assertEqual(g.check_case({"case_id": "r", "status": "refusal",
                                       "spans": good_case()["spans"]}, self.docs), [])


class TestGrade(unittest.TestCase):
    def test_ten_cases(self):
        cases, texts = synthetic(10)
        r = g.grade(cases, texts)
        self.assertEqual(r["counts"]["codable"], 10)
        self.assertEqual(r["predictions"], {"P1": "held", "P2": "held", "P3": "failed",
                                            "P4": "held", "P5": "held", "P6": "held"})
        self.assertEqual(r["reuse"]["shared_cases"], ["c00", "c01"])
        self.assertEqual(r["reuse"]["pairs"][0]["words"], 30)
        self.assertEqual(r["reuse"]["longest_run_by_case"]["c02"], 0)

    def test_same_court_pair_is_not_cross_court(self):
        cases, texts = synthetic(10)
        cases[1]["court"] = cases[0]["court"]
        r = g.grade(cases, texts)
        self.assertEqual(r["predictions"]["P5"], "failed")
        self.assertEqual(r["predictions"]["P6"], "held")

    def test_openness_case_permitting_a_fails_p3(self):
        cases, texts = synthetic(20, shared_pair=False)
        for c in cases[5:]:
            c["tests"].pop("OPENNESS", None)
        cases[0]["tests"]["OPENNESS"] = "q"
        r = g.grade(cases, texts)
        self.assertEqual(r["openness_cases_permitting_a"], ["c00"])
        self.assertEqual(r["predictions"]["P3"], "failed")
        self.assertEqual(r["predictions"]["P5"], "failed")

    def test_too_small(self):
        cases, texts = synthetic(9)
        r = g.grade(cases, texts)
        self.assertEqual(set(r["predictions"].values()), {"too small to grade"})
        self.assertEqual(r["counts"]["codable"], 9)


class TestMain(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(os.path.join(d, "texts"))
            with open(os.path.join(d, "texts", "1.txt"), "w", encoding="utf-8") as f:
                f.write(POST)
            data = os.path.join(d, "data.json")
            with open(data, "w", encoding="utf-8") as f:
                json.dump({"cases": [good_case(), {"case_id": "b", "status": "not_codable",
                                                   "reason": "described only"}]}, f)
            out = os.path.join(d, "results.json")
            with contextlib.redirect_stdout(io.StringIO()):
                code = g.main(["--data", data, "--texts", os.path.join(d, "texts"), "--out", out])
            self.assertEqual(code, 0)
            with open(out, encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(r["problems"], [])
            self.assertEqual(r["counts"]["not_codable"], 1)
            self.assertEqual(r["predictions"]["P1"], "too small to grade")
            self.assertIn("self-hosted models are allowed", r["ai_text_by_case"]["a"])

    def test_problems_give_exit_code_1(self):
        with tempfile.TemporaryDirectory() as d:
            data = os.path.join(d, "data.json")
            with open(data, "w", encoding="utf-8") as f:
                json.dump({"cases": [good_case(), good_case()]}, f)
            with contextlib.redirect_stdout(io.StringIO()):
                code = g.main(["--data", data, "--texts", d])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
