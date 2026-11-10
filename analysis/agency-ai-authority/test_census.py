# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Tests for census.py on synthetic rows and texts only (no network, no real data)."""
import csv
import io
import unittest

import census

FILLER = " The tribunal considered the record in full." * 60  # > MIN_CHARS


def make_csv(rows):
    buf = io.StringIO()
    cols = ["case_id", "Case Name", "Court", "State(s)", "Date", "Party(ies)", "Source", "Pointer"]
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in cols})
    return buf.getvalue()


class ForumTest(unittest.TestCase):
    def test_agencies(self):
        cases = {
            "Trademark Trial and Appeal Board": "USPTO",
            "USPTO (PTAB)": "USPTO",
            "Board of Immigration Appeals": "EOIR",
            "Immigration Court (EOIR)": "EOIR",
            "Merit Systems Protection Board": "MSPB",
            "Board of Veterans' Appeals": "BVA",
            "NLRB": "NLRB",
            "Securities and Exchange Commission": "SEC",
            "Department of Labor, Office of Administrative Law Judges": "DOL",
            "Copyright Claims Board": "OTHER_FED",
        }
        for court, forum in cases.items():
            f, s, why = census.forum_of(court)
            self.assertEqual((f, s, why), (forum, "agency", "matched"), court)

    def test_article_i(self):
        for court, forum in (("United States Tax Court", "TAXCT"), ("U.S. Tax Court", "TAXCT"),
                             ("Tax Court", "TAXCT"),
                             ("U.S. Court of Appeals for Veterans Claims", "CAVC")):
            self.assertEqual(census.forum_of(court)[:2], (forum, "article_i"), court)

    def test_exclusions(self):
        self.assertEqual(census.forum_of("Oregon Tax Court")[2], "other")
        self.assertEqual(census.forum_of("Tax Court (New Jersey)")[2], "state tax court")
        self.assertEqual(census.forum_of("GAO")[2], "procurement (other study)")
        self.assertEqual(census.forum_of("ASBCA")[2], "procurement (other study)")
        self.assertEqual(census.forum_of("Fifth Circuit CA (on petition from BIA)")[2], "review court")
        self.assertEqual(census.forum_of("S.D.N.Y. (appeal from TTAB)")[2], "review court")
        self.assertEqual(census.forum_of("Court of Federal Claims")[2], "other")
        self.assertEqual(census.forum_of("D. Mass. (review of MSPB)")[2], "review court")
        self.assertEqual(census.forum_of("California Department of Labor")[2], "state agency")
        self.assertEqual(census.forum_of("Workers' Compensation Appeals Board")[2], "near miss")
        self.assertEqual(census.forum_of("N.D. Cal.")[2], "other")

    def test_select_rows(self):
        text = make_csv([
            {"case_id": "1", "Court": "TTAB", "State(s)": "USA", "Date": "2025-03-01",
             "Party(ies)": "Lawyer", "Source": "/documents/a b.pdf"},
            {"case_id": "2", "Court": "TTAB", "State(s)": "Canada", "Date": "2025-03-01"},
            {"case_id": "3", "Court": "United States Tax Court", "State(s)": "USA", "Date": "2026-12-01"},
            {"case_id": "4", "Court": "MSPB", "State(s)": "USA", "Date": "n/a",
             "Party(ies)": "Pro Se Litigant", "Pointer": "https://example.org/d.pdf"},
            {"case_id": "5", "Court": "D. Mass.", "State(s)": "USA", "Date": "2025-01-01"},
            {"case_id": "6", "Court": "GAO", "State(s)": "USA", "Date": "2025-01-01"},
        ])
        rows, table = census.select_rows(text)
        self.assertEqual([r["case_id"] for r in rows], ["4", "1"])
        by_id = {r["case_id"]: r for r in rows}
        self.assertEqual(by_id["1"]["url"], census.SITE + "/documents/a%20b.pdf")
        self.assertEqual(by_id["1"]["party"], "lawyer")
        self.assertIsNone(by_id["4"]["date"])
        self.assertEqual(by_id["4"]["party"], "pro_se")
        self.assertEqual(by_id["4"]["url"], "https://example.org/d.pdf")
        classified = {t["court"]: t["classified"] for t in table}
        self.assertEqual(classified["GAO"], "procurement (other study)")
        self.assertNotIn("D. Mass.", classified)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            census.select_rows("case_id,Court\n1,TTAB\n")


class TextTest(unittest.TestCase):
    def test_unreadable(self):
        out = census.classify_text("USPTO", "37 C.F.R. § 11.18")
        self.assertFalse(out["readable"])
        self.assertFalse(out["forum_rule"])

    def test_uspto(self):
        t = FILLER + (" Under 37 C.F.R. § 11.18(b) the signer certifies. See Guidance on Use of "
                      "Artificial Intelligence-Based Tools in Practice Before the USPTO, 89 FR 25609. "
                      "Cf. Mata v. Avianca, Inc. and Fed. R. Civ. P. 11.")
        out = census.classify_text("USPTO", t)
        self.assertTrue(out["readable"])
        for k in ("forum_rule", "uspto_11_18", "uspto_ai_guidance_2024", "ai_instrument", "mata",
                  "frcp_11", "ai_words"):
            self.assertTrue(out[k], k)
        self.assertFalse(out["eoir_pm_25_40"])
        self.assertIn("forum_rule", out["excerpts"])

    def test_rule_11_18_is_not_frcp_11(self):
        out = census.classify_text("USPTO", FILLER + " Rule 11.18 applies here.")
        self.assertTrue(out["forum_rule"])
        self.assertFalse(out["frcp_11"])

    def test_eoir(self):
        t = FILLER + (" See 8 C.F.R. § 1003.102 and EOIR Policy Memorandum 25-40. The court has "
                      "inherent authority.")
        out = census.classify_text("EOIR", t)
        self.assertTrue(out["forum_rule"])
        self.assertTrue(out["eoir_pm_25_40"])
        self.assertTrue(out["inherent"])
        self.assertFalse(out["uspto_11_18"])

    def test_tax(self):
        out = census.classify_text("TAXCT", FILLER + " A penalty under section 6673 may apply; see Rule 33(b).")
        self.assertTrue(out["forum_rule"])
        self.assertTrue(out["tax_6673"])
        out = census.classify_text("TAXCT", FILLER + " Fed. R. Evid. Rule 201(b) notice; Rule 201(a) binds counsel.")
        self.assertTrue(out["forum_rule"])
        self.assertFalse(out["tax_6673"])
        out = census.classify_text("TAXCT", FILLER + " Judicial notice under Rule 201(b).")
        self.assertFalse(out["forum_rule"])

    def test_forum_rule_is_forum_specific(self):
        out = census.classify_text("MSPB", FILLER + " 37 C.F.R. § 11.18 and 5 C.F.R. 1201.43.")
        self.assertTrue(out["forum_rule"])
        out = census.classify_text("NLRB", FILLER + " 37 C.F.R. § 11.18.")
        self.assertFalse(out["forum_rule"])
        out = census.classify_text("OTHER_FED", FILLER + " 37 C.F.R. § 11.18.")
        self.assertFalse(out["forum_rule"])

    def test_model_rules_and_1001(self):
        out = census.classify_text("SEC", FILLER + " ABA Model Rules of Professional Conduct; 18 U.S.C. § 1001.")
        self.assertTrue(out["model_rules"])
        self.assertTrue(out["usc_1001"])


def rec(case_id, forum, stratum, date, **flags):
    r = {"case_id": case_id, "forum": forum, "stratum": stratum, "date": date, "party": "lawyer",
         "court": forum, "doc_status": "ok", "readable": True}
    for k in census.FLAG_KEYS:
        r[k] = bool(flags.get(k))
    return r


class GradeTest(unittest.TestCase):
    def test_not_testable_when_empty(self):
        res = census.grade([])
        for k in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q8"):
            self.assertEqual(res["predictions"][k]["verdict"], "not testable", k)
        self.assertEqual(res["predictions"]["Q7"]["verdict"], "held")

    def test_grading(self):
        rows = []
        for i in range(6):  # USPTO from 2025: all cite 11.18, one cites the guidance
            rows.append(rec("u%d" % i, "USPTO", "agency", "2025-06-0%d" % (i + 1), forum_rule=True,
                            uspto_11_18=True, uspto_ai_guidance_2024=(i == 0), ai_instrument=(i == 0),
                            mata=(i < 2)))
        for i in range(6):  # EOIR: none cite a regulation, two cite FRCP 11
            rows.append(rec("e%d" % i, "EOIR", "agency", "2026-01-0%d" % (i + 1), frcp_11=(i < 2)))
        for i in range(5):  # Tax Court: one cites 6673
            rows.append(rec("t%d" % i, "TAXCT", "article_i", "2026-02-0%d" % (i + 1), tax_6673=(i == 0),
                            forum_rule=(i == 0)))
        rows.append(rec("x", "MSPB", "agency", "2023-01-01", ai_instrument=True))
        rows.append(dict(rec("y", "MSPB", "agency", "2025-01-01", forum_rule=True), doc_status="http_404"))
        res = census.grade(rows)
        p = {k: v["verdict"] for k, v in res["predictions"].items()}
        self.assertEqual(res["counts"]["readable"], 18)
        # agency readable: 6 USPTO + 6 EOIR + 1 MSPB = 13; AI instrument 2/13 < 25%
        self.assertEqual(p["Q1"], "held")
        # forum rule 6/13 = 0.46 >= 0.40
        self.assertEqual(p["Q2"], "held")
        self.assertEqual(p["Q3"], "held")   # 6 > 2
        self.assertEqual(p["Q4"], "held")   # 6/6
        self.assertEqual(p["Q5"], "held")   # 1/6 < 50%
        self.assertEqual(p["Q6"], "held")   # 1/5 < 50%
        self.assertEqual(p["Q7"], "held")   # one early match allowed
        self.assertEqual(p["Q8"], "failed")  # 2/18 < 15%
        self.assertEqual(res["no_listed_authority"]["n"], 4 + 4)  # EOIR e2-e5, TAXCT t1-t4
        md = census.results_md(res, {"sha256": "abc", "fetched_at": "now"})
        self.assertIn("| Q1 |", md)
        self.assertIn("| USPTO | 6 |", md)
        out = census.rows_csv(rows)
        self.assertTrue(out.startswith(",".join(census.PUBLIC_COLUMNS)))
        self.assertNotIn("case_name", out.splitlines()[0])

    def test_q7_fails_on_two_early_matches(self):
        rows = [rec("a", "MSPB", "agency", "2023-01-01", ai_instrument=True),
                rec("b", "MSPB", "agency", "2024-04-10", ai_instrument=True)]
        self.assertEqual(census.grade(rows)["predictions"]["Q7"]["verdict"], "failed")


if __name__ == "__main__":
    unittest.main()
