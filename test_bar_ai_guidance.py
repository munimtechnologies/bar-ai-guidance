"""Checks for data/guidance.json. Standard library only.

Run:  python -m unittest test_bar_ai_guidance
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "guidance.json")

REQUIRED = [
    "id", "jurisdiction", "issuer", "title", "number", "date", "kind", "binding",
    "url", "url_verified", "verification", "confidentiality_note",
    "in_house_tools_note", "notes",
]
KINDS = {"formal_opinion", "advisory_opinion", "guidance", "court_notice"}
BINDING = {"advisory", "court_rule"}
VERIFICATION = {"fetched", "cited"}
DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
JURIS_RE = re.compile(r"^(US|DC|[A-Z]{2})$")
PRIMARY_HOSTS = (
    "americanbar.org", "calbar.ca.gov", "dcbar.org", "floridabar.org", "kybar.org",
    "njcourts.gov", "nycbar.org", "ncbar.gov", "pabar.org", "legalethicstexas.com",
)


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


class GuidanceDataTest(unittest.TestCase):
    def setUp(self):
        self.doc = load()
        self.entries = self.doc["entries"]

    def test_top_level(self):
        for key in ("dataset", "version", "updated", "license", "fields", "entries"):
            self.assertIn(key, self.doc)
        self.assertTrue(DAY_RE.match(self.doc["updated"]))
        self.assertGreaterEqual(len(self.entries), 10)
        self.assertEqual(set(self.doc["fields"]), set(REQUIRED))

    def test_required_fields_present(self):
        for e in self.entries:
            for key in REQUIRED:
                self.assertIn(key, e, f"{e.get('id')} lacks {key}")
            self.assertEqual(set(e), set(REQUIRED), f"{e['id']} has unexpected keys")

    def test_ids_and_urls_unique(self):
        ids = [e["id"] for e in self.entries]
        urls = [e["url"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(urls), len(set(urls)))
        for i in ids:
            self.assertRegex(i, r"^[a-z0-9][a-z0-9-]*$")

    def test_enums_and_dates(self):
        for e in self.entries:
            self.assertIn(e["kind"], KINDS, e["id"])
            self.assertIn(e["binding"], BINDING, e["id"])
            self.assertIn(e["verification"], VERIFICATION, e["id"])
            self.assertRegex(e["date"], DATE_RE, e["id"])
            self.assertRegex(e["url_verified"], DAY_RE, e["id"])
            self.assertRegex(e["jurisdiction"], JURIS_RE, e["id"])
            self.assertLessEqual(e["url_verified"], self.doc["updated"], e["id"])

    def test_urls_are_primary_https(self):
        for e in self.entries:
            self.assertTrue(e["url"].startswith("https://"), e["id"])
            host = e["url"].split("/")[2].lower()
            self.assertTrue(any(host == h or host.endswith("." + h) for h in PRIMARY_HOSTS),
                            f"{e['id']}: {host} is not a listed primary host")

    def test_notes_are_sentences_not_quotes(self):
        for e in self.entries:
            note = e["confidentiality_note"]
            self.assertTrue(note and len(note) > 40, e["id"])
            self.assertFalse(note.startswith('"'), f"{e['id']}: paraphrase, do not quote")
            for key in ("in_house_tools_note", "notes"):
                self.assertTrue(e[key] is None or isinstance(e[key], str), e["id"])

    def test_no_mv2_described_as_an_ai(self):
        text = json.dumps(self.doc).lower()
        self.assertNotIn("mv2, an ai", text)
        self.assertNotIn("mv2 (an ai", text)
        self.assertNotIn("mv2 of munim, inc., an ai", text)


if __name__ == "__main__":
    unittest.main()
