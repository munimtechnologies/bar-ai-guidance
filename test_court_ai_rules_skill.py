# SPDX-License-Identifier: Apache-2.0
"""Checks for the court-ai-rules agent skill (skills/court-ai-rules). Standard library only.

Run from the repository root:  python -m unittest test_court_ai_rules_skill
No test touches the network: real-data tests read data/guidance.json from this checkout,
and the rest use a small synthetic index written to a temporary folder.
Made with AI agents working in MV2's (Munim, Inc.) name.
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
SKILL_DIR = os.path.join(ROOT, "skills", "court-ai-rules")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
SCRIPT = os.path.join(SKILL_DIR, "scripts", "court_ai_rules.py")
DATA = os.path.join(ROOT, "data", "guidance.json")


def _load_script():
    spec = importlib.util.spec_from_file_location("court_ai_rules", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAR = _load_script()
with open(DATA, encoding="utf-8") as _fh:
    INDEX = json.load(_fh)
with open(SKILL_MD, encoding="utf-8") as _fh:
    SKILL_TEXT = _fh.read().replace("\r\n", "\n")
ENTRIES = INDEX["entries"]
IDS = set(e["id"] for e in ENTRIES)


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = CAR.main(argv)
    return code, out.getvalue(), err.getvalue()


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
    prefix = "python scripts/court_ai_rules.py"
    return [line.strip() for line in SKILL_TEXT.split("\n") if line.strip().startswith(prefix)]


class SkillFileTest(unittest.TestCase):
    def test_frontmatter(self):
        fields = frontmatter(SKILL_TEXT)
        self.assertEqual(set(fields), {"name", "description", "license"})
        self.assertEqual(fields["name"], "court-ai-rules")
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
        cited = set(re.findall(r"`([a-z]{2}-[a-z0-9-]+)`", SKILL_TEXT))
        cited |= set(re.findall(r"--id ([a-z0-9-]+)", SKILL_TEXT))
        self.assertGreaterEqual(len(cited), 9)
        self.assertEqual(sorted(cited - IDS), [])

    def test_documented_commands_run(self):
        cmds = documented_commands()
        self.assertGreaterEqual(len(cmds), 7)
        for cmd in cmds:
            argv = shlex.split(cmd)[2:] + ["--file", DATA]
            code, out, err = run(argv)
            self.assertEqual(code, 0, "%s -> %s %s" % (cmd, code, err))
            if "--json" in argv:
                self.assertIn("entries", json.loads(out))

    def test_script_version(self):
        self.assertEqual(CAR.__version__, "0.1.0")


class RealIndexTest(unittest.TestCase):
    def test_summary(self):
        code, out, _ = run(["--summary", "--file", DATA])
        self.assertEqual(code, 0)
        lines = out.split("\n")
        self.assertEqual(lines[0], "%d entries, version %s (updated %s)"
                         % (len(ENTRIES), INDEX["version"], INDEX["updated"]))
        self.assertTrue(lines[1].startswith("by binding: "))
        codes = set(e["jurisdiction"] for e in ENTRIES)
        self.assertTrue(lines[2].startswith("jurisdictions (%d): US " % len(codes)), lines[2])

    def test_connecticut_court_rule(self):
        code, out, _ = run(["--state", "CT", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("[ct-practice-book-4-9-2026] CT | court rule | rule_amendment | 2026-06-11",
                      out)
        self.assertIn("https://www.jud.ct.gov/legalresources/Docs/LJDocs/Misc/2026/26/"
                      "pblj_8752.pdf", out)
        self.assertIn("[us-aba-512] US | advisory guidance", out)
        self.assertIn(CAR.FOOTER, out)

    def test_california_statute_label(self):
        code, out, _ = run(["--state", "CA", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("[ca-sb-574] CA | state statute | statute | 2026-09-30", out)

    def test_archived_label(self):
        code, out, _ = run(["--id", "ms-op-267", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertIn("archived copy of the issuer's own file (Internet Archive)", out)

    def test_no_national(self):
        code, out, _ = run(["--state", "NY", "--no-national", "--file", DATA])
        self.assertEqual(code, 0)
        self.assertNotIn("[us-aba-512]", out)
        self.assertIn("[ny-ucs-part-161] NY | court rule", out)

    def test_binding_filter_json(self):
        code, out, _ = run(["--binding", "court_rule", "--json", "--file", DATA])
        self.assertEqual(code, 0)
        got = json.loads(out)
        expected = [e["id"] for e in ENTRIES if e["binding"] == "court_rule"]
        self.assertGreaterEqual(len(expected), 9)
        self.assertEqual([e["id"] for e in got["entries"]], expected)
        self.assertEqual(set(e["binding_label"] for e in got["entries"]), {"court rule"})
        self.assertEqual(got["version"], INDEX["version"])

    def test_each_state_lookup_matches_index(self):
        for code_ in sorted(set(e["jurisdiction"] for e in ENTRIES) - {"US"}):
            code, out, _ = run(["--state", code_, "--no-national", "--json", "--file", DATA])
            self.assertEqual(code, 0, code_)
            got = [e["id"] for e in json.loads(out)["entries"]]
            self.assertEqual(got, [e["id"] for e in ENTRIES if e["jurisdiction"] == code_])

    def test_local_checkout_is_default(self):
        self.assertEqual(os.path.normcase(os.path.abspath(CAR.local_data_path())),
                         os.path.normcase(os.path.abspath(DATA)))
        code, out, _ = run(["--summary"])
        self.assertEqual(code, 0)
        self.assertIn("source: ", out)
        self.assertNotIn("raw.githubusercontent.com", out)


FIXTURE = {
    "version": "9.9.9",
    "updated": "2026-01-02",
    "entries": [
        {"id": "us-x", "jurisdiction": "US", "issuer": "Issuer A", "title": "T1",
         "number": None, "date": "2025", "kind": "formal_opinion", "binding": "advisory",
         "url": "https://example.org/a", "url_verified": "2026-01-01", "verification": "cited",
         "confidentiality_note": "Note one about confidentiality.", "in_house_tools_note": None,
         "notes": "First note text"},
        {"id": "ny-y", "jurisdiction": "NY", "issuer": "Issuer B", "title": "T2",
         "number": "Part 1", "date": "2026-01-01", "kind": "rule_amendment",
         "binding": "court_rule", "url": "https://example.org/b", "url_verified": "2026-01-01",
         "verification": "fetched", "confidentiality_note": "Note two about filings.",
         "in_house_tools_note": "In-house text", "notes": "Second note text"},
    ],
}


class SyntheticIndexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "guidance.json")
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(FIXTURE, fh)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_state_keeps_national(self):
        code, out, _ = run(["--state", "MD", "--file", self.path])
        self.assertEqual(code, 1)
        self.assertIn("No entry for MD in bar-ai-guidance 9.9.9 (updated 2026-01-02).", out)
        self.assertIn("That does not mean MD has no rule", out)
        self.assertIn("[us-x] US | advisory guidance | formal_opinion | 2025", out)

    def test_missing_state_no_national(self):
        code, out, _ = run(["--state", "MD", "--no-national", "--file", self.path])
        self.assertEqual(code, 1)
        self.assertNotIn("[us-x]", out)
        self.assertIn("0 of 2 entries matched", out)

    def test_filtered_missing_wording(self):
        code, out, _ = run(["--state", "NY", "--binding", "advisory", "--no-national",
                            "--file", self.path])
        self.assertEqual(code, 1)
        self.assertIn("No matching entry for NY", out)

    def test_notes_only_on_request(self):
        code, out, _ = run(["--state", "NY", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertNotIn("Second note text", out)
        self.assertIn("  In-house tools: In-house text", out)
        self.assertIn("  T2 (Part 1)", out)
        self.assertIn("issuer's own page or file, retrieved and title matched", out)
        code, out, _ = run(["--state", "NY", "--notes", "--file", self.path])
        self.assertIn("  Notes: Second note text", out)

    def test_codes_case_and_commas(self):
        code, out, _ = run(["--state", "ny, us", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertIn("[ny-y]", out)
        self.assertIn("[us-x]", out)
        self.assertNotIn("No entry", out)

    def test_grep_and_kind(self):
        code, out, _ = run(["--grep", "NOTE ONE", "--file", self.path])
        self.assertEqual(code, 0)
        self.assertIn("[us-x]", out)
        self.assertNotIn("[ny-y]", out)
        code, out, _ = run(["--kind", "statute", "--file", self.path])
        self.assertEqual(code, 1)

    def test_json_labels(self):
        code, out, _ = run(["--id", "us-x", "--json", "--file", self.path])
        self.assertEqual(code, 0)
        got = json.loads(out)
        self.assertEqual(got["matched"], 1)
        self.assertEqual(got["missing"], [])
        self.assertEqual(got["entries"][0]["link_label"],
                         "issuer's own address, cited but not retrieved")
        self.assertEqual(got["entries"][0]["binding_label"], "advisory guidance")

    def test_bad_inputs_exit_2(self):
        self.assertEqual(run(["--state", "NEWYORK", "--file", self.path])[0], 2)
        self.assertEqual(run(["--file", os.path.join(self.tmp.name, "absent.json")])[0], 2)
        bad = os.path.join(self.tmp.name, "bad.json")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("not json")
        self.assertEqual(run(["--file", bad])[0], 2)
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump({"version": "1"}, fh)
        self.assertEqual(run(["--file", bad])[0], 2)
        self.assertEqual(run(["--url", "http://example.org/guidance.json"])[0], 2)


if __name__ == "__main__":
    unittest.main()
