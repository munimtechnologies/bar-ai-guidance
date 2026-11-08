# SPDX-License-Identifier: Apache-2.0
"""Checks for the ai-protective-orders agent skill (skills/ai-protective-orders).

Run from the repository root:  python -m unittest test_ai_protective_orders_skill
Standard library only. No test touches the network: real-data tests read
data/ai_protective_orders.json from this checkout, and the rest use a small synthetic dataset
written to a temporary folder. Made with AI agents working in MV2's (Munim, Inc.) name.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(ROOT, "skills", "ai-protective-orders")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
SCRIPT = os.path.join(SKILL_DIR, "scripts", "ai_protective_orders.py")
DATA = os.path.join(ROOT, "data", "ai_protective_orders.json")


def _load_script():
    spec = importlib.util.spec_from_file_location("ai_protective_orders", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


APO = _load_script()
with open(DATA, encoding="utf-8") as _fh:
    DATASET = json.load(_fh)
with open(SKILL_MD, encoding="utf-8") as _fh:
    SKILL_TEXT = _fh.read().replace("\r\n", "\n")
CASES = DATASET["cases"]
CODED = [c for c in CASES if c.get("status") == "codable"]
IDS = set(c["case_id"] for c in CASES)


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = APO.main(argv)
    return code, out.getvalue(), err.getvalue()


def run_json(argv):
    code, out, err = run(argv + ["--json"])
    return code, (json.loads(out) if out.strip() else None)


def frontmatter(text):
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must start with a '---' line")
    end = text.index("\n---\n", 4)
    fields = {}
    for line in text[4:end].split("\n"):
        if line.strip():
            key, _, value = line.partition(": ")
            fields[key.strip()] = value.strip()
    return fields


def documented_commands():
    prefix = "python scripts/ai_protective_orders.py"
    return [line.strip() for line in SKILL_TEXT.split("\n") if line.strip().startswith(prefix)]


class SkillFileTest(unittest.TestCase):
    def test_frontmatter(self):
        fields = frontmatter(SKILL_TEXT)
        self.assertEqual(set(fields), {"name", "description", "license"})
        self.assertEqual(fields["name"], "ai-protective-orders")
        self.assertEqual(fields["name"], os.path.basename(SKILL_DIR))
        self.assertRegex(fields["name"], r"^[a-z0-9-]{1,64}$")
        desc = fields["description"]
        self.assertTrue(40 <= len(desc) <= 1024, len(desc))
        self.assertNotIn(": ", desc)
        self.assertFalse(desc.startswith(("'", '"')))
        self.assertIn("not legal advice", desc)
        self.assertEqual(fields["license"], "Apache-2.0")

    def test_disclosure_and_licence(self):
        self.assertIn("Made with AI agents working in MV2's (Munim, Inc.) name", SKILL_TEXT)
        self.assertIn("not legal advice", SKILL_TEXT.lower())
        self.assertIn("Apache-2.0", SKILL_TEXT)
        self.assertIsNone(re.search(r"\bMIT\b", SKILL_TEXT))
        with open(SCRIPT, encoding="utf-8") as fh:
            script = fh.read()
        self.assertIn("SPDX-License-Identifier: Apache-2.0", script)
        self.assertIsNone(re.search(r"\bMIT\b", script))

    def test_every_cited_id_exists(self):
        cited = set(re.findall(r"`([a-z0-9-]+-v-[a-z0-9-]+|in-re-[a-z0-9-]+)`", SKILL_TEXT))
        cited |= set(re.findall(r"--id ([a-z0-9-]+)", SKILL_TEXT))
        self.assertGreaterEqual(len(cited), 5)
        self.assertEqual(sorted(cited - IDS), [])

    def test_documented_commands_run(self):
        cmds = documented_commands()
        self.assertGreaterEqual(len(cmds), 7)
        for cmd in cmds:
            argv = shlex.split(cmd)[2:] + ["--file", DATA]
            code, out, err = run(argv)
            self.assertEqual(code, 0, "%s -> %s %s" % (cmd, code, err))
            if "--json" in argv:
                self.assertIn("cases", json.loads(out))

    def test_test_codes_documented_and_known(self):
        for code in APO.TEST_LABELS:
            self.assertIn("`%s`" % code, SKILL_TEXT, code)
        used = set(k for c in CODED for k in (c.get("tests") or {}))
        self.assertEqual(sorted(used - set(APO.TEST_LABELS)), [])

    def test_script_version(self):
        self.assertEqual(APO.__version__, "0.1.0")


class RealDataTest(unittest.TestCase):
    def test_summary(self):
        code, out, _ = run(["--summary", "--file", DATA])
        self.assertEqual(code, 0)
        lines = out.split("\n")
        self.assertEqual(lines[0], "%d cases, %d coded, version %s"
                         % (len(CASES), len(CODED), DATASET["version"]))
        self.assertTrue(lines[2].startswith("setup A (coded cases): permitted "), lines[2])
        self.assertGreaterEqual(len(CODED), 40)

    def test_setup_counts_match_data(self):
        total = 0
        for setup in APO.SETUP_LABELS:
            code, got = run_json(["--setup", setup, "--file", DATA])
            expected = [c["case_id"] for c in CODED if c.get("setup_a") == setup]
            self.assertEqual([c["case_id"] for c in got["cases"]], expected, setup)
            self.assertEqual(code, 0 if expected else 1)
            total += len(expected)
        self.assertEqual(total, len(CODED))

    def test_warner_ban(self):
        code, out, _ = run(["--id", "warner-v-gilbarco", "--quotes", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("[warner-v-gilbarco] E.D. Mich. | forbidden | ", out)
        self.assertIn("  Clause tests: BAN", out)
        self.assertIn("    BAN (bars putting the material into any AI platform): \"", out)
        self.assertIn(APO.FOOTER, out)

    def test_sarris_own_systems(self):
        code, out, _ = run(["--id", "us-v-sarris", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("[us-v-sarris] S.D.N.Y. | permitted | ", out)
        self.assertIn("  Names self-hosting: \"", out)

    def test_court_spellings(self):
        expected = [c["case_id"] for c in CASES if c.get("court") == "S.D.N.Y."]
        self.assertGreaterEqual(len(expected), 10)
        for spelling in ("S.D.N.Y.", "sdny", "SDNY", "s.d.n.y"):
            code, got = run_json(["--court", spelling, "--file", DATA])
            self.assertEqual(code, 0, spelling)
            self.assertEqual([c["case_id"] for c in got["cases"]], expected, spelling)

    def test_each_test_code_filter(self):
        for test in APO.TEST_LABELS:
            code, got = run_json(["--test", test.lower(), "--file", DATA])
            expected = [c["case_id"] for c in CASES if test in (c.get("tests") or {})]
            self.assertEqual([c["case_id"] for c in got["cases"]], expected, test)

    def test_self_hosting_filter(self):
        code, got = run_json(["--self-hosting", "--file", DATA])
        expected = [c["case_id"] for c in CASES if c.get("self_hosting_named") is True]
        self.assertGreaterEqual(len(expected), 2)
        self.assertEqual([c["case_id"] for c in got["cases"]], expected)
        self.assertIn("us-v-sarris", expected)

    def test_refusals_print_status(self):
        refusals = [c for c in CASES if c.get("status") == "refusal"]
        self.assertGreaterEqual(len(refusals), 1)
        code, out, _ = run(["--status", "refusal", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("  Status: a court refused a proposed AI clause", out)
        self.assertNotIn("  Setup A:", out)

    def test_local_checkout_is_default(self):
        self.assertEqual(os.path.normcase(os.path.abspath(APO.local_data_path())),
                         os.path.normcase(os.path.abspath(DATA)))
        code, out, _ = run(["--summary"])
        self.assertEqual(code, 0)
        self.assertIn("source: ", out)
        self.assertNotIn("raw.githubusercontent.com", out)


FIXTURE = {
    "version": "9.9.9",
    "license": "CC BY 4.0",
    "cases": [
        {"case_id": "a-v-b", "caption": "A v. B", "court": "N.D. Cal.", "case_no": "1 WL 1",
         "order": "Order one", "status": "codable",
         "tests": {"DATA": "Data words", "PUBLIC": "Public words"},
         "self_hosting_named": False, "self_hosting_quote": "",
         "openness_named": False, "openness_quote": "",
         "setup_a": "permitted", "setup_a_quote": "Permit words"},
        {"case_id": "c-v-d", "caption": "C v. D", "court": "D. Colo.", "case_no": "2 WL 2",
         "order": "Order two", "status": "codable", "tests": {"CONTRACT": "Contract words"},
         "self_hosting_named": True, "self_hosting_quote": "own servers",
         "openness_named": False, "openness_quote": "",
         "setup_a": "unclear", "setup_a_quote": "Unclear words",
         "setup_a_reason": "Reason text", "reading_rule": "provider_contract",
         "note": "Note text"},
        {"case_id": "e-v-f", "caption": "E v. F", "court": "D. Colo.", "case_no": "3 WL 3",
         "order": "Order three", "status": "not_codable", "reason": "No free copy"},
    ],
}


class SyntheticDataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "ai_protective_orders.json")
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(FIXTURE, fh)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_match(self):
        code, out, _ = run(["--court", "EDNY", "--file", self.path])
        self.assertEqual(code, 1)
        self.assertIn("0 of 3 cases matched", out)
        self.assertIn("No case matched.", out)
        self.assertIn("no match does not mean no court has such an order", out)

    def test_quotes_and_notes_only_on_request(self):
        code, out, _ = run(["--id", "c-v-d", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertIn("[c-v-d] D. Colo. | unclear | 2 WL 2", out)
        self.assertIn("  Setup A: unclear (the order's words do not settle it)", out)
        self.assertIn("    order's words: \"Unclear words\"", out)
        self.assertIn("    why: Reason text", out)
        self.assertIn("    reading rule: provider_contract", out)
        self.assertIn("  Names self-hosting: \"own servers\"", out)
        self.assertNotIn("Contract words", out)
        self.assertNotIn("Note text", out)
        code, out, _ = run(["--id", "c-v-d", "--quotes", "--notes", "--file", self.path])
        self.assertIn("    CONTRACT (asks for a contract or commitment from the AI provider or "
                      "platform): \"Contract words\"", out)
        self.assertIn("  Note: Note text", out)

    def test_not_codable(self):
        code, out, _ = run(["--court", "dcolo", "--status", "not_codable", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertIn("[e-v-f] D. Colo. | not_codable | 3 WL 3", out)
        self.assertIn("  Reason: No free copy", out)
        self.assertNotIn("[c-v-d]", out)

    def test_grep_searches_test_quotes(self):
        code, out, _ = run(["--grep", "PUBLIC WORDS", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertIn("[a-v-b]", out)
        self.assertNotIn("[c-v-d]", out)

    def test_json_labels(self):
        code, got = run_json(["--setup", "permitted", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertEqual(got["matched"], 1)
        case = got["cases"][0]
        self.assertEqual(case["setup_a_label"], "the order's words allow it")
        self.assertEqual(case["status_label"], "coded")
        self.assertEqual(sorted(case["test_labels"]), ["DATA", "PUBLIC"])
        self.assertEqual(got["version"], "9.9.9")
        self.assertIn("not legal advice", got["not_legal_advice"])

    def test_summary_counts(self):
        code, out, _ = run(["--summary", "--file", self.path])
        self.assertEqual(code, 0)
        lines = out.split("\n")
        self.assertEqual(lines[0], "3 cases, 2 coded, version 9.9.9")
        self.assertEqual(lines[1], "by status: codable 2, not_codable 1")
        self.assertEqual(lines[2], "setup A (coded cases): permitted 1, conditional 0, "
                                   "unclear 1, forbidden 0")
        self.assertEqual(lines[3], "clause tests: CONTRACT 1, DATA 1, PUBLIC 1")
        self.assertEqual(lines[4], "courts (2): D. Colo. 2, N.D. Cal. 1")
        self.assertEqual(lines[5], "self-hosting named in 1 coded cases")

    def test_bad_inputs_exit_2(self):
        self.assertEqual(run(["--test", "XYZ", "--file", self.path])[0], 2)
        self.assertEqual(run(["--setup", "maybe", "--file", self.path])[0], 2)
        self.assertEqual(run(["--file", os.path.join(self.tmp.name, "absent.json")])[0], 2)
        bad = os.path.join(self.tmp.name, "bad.json")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("not json")
        self.assertEqual(run(["--file", bad])[0], 2)
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump({"version": "1"}, fh)
        self.assertEqual(run(["--file", bad])[0], 2)
        self.assertEqual(run(["--url", "http://example.org/x.json"])[0], 2)


if __name__ == "__main__":
    unittest.main()
