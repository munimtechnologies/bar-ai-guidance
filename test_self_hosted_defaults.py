"""Checks for data/self_hosted_defaults.json. Standard library only.

SPDX-License-Identifier: Apache-2.0

Run:  python -m unittest test_self_hosted_defaults
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "self_hosted_defaults.json")

REQUIRED = [
    "id", "project", "role", "release_seen", "listen_direct", "listen_container",
    "credential_by_default", "credential_options", "signup_default", "other_defaults",
    "out_of_the_box", "sources", "notes",
]
ROLES = {"model_server", "chat_app"}
CREDENTIAL = {"none", "key", "login"}
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_RE = re.compile(r"^v?\d+(\.\d+)*$")
SOURCE_HOSTS = (
    "github.com", "docs.vllm.ai", "docs.openwebui.com", "docs.anythingllm.com",
    "docs.useanything.com", "docs.dify.ai",
)


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


class SelfHostedDefaultsTest(unittest.TestCase):
    def setUp(self):
        self.doc = load()
        self.entries = self.doc["entries"]

    def test_top_level(self):
        for key in ("dataset", "version", "checked", "license", "purpose", "fields", "entries"):
            self.assertIn(key, self.doc)
        self.assertTrue(DAY_RE.match(self.doc["checked"]))
        self.assertGreaterEqual(len(self.entries), 11)
        self.assertEqual(set(self.doc["fields"]), set(REQUIRED))

    def test_entries_have_exactly_the_fields(self):
        for e in self.entries:
            self.assertEqual(set(e), set(REQUIRED), e.get("id"))

    def test_ids_unique_and_sorted(self):
        ids = [e["id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))
        for i in ids:
            self.assertRegex(i, r"^[a-z0-9][a-z0-9-]*$")

    def test_enums(self):
        for e in self.entries:
            self.assertIn(e["role"], ROLES, e["id"])
            self.assertIn(e["credential_by_default"], CREDENTIAL, e["id"])
            self.assertRegex(e["release_seen"], TAG_RE, e["id"])

    def test_enums_documented(self):
        fields = self.doc["fields"]
        documented = set(re.findall(r"\b(model_server|chat_app)\b", fields["role"]))
        self.assertEqual(documented, ROLES)
        for value in CREDENTIAL:
            self.assertIn(f"{value} = ", fields["credential_by_default"])

    def test_signup_only_for_chat_apps(self):
        for e in self.entries:
            if e["role"] == "model_server":
                self.assertIsNone(e["signup_default"], e["id"])
            else:
                self.assertTrue(e["signup_default"], e["id"])

    def test_key_entries_say_how_start_is_refused(self):
        for e in self.entries:
            if e["credential_by_default"] == "key":
                self.assertIn("refuses to start", e["other_defaults"] or "", e["id"])

    def test_every_entry_says_where_it_listens(self):
        for e in self.entries:
            self.assertTrue(e["listen_direct"] or e["listen_container"], e["id"])

    def test_sources_are_project_files_or_docs(self):
        for e in self.entries:
            self.assertTrue(e["sources"], e["id"])
            for url in e["sources"]:
                self.assertTrue(url.startswith("https://"), url)
                host = url.split("/")[2].lower()
                self.assertIn(host, SOURCE_HOSTS, f"{e['id']}: {host}")

    def test_summary_is_a_sentence(self):
        for e in self.entries:
            s = e["out_of_the_box"]
            self.assertTrue(len(s) > 40 and s.endswith("."), e["id"])

    def test_no_legal_conclusions(self):
        text = json.dumps(self.doc).lower()
        for phrase in ("compliant", "violates", "complies with", "is legal", "is illegal"):
            self.assertNotIn(phrase, text)

    def test_no_mv2_described_as_an_ai(self):
        text = json.dumps(self.doc).lower()
        self.assertNotIn("mv2, an ai", text)
        self.assertNotIn("mv2 (an ai", text)


if __name__ == "__main__":
    unittest.main()
