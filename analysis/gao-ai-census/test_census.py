# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for census.py (synthetic pages shaped like GAO's decision pages)."""
import unittest

import census

PAGE_AI = """<html><body><nav><a class="link--ai-reports">Artificial Intelligence (AI)-Related Reports</a></nav>
<div class="field__item"><p><strong>Decision</strong></p>
<p class="matterOf"><strong>Matter of: </strong>Acme Widgets, LLC</p>
<p class="file"><strong>File: </strong>B-424999</p>
<p class="date:"><strong>Date:</strong> October 27, 2026</p>
<p style="border-top:1pt">Jane Roe, for the protester.<br>
John Doe, Esq., Department of the Army, for the agency.</p>
<p><strong>DIGEST</strong></p>
<p>Protest is dismissed.</p>
<p><strong>DECISION</strong></p>
<p>The protester cited decisions that do not exist. These bear the hallmarks of artificial intelligence (AI).</p>
<p>The protest is dismissed.</p>
<p>Edda Emmanuelli Perez<br>
General Counsel</p></div>
<footer>Artificial Intelligence and fabricated menus</footer></body></html>"""

PAGE_PLAIN = PAGE_AI.replace(
    "The protester cited decisions that do not exist. These bear the hallmarks of artificial intelligence (AI).",
    "The agency reasonably evaluated the quotation.").replace(
    "Jane Roe, for the protester.", "Neil Smith, Esq., Smith Law, for the protester.").replace(
    "The protest is dismissed.", "The protest is sustained.")

RSS = """<rss version="2.0"><channel><title>GAO</title>
<item><title>A</title><link>https://www.gao.gov/products/b-338834</link>
<pubDate>Fri, 06 Nov 2026 13:18:41 -0500</pubDate></item>
<item><title>B</title><link>https://www.gao.gov/products/b-424641%2Cb-424641.2</link>
<pubDate>Tue, 03 Nov 2026 08:57:04 -0500</pubDate></item>
<item><title>C</title><link>https://www.gao.gov/products/b-424672</link>
<pubDate>Fri, 06 Nov 2026 09:05:31 -0500</pubDate></item>
</channel></rss>"""


class TestParse(unittest.TestCase):
    def test_ai_citation_body_only(self):
        d = census.parse_decision(PAGE_AI)
        self.assertTrue(d["parsed"])
        self.assertEqual(d["protester"], "Acme Widgets, LLC")
        self.assertEqual(d["decision_date"], "2026-10-27")
        self.assertEqual(d["protester_counsel"], "no_lawyer")
        self.assertEqual(d["category"], "ai_citation")
        self.assertIn("artificial intelligence", d["ai_terms"])
        self.assertIn("do not exist", d["cite_terms"])
        self.assertFalse(d["sustained"])

    def test_menus_do_not_count(self):
        d = census.parse_decision(PAGE_PLAIN)
        self.assertEqual(d["category"], "none")
        self.assertEqual(d["protester_counsel"], "lawyer")
        self.assertTrue(d["sustained"])

    def test_no_matter_of_is_unparsed(self):
        self.assertEqual(census.parse_decision("<html><p>Artificial intelligence</p></html>"), {"parsed": False})

    def test_word_boundary(self):
        page = PAGE_PLAIN.replace("The agency reasonably evaluated the quotation.",
                                  "The Dubai program office said the record does not exist.")
        d = census.parse_decision(page)
        self.assertEqual(d["category"], "cite_only")

    def test_withheld_individual(self):
        self.assertEqual(census.protester_public("Davos Francois"), "")
        self.assertEqual(census.protester_public("Bramstedt Surgical Inc."), "Bramstedt Surgical Inc.")
        d = census.parse_decision(PAGE_AI.replace("Acme Widgets, LLC", "Jane Roe"))
        self.assertEqual(d["protester"], "")
        self.assertEqual(d["protester_full"], "Jane Roe")


class TestFeed(unittest.TestCase):
    def test_rss_and_b_numbers(self):
        items = census.parse_rss(RSS.encode("utf-8"))
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["pubdate"], "2026-11-06T18:18:41Z")
        self.assertEqual(census.b_numbers_from_link(items[1]["link"]), ["B-424641", "B-424641.2"])
        self.assertFalse(census.is_protest("B-338834"))
        self.assertTrue(census.is_protest("B-424641.2"))

    def test_plan_wave(self):
        items = census.parse_rss(RSS)
        fetch, skipped = census.plan_wave(items, {"B-424672"})
        self.assertEqual([f["b_number"] for f in fetch], ["B-424641"])
        self.assertEqual(fetch[0]["b_numbers"], "B-424641;B-424641.2")
        self.assertEqual(skipped["not_protest"], 1)
        self.assertEqual(skipped["already_in_ledger"], 1)
        fetch, skipped = census.plan_wave(items, set(), max_pages=1)
        self.assertEqual(len(fetch), 1)
        self.assertEqual(skipped["over_cap"], 1)

    def test_gap(self):
        self.assertFalse(census.gap_possible(["2026-11-01T00:00:00Z"], []))
        self.assertFalse(census.gap_possible(["2026-11-01T00:00:00Z", "2026-11-09T00:00:00Z"],
                                             ["2026-11-02T00:00:00Z"]))
        self.assertTrue(census.gap_possible(["2026-11-05T00:00:00Z"], ["2026-11-02T00:00:00Z"]))

    def test_ledger_round_trip(self):
        rows = [{"b_number": "B-424999", "rss_pubdate": "2026-11-06T18:18:41Z", "category": "ai_citation"},
                {"b_number": "B-424001", "rss_pubdate": "2026-11-01T10:00:00Z", "category": "none"}]
        back = census.load_ledger(census.ledger_csv(rows))
        self.assertEqual([r["b_number"] for r in back], ["B-424999", "B-424001"])
        self.assertEqual(list(back[0].keys()), census.FIELDS)
        self.assertEqual(census.load_ledger(""), [])


class TestDbMatch(unittest.TestCase):
    def test_match_rules(self):
        dec = {"b_number": "B-423066.2", "protester": "LOGMET LLC", "decision_date": "2026-04-15"}
        by_number = [{"Court": "GAO", "Case Name": "Matter of: LOGMET LLC, B-423066.2", "Date": "2026-04-15"}]
        self.assertTrue(census.db_match(dec, by_number))
        by_name = [{"Court": "GAO", "Case Name": "Logmet, LLC", "Date": "2026-04-17", "Source": "", "Details": ""}]
        self.assertTrue(census.db_match(dec, by_name))
        too_far = [{"Court": "GAO", "Case Name": "Logmet, LLC", "Date": "2026-04-30"}]
        self.assertFalse(census.db_match(dec, too_far))
        other_court = [{"Court": "ASBCA", "Case Name": "Matter of: LOGMET LLC, B-423066.2", "Date": "2026-04-15"}]
        self.assertFalse(census.db_match(dec, other_court))


if __name__ == "__main__":
    unittest.main()
