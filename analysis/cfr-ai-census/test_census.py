# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Tests for census.py (standard library only, no network)."""
import csv
import io
import unittest

import census


def hit(title, part, section=None, appendix=None, subpart=None, starts="2025-01-15", ends=None,
        chapter="Agency", part_heading="Some Part", sub_heading=None, heading="Heading",
        excerpt="uses <strong>artificial intelligence</strong> here"):
    return {
        "starts_on": starts, "ends_on": ends, "type": "Section" if section else "Appendix",
        "hierarchy": {"title": title, "part": part, "section": section, "appendix": appendix,
                      "subpart": subpart},
        "headings": {"chapter": chapter, "part": part_heading, "subpart": sub_heading,
                     "subchapter": None, "section": heading if section else None,
                     "appendix": None if section else heading},
        "full_text_excerpt": excerpt,
    }


EXPORT = hit("15", "740", section="740.27", starts="2025-01-16", chapter="Bureau of Industry and Security")
EXPORT_OLD = hit("15", "740", section="740.27", starts="2025-01-15", ends="2025-01-15")
CCL = hit("15", "774", appendix="Supplement No. 1 to Part 774", starts="2026-08-18")
DEVICE = hit("21", "870", section="870.2380", starts="2026-09-11", heading="Cardiovascular <strong>machine learning</strong>-based notification software.")
ENV = hit("40", "73", appendix="Appendix A to Subpart F", subpart="F", starts="2016-12-27")
PRACTICE = hit("37", "42", section="42.11", starts="2026-10-01", part_heading="Trial Practice Before the Patent Trial and Appeal Board")


class KeyTest(unittest.TestCase):
    def test_section_key(self):
        self.assertEqual(census.provision_key(EXPORT), "15 CFR 740.27")
        self.assertEqual(census.provision_key(EXPORT_OLD), "15 CFR 740.27")

    def test_appendix_keys(self):
        self.assertEqual(census.provision_key(CCL), "15 CFR Part 774, Supplement No. 1 to Part 774")
        self.assertEqual(census.provision_key(ENV), "40 CFR Part 73 Subpart F, Appendix A to Subpart F")

    def test_clean(self):
        self.assertEqual(census.clean(" a <strong>b</strong>&amp; c \n d"), "a b& c d")
        self.assertEqual(census.clean(None), "")


class CategoryTest(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(census.category(EXPORT), "export controls (BIS)")
        self.assertEqual(census.category(CCL), "export controls (BIS)")
        self.assertEqual(census.category(DEVICE), "medical devices (FDA)")
        self.assertEqual(census.category(hit("15", "791", section="791.3")), "ICT supply chain (Commerce)")
        self.assertEqual(census.category(hit("31", "850", section="850.210")), "outbound investment (Treasury)")
        self.assertEqual(census.category(hit("28", "202", section="202.214")), "bulk sensitive data (DOJ)")
        self.assertEqual(census.category(hit("42", "410", section="410.79")), "Medicare and Medicaid (CMS)")
        self.assertEqual(census.category(ENV), "other")

    def test_rules_of_practice(self):
        self.assertTrue(census.rules_of_practice(PRACTICE))
        self.assertTrue(census.rules_of_practice(hit("29", "2200", section="2200.1", part_heading="Rules of Procedure")))
        self.assertFalse(census.rules_of_practice(hit("21", "211", section="211.22", part_heading="Current Good Manufacturing Practice for Finished Pharmaceuticals")))
        self.assertFalse(census.rules_of_practice(EXPORT))


class InForceTest(unittest.TestCase):
    def test_inclusive_bounds(self):
        self.assertTrue(census.in_force_on(EXPORT_OLD, "2025-01-15"))
        self.assertFalse(census.in_force_on(EXPORT_OLD, "2025-01-16"))
        self.assertFalse(census.in_force_on(EXPORT, "2025-01-01"))
        self.assertTrue(census.in_force_on(EXPORT, census.CENSUS_DATE))


class BuildTest(unittest.TestCase):
    def setUp(self):
        ai, ml = "artificial intelligence", "machine learning"
        undated = {ai: [EXPORT, EXPORT_OLD, CCL, ENV, PRACTICE], ml: [DEVICE]}
        dated = {
            (ai, "2017-01-01"): [ENV],
            (ai, "2026-01-01"): [EXPORT, ENV, CCL],          # CCL here is an anomaly (starts 2026-08-18)
            (ai, census.CENSUS_DATE): [EXPORT, CCL, ENV, PRACTICE],
            (ml, census.CENSUS_DATE): [DEVICE],
        }
        self.prov, self.timeline, self.anomalies = census.build(dated, undated)

    def test_provisions(self):
        self.assertEqual(len(self.prov), 5)
        p = self.prov["15 CFR 740.27"]
        self.assertEqual(p["first_starts_on"], "2025-01-15")
        self.assertEqual(p["terms"], {"artificial intelligence"})
        self.assertEqual(p["agency"], "Bureau of Industry and Security")
        self.assertEqual(self.prov["21 CFR 870.2380"]["heading"],
                         "Cardiovascular machine learning-based notification software.")

    def test_anomaly_excluded(self):
        self.assertEqual(len(self.anomalies), 1)
        self.assertEqual(self.anomalies[0]["provision"], "15 CFR Part 774, Supplement No. 1 to Part 774")
        row = {r["date"]: r for r in self.timeline}
        self.assertEqual(row["2026-01-01"]["any_term"], 2)
        self.assertEqual(row["2026-01-01"]["artificial intelligence"], 2)
        self.assertEqual(row["2017-01-01"]["any_term"], 1)
        self.assertEqual(row["2018-01-01"]["any_term"], 0)
        self.assertEqual(row[census.CENSUS_DATE]["any_term"], 5)
        self.assertEqual(row[census.CENSUS_DATE]["machine learning"], 1)
        self.assertEqual(len(self.timeline), len(census.DATES))

    def test_summary(self):
        s = census.summarize(self.prov, self.timeline, self.anomalies)
        self.assertEqual(s["provisions_in_force_on_census_date"], 5)
        self.assertEqual(s["provisions_ever"], 5)
        self.assertEqual(s["in_force_first_effective_2025_or_later"], 4)
        self.assertEqual(s["by_category"]["export controls (BIS)"], 2)
        self.assertEqual(list(s["by_category"])[0], "export controls (BIS)")
        self.assertEqual(s["rules_of_practice_in_force"], ["37 CFR 42.11"])
        self.assertIn("large language model", s["terms_never_matched"])
        self.assertNotIn("machine learning", s["terms_never_matched"])
        self.assertEqual(s["date_filter_anomalies"], 1)

    def test_rows_and_csv(self):
        rows = census.rows(self.prov)
        self.assertEqual(rows[0]["provision"], "40 CFR Part 73 Subpart F, Appendix A to Subpart F")
        self.assertEqual([r["in_force_on_census_date"] for r in rows], ["yes"] * 5)
        text = census.to_csv(rows, census.ROW_FIELDS)
        back = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(back), 5)
        self.assertEqual(list(back[0].keys()), census.ROW_FIELDS)
        md = census.results_md(census.summarize(self.prov, self.timeline, self.anomalies), rows, True)
        self.assertIn("| %s | 5 |" % census.CENSUS_DATE, md)
        self.assertIn("15 CFR 740.27", md)


class ConfigTest(unittest.TestCase):
    def test_dates_sorted_and_end_at_census(self):
        self.assertEqual(census.DATES, sorted(census.DATES))
        self.assertEqual(census.DATES[-1], census.CENSUS_DATE)
        self.assertEqual(census.DATES[0], "2017-01-01")
        self.assertEqual(len(set(census.TERMS)), len(census.TERMS))


if __name__ == "__main__":
    unittest.main()
