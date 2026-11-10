# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Offline tests for census.py (U.S. Tax Court fabricated-citation census 1.0.0)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

# Shapes copied from real DAWSON responses fetched on 2026-11-10 (long strings shortened).
# Opinion search: opinion-search?keyword="large language model"&dateRange=allDates&opinionTypes=MOP,OST,SOP,TCOP
OPINION_RESPONSE = json.dumps({"results": [{
    "entityName": "PublicDocumentSearchResult",
    "caseCaption": "Peter L. Clinco, Deceased, C. M. Barone-Clinco, Successor In Interest, and C. M.",
    "docketEntryId": "723ad324-f176-4a2b-a6a8-27e7a75cdfaa",
    "docketNumber": "8077-23",
    "docketNumberWithSuffix": "8077-23",
    "documentTitle": "Memorandum Opinion Judge Holmes Opinion - T.C. Memo. 2026-16  (Decision will be",
    "documentType": "Memorandum Opinion",
    "eventCode": "MOP",
    "filingDate": "2026-02-09T19:34:51.221Z",
    "isStricken": False,
    "judge": "Holmes",
    "numberOfPages": 11}]})
# Order search: order-search?keyword=ChatGPT&dateRange=allDates (orders also carry signedJudgeName)
ORDER_RESPONSE = json.dumps({"results": [{
    "entityName": "PublicDocumentSearchResult",
    "caseCaption": "Elias M. Seda, Petitioner",
    "docketEntryId": "e87a6f9d-54aa-42d6-9477-25440d55797e",
    "docketNumber": "6165-24",
    "docketNumberWithSuffix": "6165-24",
    "documentTitle": "Order of Dismissal and Decision Entered, Judge Copeland Petr's motion for contin...",
    "documentType": "Order of Dismissal and Decision",
    "eventCode": "ODD",
    "filingDate": "2025-12-31T13:22:14.813Z",
    "isStricken": False,
    "judge": "Copeland",
    "numberOfPages": 3,
    "signedJudgeName": "Elizabeth A. Copeland"}, {
    "entityName": "PublicDocumentSearchResult",
    "caseCaption": "Perimeter Protective Systems, Inc., Petitioner",
    "docketEntryId": "089903f6-a12f-496e-bbe5-941d732722c8",
    "docketNumber": "255-18",
    "docketNumberWithSuffix": "255-18SL",
    "documentTitle": "ORDER AND DECISION ENTERED,  JUDGE COPELAND.",
    "documentType": "Order and Decision",
    "eventCode": "OAD",
    "filingDate": "2020-07-14T04:00:00.000Z",
    "isStricken": False,
    "numberOfPages": 10,
    "signedJudgeName": "Elizabeth A. Copeland"}]})

AI_ORDER = ("ORDER. Petitioner's pretrial memorandum cites several cases that do not exist. " + "x " * 50 +
            "Petitioner admits that the memorandum was prepared with the help of generative artificial "
            "intelligence (AI). The Court reminds petitioner that under Rule 33(b) a signature certifies "
            "that the paper is warranted by existing law. We will not impose sanctions at this time.")
PLAIN_FAKE = ("The brief relies on fictitious citations; the cases petitioner cited do not exist. "
              "We warn petitioner that the Court may impose a penalty of $25,000 under section 6673.")
TAX_NOISE = ("The partnership was a fictitious entity and the transaction was a sham in this case. "
             "Petitioner fabricated invoices in this case. We find the cases cited by respondent persuasive. "
             "A notice of deficiency does not exist for 2019. Mailing address: Birmingham (AL).")


class TestSearch(unittest.TestCase):
    def test_urls(self):
        u = census.search_url("order", '"artificial intelligence"')
        self.assertEqual(u, census.API + "/order-search?keyword=%22artificial%20intelligence%22&dateRange=allDates")
        u = census.search_url("opinion", "nonexistent cases")
        self.assertTrue(u.endswith("keyword=nonexistent%20cases&dateRange=allDates&opinionTypes=MOP,OST,SOP,TCOP"))
        self.assertNotIn("+", u)
        self.assertEqual(census.download_url("10795-22", "abc"),
                         census.API + "/10795-22/abc/public-document-download-url")

    def test_parse_real_shapes(self):
        op = census.parse_results(OPINION_RESPONSE.encode())
        self.assertEqual(len(op), 1)
        self.assertEqual(op[0]["date"], "2026-02-09")
        self.assertEqual(op[0]["judge"], "Holmes")
        self.assertEqual(op[0]["event_code"], "MOP")
        orders = census.parse_results(ORDER_RESPONSE)
        self.assertEqual([o["docket_number"] for o in orders], ["6165-24", "255-18"])
        self.assertEqual(orders[0]["judge"], "Elizabeth A. Copeland")
        self.assertEqual(orders[1]["docket_suffixed"], "255-18SL")
        self.assertEqual(census.parse_results(b'{"results":[]}'), [])

    def test_merge_window_and_dedupe(self):
        frame = {}
        orders = census.parse_results(ORDER_RESPONSE)
        self.assertEqual(census.merge(frame, "order", "ChatGPT", orders), 1)  # 2020 order is out of window
        self.assertEqual(census.merge(frame, "order", "generative", orders), 1)
        consolidated = dict(orders[0], docket_number="6166-24")
        census.merge(frame, "order", "ChatGPT", [consolidated])
        census.merge(frame, "opinion", '"artificial intelligence"', census.parse_results(OPINION_RESPONSE))
        self.assertEqual(len(frame), 2)
        d = frame["e87a6f9d-54aa-42d6-9477-25440d55797e"]
        self.assertEqual(d["dockets"], ["6165-24", "6166-24"])
        self.assertEqual(d["queries"], ["order:ChatGPT", "order:generative"])
        self.assertEqual(d["kind"], "order")
        self.assertEqual(frame["723ad324-f176-4a2b-a6a8-27e7a75cdfaa"]["kind"], "opinion")

    def test_window(self):
        self.assertTrue(census.in_window("2023-01-01"))
        self.assertTrue(census.in_window("2026-11-10"))
        self.assertFalse(census.in_window("2022-12-31"))
        self.assertFalse(census.in_window(None))


class TestClassify(unittest.TestCase):
    def test_ai_order(self):
        r = census.classify(AI_ORDER)
        self.assertTrue(r["fake_cite"])
        self.assertTrue(r["ai_mention"])
        self.assertTrue(r["ai_citation"])
        self.assertTrue(r["ai_phrase"])
        self.assertTrue(r["rule_33"])
        self.assertFalse(r["sec_6673"])
        self.assertTrue(r["action"])
        self.assertIn("ai_citation", r["excerpts"])

    def test_plain_fake(self):
        r = census.classify(PLAIN_FAKE)
        self.assertTrue(r["fake_cite"])
        self.assertFalse(r["ai_mention"])
        self.assertFalse(r["ai_citation"])
        self.assertTrue(r["sec_6673"])
        self.assertTrue(r["action"])
        self.assertFalse(r["rule_33"])

    def test_tax_noise_is_not_a_fake_citation(self):
        r = census.classify(TAX_NOISE)
        self.assertFalse(r["fake_cite"])
        self.assertFalse(r["ai_mention"])
        self.assertFalse(r["rule_33"])  # only computed for fake_cite documents

    def test_pdf_line_breaks(self):
        r = census.classify("The memorandum cites non-\nexistent\ncases and was drafted with Chat GPT.")
        self.assertTrue(r["fake_cite"])
        r = census.classify("we were unable to locate the cases cited in the brief, generated by ChatGPT")
        self.assertTrue(r["fake_cite"])
        self.assertTrue(r["ai_citation"])
        r = census.classify("hallucinated   case law\nfrom an Al tool")
        self.assertTrue(r["fake_cite"])
        self.assertTrue(r["ai_mention"])


class TestCoverage(unittest.TestCase):
    CSV = ("case_id,Case Name,Court,State(s),Date\n"
           "2668,Moore v. Commissioner of Internal Revenue,Tax Court,USA,2026-09-15\n"
           "1209,Peter L. Clinco v. Commissioner,US Tax Court,USA,2026-02-09\n"
           "2925,2028604 Ontario Ltd. v. His Majesty the King,Tax Court of Canada,Canada,2026-10-28\n"
           "1002,Donovan v. Clark County Assessor,Indiana Tax Court,USA,2025-12-22\n"
           "1703,Riddle Aggregates v. Commissioner of Internal Revenue,Tax Court,USA,2026-03-18\n"
           "1,Old v. Commissioner,US Tax Court,USA,2022-05-01\n")

    def test_db_rows(self):
        db = census.db_rows(self.CSV)
        self.assertEqual([x["case_id"] for x in db], ["2668", "1209", "1703", "1"])
        self.assertEqual(db[1]["tokens"], ["peter", "clinco"])
        self.assertEqual(db[2]["tokens"], ["riddle", "aggregates"])

    def test_match(self):
        db = census.db_rows(self.CSV)
        docs = [{"docket_entry_id": "a", "date": "2026-02-09", "caption": "Peter L. Clinco, Deceased", "fake_cite": True},
                {"docket_entry_id": "b", "date": "2026-09-16", "caption": "Justin Joseph Moore, Petitioner"},
                {"docket_entry_id": "c", "date": "2026-09-15", "caption": "Moorehead, Petitioner"},
                {"docket_entry_id": "d", "date": None, "caption": "Riddle Aggregates, LLC"}]
        win = census.match_db(docs, db)
        self.assertEqual([x["case_id"] for x in win], ["2668", "1209", "1703"])
        self.assertEqual(win[0]["matched"], ["b"])
        self.assertEqual(win[1]["matched_fake_cite"], ["a"])
        self.assertEqual(win[2]["matched"], [])
        self.assertEqual([d["in_db"] for d in docs], [True, True, False, False])
        self.assertEqual(docs[0]["db_case_id"], "1209")


class TestGrade(unittest.TestCase):
    def docs(self):
        base = {"readable": True, "queries": ["order:nonexistent"]}
        return [
            dict(base, docket_entry_id="1", docket_number="1-24", dockets=["1-24"], date="2026-01-05", kind="order",
                 fake_cite=True, in_db=True, ai_mention=True, ai_citation=True, ai_phrase=True, rule_33=True,
                 queries=['order:"artificial intelligence"']),
            dict(base, docket_entry_id="2", docket_number="2-24", dockets=["2-24"], date="2025-03-01", kind="order",
                 fake_cite=True, rule_33=True),
            dict(base, docket_entry_id="3", docket_number="3-24", dockets=["3-24"], date="2024-07-01", kind="opinion",
                 fake_cite=True, sec_6673=True, ai_phrase=True),
            dict(base, docket_entry_id="4", docket_number="4-24", dockets=["4-24"], date="2024-01-01", kind="opinion"),
            dict(base, docket_entry_id="5", docket_number="5-24", dockets=["5-24"], date="2023-01-01", kind="order",
                 readable=False, fake_cite=True),
        ]

    def test_verdicts(self):
        db_win = [{"case_id": "9", "date": "2026-01-05", "matched": ["1"], "matched_fake_cite": ["1"]},
                  {"case_id": "8", "date": "2025-05-20", "matched": [], "matched_fake_cite": []}]
        res = census.grade(self.docs(), db_win, [{"kind": "order", "query": "x", "results": 3, "in_window": 2}])
        v = {k: p["verdict"] for k, p in res["predictions"].items()}
        self.assertEqual(v, {"P1": "failed", "P2": "held", "P3": "held", "P4": "held", "P5": "held",
                             "P6": "held", "P7": "failed", "P8": "not testable"})
        self.assertEqual(res["predictions"]["P7"]["detail"]["missed_case_ids"], ["8"])
        self.assertEqual(res["counts"]["in_frame"], 5)
        self.assertEqual(res["counts"]["readable"], 4)
        self.assertEqual(res["counts"]["fake_cite"], 3)
        self.assertEqual(res["counts"]["fake_cite_orders"], 2)
        self.assertEqual(res["counts"]["by_year"]["2024"], {"readable": 2, "fake_cite": 1, "ai_citation": 0})
        self.assertEqual(res["predictions"]["P8"]["detail"], {"n": 2, "k": 1, "share": 0.5})

    def test_without_database(self):
        res = census.grade(self.docs(), None)
        self.assertEqual(res["predictions"]["P2"]["verdict"], "not testable")
        self.assertEqual(res["predictions"]["P7"]["verdict"], "not testable")

    def test_outputs_never_carry_captions(self):
        docs = self.docs()
        docs[0]["caption"] = "Secret Name, Petitioner"
        res = census.grade(docs, [], [{"kind": "order", "query": "ChatGPT", "results": 1, "in_window": 1}])
        md = census.results_md(res, {"x": 1})
        self.assertIn("| P1 |", md)
        self.assertIn("](https://dawson.ustaxcourt.gov/case-detail/1-24)", md)
        self.assertIn("| order `ChatGPT` | 1 | 1 |", md)
        out = census.rows_csv(docs)
        self.assertTrue(out.startswith("docket_entry_id,dockets,date,kind"))
        self.assertNotIn("Secret", out)
        self.assertNotIn("Secret", json.dumps(res))
        self.assertEqual(out.splitlines()[1].split(",")[0], "5")  # sorted by date


if __name__ == "__main__":
    unittest.main()
