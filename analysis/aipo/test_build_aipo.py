"""Offline tests for build_aipo.py. Apache-2.0. MV2 of Munim, Inc."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import build_aipo as b  # noqa: E402

TESTS = ("BAN", "PUBLIC", "OPENNESS", "DATA", "CONTRACT", "NOTICE", "OTHER")


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def extras():
    return b.load_extras(os.path.join(HERE, "srcextra"))


class TestApplyPatch(unittest.TestCase):
    def setUp(self):
        self.base = {"version": "0.9.0", "status_note": "old", "coding_rules": ["R1"],
                     "cases": [{"case_id": "a", "status": "codable"},
                               {"case_id": "b", "status": "not_codable", "reason": "x"}]}
        self.patch = {"from_version": "0.9.0", "version": "0.9.1", "status_note": "new",
                      "add_rules": ["R10"], "replace": [{"case_id": "b", "status": "codable"}]}

    def test_replaces_in_place(self):
        out = b.apply_patch(self.base, self.patch)
        self.assertEqual(out["version"], "0.9.1")
        self.assertEqual(out["status_note"], "new")
        self.assertEqual(out["coding_rules"], ["R1", "R10"])
        self.assertEqual([c["case_id"] for c in out["cases"]], ["a", "b"])
        self.assertEqual(out["cases"][1], {"case_id": "b", "status": "codable"})
        self.assertEqual(self.base["cases"][1]["status"], "not_codable")  # base untouched

    def test_refuses_wrong_version_unknown_or_repeated_case(self):
        with self.assertRaises(ValueError):
            b.apply_patch(dict(self.base, version="0.8.0"), self.patch)
        with self.assertRaises(ValueError):
            b.apply_patch(self.base, dict(self.patch, replace=[{"case_id": "zz"}]))
        with self.assertRaises(ValueError):
            b.apply_patch(self.base, dict(self.patch, replace=[{"case_id": "a"}, {"case_id": "a"}]))

    def test_chain(self):
        p2 = {"from_version": "0.9.1", "version": "0.9.2", "status_note": "newer",
              "add_rules": ["R11"], "replace": [{"case_id": "a", "status": "not_codable", "reason": "y"}]}
        out = b.apply_chain(self.base, [self.patch, p2])
        self.assertEqual(out["version"], "0.9.2")
        self.assertEqual(out["coding_rules"], ["R1", "R10", "R11"])
        self.assertEqual(out["cases"][0]["status"], "not_codable")
        with self.assertRaises(ValueError):
            b.apply_chain(self.base, [p2])

    def test_default_chain_names(self):
        self.assertEqual(b.PUBLISHED_PATCHES, ("patch-0.9.1.json", "patch-0.9.2.json"))


class TestPending(unittest.TestCase):
    def test_pending(self):
        cases = [{"case_id": "a", "status": "not_codable", "reason": "Pending (R10): x"},
                 {"case_id": "b", "status": "not_codable", "reason": "R2: no free copy"},
                 {"case_id": "c", "status": "codable"}]
        self.assertEqual(b.pending(cases), ["a"])


class TestVariants(unittest.TestCase):
    def test_alternative_readings(self):
        cases = [
            {"case_id": "p", "status": "codable", "setup_a": "unclear", "reading_rule": "provider_contract",
             "self_hosting_named": False},
            {"case_id": "m", "status": "codable", "setup_a": "unclear", "reading_rule": "public_model",
             "self_hosting_named": False},
            {"case_id": "c", "status": "codable", "setup_a": "conditional", "self_hosting_named": False},
            {"case_id": "s", "status": "codable", "setup_a": "permitted", "reading_rule": "own_systems_exclusion",
             "self_hosting_named": True},
            {"case_id": "v", "status": "codable", "setup_a": "unclear",
             "reading_rule": "self_hosted_contract_proviso", "self_hosting_named": True},
            {"case_id": "n", "status": "not_codable", "reason": "R2", "reading_rule": "provider_contract"},
        ]
        texts = {"p": "x", "m": "tools, whether cloud-based or otherwise.", "c": "y", "s": "z", "v": "w"}
        v = b.variants(cases, texts, b.norm)
        self.assertEqual(v["provider_contract->forbidden"][1], ["p"])
        self.assertEqual(v["provider_contract->forbidden"][0][0]["setup_a"], "forbidden")
        self.assertEqual(v["public_model->permitted"][1], ["m"])
        self.assertEqual(v["provisos_not_copied->permitted"][1], [])
        self.assertEqual(v["self_hosted_contract_proviso->permitted"][1], ["v"])
        self.assertEqual(v["conditional->forbidden"][1], ["c"])
        self.assertEqual(v["cloud"][1], ["m"])
        self.assertEqual(sorted(v["all_reading_rules_reversed"][1]), ["m", "p", "v"])
        self.assertEqual(cases[0]["setup_a"], "unclear")  # input untouched
        self.assertEqual(len(v), 8)


class TestPatchFile(unittest.TestCase):
    def setUp(self):
        self.patch = load("patch-1.0.0.json")
        self.cases = {c["case_id"]: c for c in self.patch["replace"]}

    def test_shape(self):
        self.assertEqual(self.patch["from_version"], "0.9.2")
        self.assertEqual(self.patch["version"], "1.0.0")
        ids = [c["case_id"] for c in self.patch["replace"]]
        self.assertEqual(sorted(ids), ["dunn-v-lexisnexis", "fischman-v-epic", "velez-v-oneplus"])
        self.assertEqual(self.cases["fischman-v-epic"]["status"], "codable")
        self.assertEqual(self.cases["velez-v-oneplus"]["status"], "codable")
        self.assertEqual(self.cases["dunn-v-lexisnexis"]["status"], "not_codable")
        self.assertEqual(b.pending(self.patch["replace"]), [])
        self.assertEqual([r[:3] for r in self.patch["add_rules"]], ["R13"])

    def test_codes(self):
        f, v = self.cases["fischman-v-epic"], self.cases["velez-v-oneplus"]
        self.assertEqual((f["setup_a"], f["reading_rule"], f["self_hosting_named"]),
                         ("unclear", "provider_contract", False))
        self.assertEqual((v["setup_a"], v["reading_rule"], v["self_hosting_named"]),
                         ("unclear", "self_hosted_contract_proviso", True))
        self.assertIn(v["reading_rule"], b.ALTERNATIVES)

    def test_codable_cases_are_complete(self):
        for c in self.patch["replace"]:
            if c["status"] != "codable":
                self.assertTrue(c.get("reason"), c["case_id"])
                continue
            self.assertTrue(c["spans"] and c["tests"] and c["court"], c["case_id"])
            self.assertIn(c["setup_a"], ("permitted", "conditional", "forbidden", "unclear"))
            self.assertTrue(c["setup_a_quote"])
            if c["setup_a"] == "unclear":
                self.assertTrue(c.get("setup_a_reason") and c.get("reading_rule"), c["case_id"])
            if c["self_hosting_named"]:
                self.assertTrue(c["self_hosting_quote"], c["case_id"])
            for t in c["tests"]:
                self.assertIn(t, TESTS)

    def test_src_docs_exist(self):
        man = {o["case_id"] for o in load("build_manifest.json")["orders"]}
        known = man | set(extras()) | {"velez-oneplus"}
        for c in self.patch["replace"]:
            for sp in c.get("spans", []):
                self.assertTrue(sp["doc"].startswith("src:"))
                self.assertIn(sp["doc"][4:], known)

    def test_velez_provisos_offline(self):
        """The Velez span and quotations on the pasted passage check out with the grader's rules."""
        text = b.norm(extras()["velez-oneplus-provisos"])
        sp = self.cases["velez-v-oneplus"]["spans"][1]
        s, e = b.norm(sp["start"]), b.norm(sp["end"])
        self.assertEqual(text.count(s), 1)
        i = text.find(s)
        j = text.find(e, i)
        self.assertGreater(j, i)
        span = text[i:j + len(e)]
        v = self.cases["velez-v-oneplus"]
        for q in (v["tests"]["CONTRACT"], v["tests"]["OTHER"], v["self_hosting_quote"], v["setup_a_quote"]):
            self.assertIn(b.norm(q), span)
        for k in range(1, 6):
            self.assertIn("%d. " % k, span)


class TestManifest(unittest.TestCase):
    def test_orders(self):
        orders = load("build_manifest.json")["orders"]
        self.assertEqual(len(orders), 14)
        self.assertEqual(len({o["case_id"] for o in orders}), 14)
        self.assertEqual(sum(1 for o in orders if o["use"] == "text"), 10)
        ocr = sorted(o["case_id"] for o in orders if o["use"] == "ocr")
        self.assertEqual(ocr, ["us-v-dejesus", "us-v-jones-sdny", "us-v-santos", "us-v-sarris"])
        for o in orders:
            self.assertIn(len(o["sha256"]), (0, 64))
            self.assertTrue(o["url"].startswith("https://storage.courtlistener.com/recap/gov.uscourts."))
            self.assertTrue(o["url"].endswith(".%d.0.pdf" % o["ecf"]))
            if o["use"] == "ocr":
                self.assertEqual(len(o["text_sha256"]), 64)
        self.assertEqual([o["case_id"] for o in orders if not o["sha256"]], ["velez-v-oneplus-pdf"])
        by = {o["case_id"]: o for o in orders}
        for k in ("fischman-v-epic", "dunn-v-lexisnexis"):
            self.assertEqual(by[k]["extracted_on"], "2026-11-02")
            self.assertEqual(len(by[k]["text_sha256"]), 64)
        self.assertIn(by["velez-v-oneplus-pdf"]["check_passage"], extras())


class TestIntegrity(unittest.TestCase):
    def test_failures(self):
        orders = [{"case_id": "a", "sha256_matches_pinned": True, "text_matches_pinned": True},
                  {"case_id": "b", "sha256_matches_pinned": None},
                  {"case_id": "c", "sha256_matches_pinned": False},
                  {"case_id": "d", "sha256_matches_pinned": True, "text_matches_pinned": False},
                  {"case_id": "e", "error": "boom"}]
        bad = b.integrity_failures(orders)
        self.assertEqual([x.split(":")[0] for x in bad], ["c", "d", "e"])


class TestText(unittest.TestCase):
    def test_furniture(self):
        raw = ("Case 1:26-cr-00391-ABC Document 10 Filed 09/10/26 Page 3 of 6\n"
               "7. Restrictions on Use\n3\n- 4 -\nof AI\n")
        text, removed = b.strip_page_furniture(raw)
        self.assertEqual(removed, 3)
        self.assertEqual(b.norm(text), "7. Restrictions on Use of AI")

    def test_norm_quotes(self):
        self.assertEqual(b.norm("“AI tool” does\n not include"), '"AI tool" does not include')

    def test_passage_body(self):
        self.assertEqual(b.passage_body("header line\n\nbody\nmore\n"), "body\nmore\n")
        self.assertEqual(b.passage_body("no body"), "")

    def test_post_text_marks_blockquotes(self):
        t = b.to_text("<p>Intro</p><blockquote><p>Quoted “AI”</p></blockquote>")
        self.assertEqual(t, "Intro\n> Quoted “AI”\n")

    def test_prefix_diag(self):
        d = b.prefix_diag(b.norm, "alpha beta gamma", "alpha beta delta")
        self.assertEqual(d["prefix_words_found"], 2)
        self.assertEqual(b.prefix_diag(b.norm, "a b", "a b")["occurrences"], 1)


if __name__ == "__main__":
    unittest.main()
