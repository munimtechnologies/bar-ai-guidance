# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Checks for data/agency_ai_rules.json (AI rules of U.S. administrative tribunals)."""
import json
import os
import re
import unittest
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "agency_ai_rules.json")

KEYS = ["id", "level", "state", "tribunal", "instrument", "kind", "issued", "effective", "status",
        "applies_to", "disclosure", "certification", "verification_duty", "ai_term", "authority_cited",
        "sanctions", "url", "other_urls", "source_check", "in_lag_tracker", "notes"]
ENUMS = {
    "level": {"federal", "state"},
    "kind": {"order_general", "order_per_case", "rule", "policy", "advisory", "guidance", "decision", "web_page"},
    "status": {"in_force", "rejected", "unknown"},
    "disclosure": {"required_every_filing", "required_if_used", "on_request", "encouraged", "not_required",
                   "unverified"},
    "certification": {"required_every_filing", "required_if_used", "on_request", "none", "unverified"},
    "verification_duty": {"yes", "not_explicit", "unverified"},
    "ai_term": {"artificial intelligence", "super intelligence"},
    "source_check": {"issuer_page", "issuer_listing", "secondary"},
    "in_lag_tracker": {"yes", "partial", "no"},
}
# Issuers' own hosts. content.govdelivery.com/accounts/USIRS is the IRS's own e-mail bulletin service.
ISSUER_HOSTS = ("dol.gov", "justice.gov", "ftc.gov", "federalregister.gov", "georgia.gov", "idaho.gov",
                "proddfmmainsa.blob.core.windows.net", "mass.gov", "mn.gov", "mt.gov", "texas.gov",
                "irs.gov", "govdelivery.com", "sc.gov", "ca.gov")
STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
          "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
          "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"}
DATE_RX = re.compile(r"^20\d\d-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?$")


def load():
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def host_ok(url):
    if not url.startswith("https://"):
        return False
    host = urllib.parse.urlsplit(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in ISSUER_HOSTS)


class AgencyAiRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load()
        cls.entries = cls.doc["entries"]

    def test_top_level(self):
        for k in ("name", "version", "as_of", "license", "made_by", "description", "fields", "entries"):
            self.assertIn(k, self.doc)
        self.assertEqual(self.doc["license"], "CC-BY-4.0")
        self.assertRegex(self.doc["version"], r"^\d+\.\d+\.\d+$")
        self.assertTrue(DATE_RX.match(self.doc["as_of"]))
        self.assertIn("AI agents", self.doc["made_by"])

    def test_count_and_order(self):
        self.assertGreaterEqual(len(self.entries), 16)
        ids = [e["id"] for e in self.entries]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertRegex(i, r"^us-[a-z0-9-]+$")

    def test_keys_in_order(self):
        for e in self.entries:
            self.assertEqual(list(e.keys()), KEYS, e["id"])

    def test_enums(self):
        for e in self.entries:
            for k, allowed in ENUMS.items():
                self.assertIn(e[k], allowed, "%s %s=%r" % (e["id"], k, e[k]))

    def test_level_and_state(self):
        for e in self.entries:
            if e["level"] == "federal":
                self.assertIsNone(e["state"], e["id"])
            else:
                self.assertIn(e["state"], STATES, e["id"])

    def test_dates(self):
        for e in self.entries:
            for k in ("issued", "effective"):
                if e[k] is not None:
                    self.assertTrue(DATE_RX.match(e[k]), "%s %s=%r" % (e["id"], k, e[k]))
            if e["issued"] and e["effective"] and len(e["issued"]) == 10 and len(e["effective"]) == 10:
                self.assertLessEqual(e["issued"], e["effective"], e["id"])
            if e["issued"]:
                self.assertLessEqual(e["issued"][:7], self.doc["as_of"][:7], e["id"])

    def test_urls_are_issuer_https(self):
        for e in self.entries:
            self.assertTrue(host_ok(e["url"]), e["url"])
            self.assertIsInstance(e["other_urls"], list)
            for u in e["other_urls"]:
                self.assertTrue(host_ok(u), u)
                self.assertNotEqual(u, e["url"])

    def test_lists_and_text(self):
        for e in self.entries:
            self.assertIsInstance(e["applies_to"], list)
            self.assertTrue(e["applies_to"], e["id"])
            self.assertIsInstance(e["authority_cited"], list)
            for k in ("tribunal", "instrument", "notes"):
                self.assertIsInstance(e[k], str)
                self.assertGreater(len(e[k]), 10, "%s %s" % (e["id"], k))
            self.assertTrue(e["sanctions"] is None or isinstance(e["sanctions"], str))

    def test_super_intelligence_term_only_federal(self):
        for e in self.entries:
            if e["ai_term"] == "super intelligence":
                self.assertEqual(e["level"], "federal", e["id"])

    def test_rejected_entries_have_no_effective_date(self):
        for e in self.entries:
            if e["status"] == "rejected":
                self.assertIsNone(e["effective"], e["id"])

    def test_known_entries(self):
        by_id = {e["id"]: e for e in self.entries}
        self.assertEqual(by_id["us-id-idapa-62-0101-2501-ai-sections"]["status"], "rejected")
        self.assertEqual(by_id["us-dol-arb-si-note"]["ai_term"], "super intelligence")
        self.assertEqual(by_id["us-ga-sbwc-ai-standing-order-2026"]["disclosure"], "required_every_filing")
        self.assertEqual(by_id["us-dol-oalj-order-2026-mis-00004"]["issued"], "2026-07-08")
        self.assertEqual(by_id["us-sc-wcc-ai-bench-order-2026"]["issued"], "2026-06-17")
        self.assertEqual(by_id["us-sc-wcc-ai-bench-order-2026"]["state"], "SC")
        self.assertEqual(by_id["us-irs-opr-alert-2026-19"]["issued"], "2026-06-24")
        self.assertEqual(by_id["us-irs-opr-alert-2026-19"]["verification_duty"], "yes")
        self.assertIn("31 CFR 10.22", by_id["us-irs-opr-alert-2026-19"]["authority_cited"])
        perb = by_id["us-ca-perb-atwater-2995e"]
        self.assertEqual(perb["state"], "CA")
        self.assertEqual(perb["kind"], "decision")
        self.assertEqual(perb["issued"], "2025-12-15")
        self.assertEqual(perb["source_check"], "issuer_page")
        self.assertIn("PERB Regulation 32635(a)", perb["authority_cited"])
        self.assertTrue(perb["url"].startswith("https://perb.ca.gov/"))

    def test_disclaimer_and_no_ai_label_for_mv2(self):
        text = json.dumps(self.doc).lower()
        self.assertIn("not legal advice", text)
        for bad in ("mv2 is an ai", "mv2, an ai", "mv2 (an ai"):
            self.assertNotIn(bad, text)


if __name__ == "__main__":
    unittest.main()
