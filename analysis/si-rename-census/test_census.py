# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the EO 14434 terminology census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest import mock

import census
import run_job

OTHER = [{"name": "Energy Department", "raw_name": "DEPARTMENT OF ENERGY", "parent_id": None}]
SEC = [{"name": "Securities and Exchange Commission", "parent_id": None}]
FCC = [{"name": "Federal Communications Commission", "parent_id": None}]
OCC = [{"name": "Treasury Department", "parent_id": None},
       {"name": "Comptroller of the Currency", "parent_id": 497}]


def mk(dn, date, window, cls, si=0, ai=0, ai_lower=0, eo=0, readable=True, agencies=None, typ="Rule"):
    counts = {k: 0 for k in census.COUNT_KEYS}
    counts.update({"si": si, "ai": ai, "ai_lower": ai_lower, "eo14434": eo})
    d = {"document_number": dn, "publication_date": date, "window": window, "agency_class": cls,
         "type": "Presidential Document" if cls == "presidential" else typ,
         "agencies": agencies if agencies is not None else OTHER, "readable": readable}
    d["top_agency"] = census.top_agency(d)
    if readable:
        d.update({"counts": counts, "category": census.category(counts), "chars": 1000})
    return d


def sample(with_w2=False):
    docs = [
        mk("d1", "2026-10-05", "W1", "other", si=2, ai=1, eo=1),
        mk("d2", "2026-10-06", "W1", "other", si=1),
        mk("d3", "2026-10-13", "W1", "other", si=1, ai=3),
        mk("d4", "2026-10-14", "W1", "other", ai=2, ai_lower=1),
        mk("d5", "2026-10-20", "W1", "listed_independent", ai=1, agencies=SEC),
        mk("d6", "2026-10-21", "W1", "listed_independent", ai=1, ai_lower=2, agencies=OCC),
        mk("d7", "2026-10-02", "W1", "presidential", si=1, ai=1, agencies=[]),
        mk("d8", "2026-10-22", "W1", "other", readable=False),
        mk("d9", "2026-09-01", "W0", "other", ai=1),
        mk("d10", "2026-09-30", "W0", "other", si=1),
    ]
    if with_w2:
        docs += [
            mk("d11", "2026-11-20", "W2", "other", si=1),
            mk("d12", "2026-11-23", "W2", "other", ai=1),
            mk("d13", "2026-11-24", "W2", "listed_independent", si=1, agencies=FCC),
        ]
    return docs


class TestParts(unittest.TestCase):
    def test_search_url(self):
        url = census.search_url('"super intelligence"', "2026-10-02", "2026-11-11", 2)
        self.assertTrue(url.startswith(census.API + "?"))
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        self.assertEqual(qs["conditions[term]"], ['"super intelligence"'])
        self.assertEqual(qs["conditions[publication_date][gte]"], ["2026-10-02"])
        self.assertEqual(qs["conditions[publication_date][lte]"], ["2026-11-11"])
        self.assertEqual(qs["page"], ["2"])
        self.assertEqual(qs["per_page"], ["100"])
        self.assertEqual(qs["fields[]"], census.FIELDS)

    def test_ecfr_url_and_total(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(census.ecfr_url('"super intelligence"')).query)
        self.assertEqual(qs["query"], ['"super intelligence"'])
        self.assertEqual(census.ecfr_total({"meta": {"total_count": 7}}), 7)
        self.assertEqual(census.ecfr_total({}), 0)

    def test_parse_page(self):
        self.assertEqual(census.parse_page({"count": 3, "total_pages": 1, "results": [{"a": 1}]}),
                         (3, 1, [{"a": 1}]))
        self.assertEqual(census.parse_page({"count": 0, "total_pages": 0}), (0, 0, []))

    def test_normalize(self):
        self.assertEqual(census.normalize("<html><pre>A &amp; B\n\n  C</pre></html>"), "A & B C")

    def test_classify(self):
        text = ("The Super Intelligence (SI) policy under Executive Order 14434 replaces artificial intelligence. "
                "The National Artificial Intelligence Initiative Act, 15 U.S.C. 9401, defines AI. "
                "Superintelligence is different.")
        r = census.classify(text)
        c = r["counts"]
        self.assertEqual((c["si"], c["superintelligence"], c["ai"], c["ai_lower"]), (1, 1, 2, 1))
        self.assertEqual((c["ai_acronym"], c["si_acronym"], c["eo14434"], c["usc9401"]), (1, 1, 1, 1))
        self.assertEqual(r["category"], "both")
        self.assertEqual(r["chars"], len(text))
        self.assertEqual(sorted(r["excerpts"]), ["ai", "eo14434", "si"])

    def test_classify_hyphen_and_case(self):
        c = census.classify("SUPER-INTELLIGENCE tools; Artificial  Intelligence")["counts"]
        self.assertEqual((c["si"], c["ai"], c["ai_lower"]), (1, 1, 0))
        self.assertEqual(census.classify("the Era of Super Intelligence")["counts"]["eo14434"], 1)

    def test_category(self):
        self.assertEqual(census.category({"si": 1, "ai": 0}), "si_only")
        self.assertEqual(census.category({"si": 0, "ai": 4}), "ai_only")
        self.assertEqual(census.category({"si": 2, "ai": 4}), "both")
        self.assertEqual(census.category({"si": 0, "ai": 0}), "neither")

    def test_agencies(self):
        self.assertEqual(census.agency_class({"type": "Presidential Document", "agencies": OTHER}), "presidential")
        occ = {"type": "Rule", "agencies": OCC}
        self.assertEqual(census.agency_class(occ), "listed_independent")
        self.assertEqual(census.top_agency(occ), "Treasury Department")
        self.assertEqual(census.listed_keys(census.agency_names(occ)), ["comptroller of the currency"])
        self.assertEqual(census.agency_class({"type": "Notice", "agencies": OTHER}), "other")
        self.assertEqual(census.listed_keys(["Securities and Exchange Commission"]),
                         ["securities and exchange commission"])
        self.assertEqual(census.agency_names({"agencies": [{"raw_name": "X BOARD"}, {"name": ""}]}), ["X BOARD"])
        self.assertEqual(census.top_agency({"agencies": []}), "")

    def test_dates(self):
        self.assertEqual(census.week_start("2026-10-02"), "2026-09-28")
        self.assertEqual(census.window_of("2026-10-01"), "W0")
        self.assertEqual(census.window_of("2026-10-02"), "W1")
        self.assertEqual(census.window_of("2026-12-11"), "W2")
        self.assertEqual(census.window_of("2026-12-12"), "")


class TestGrade(unittest.TestCase):
    def test_wave1(self):
        res = census.grade(sample(), {"x": 0}, "w01")
        p = res["predictions"]
        self.assertEqual((p["P1"]["verdict"], p["P1"]["value"]), ("held", "2 of 3"))
        self.assertEqual((p["P2"]["verdict"], p["P2"]["value"]), ("held", "1 of 2"))
        self.assertEqual((p["P3"]["verdict"], p["P3"]["value"]), ("failed", "1 of 3"))
        self.assertEqual((p["P4"]["verdict"], p["P4"]["value"]), ("held", "1"))
        self.assertEqual((p["P5"]["verdict"], p["P5"]["value"]), ("held", "median 1"))
        self.assertEqual((p["P6"]["verdict"], p["P6"]["value"]), ("held", "securities and exchange commission"))
        self.assertEqual((p["P7"]["verdict"], p["P7"]["value"]), ("failed", "9 of 10"))
        self.assertEqual(p["P8"]["verdict"], "pending wave w02")
        self.assertEqual(p["P9"]["verdict"], "pending wave w02")
        self.assertTrue(all(v.get("text") for v in p.values()))
        w1 = res["counts"]["W1"]
        self.assertEqual(w1["by_category"], {"both": 3, "si_only": 1, "ai_only": 3})
        self.assertEqual((w1["documents"], w1["readable"]), (8, 7))
        self.assertEqual(w1["si_share_nonpresidential"], 0.5)
        self.assertEqual(w1["si_share_other_agencies"], 0.75)
        self.assertEqual(w1["weekly_nonpresidential"]["2026-10-05"], {"matched": 2, "super_intelligence": 2})
        self.assertEqual(w1["agencies"]["Energy Department"], {"matched": 4, "super_intelligence": 3, "ai_only": 1})
        self.assertEqual(sorted(res["counts"]), ["W0", "W1"])
        md = census.results_md(res)
        self.assertIn("| P1 |", md)
        self.assertIn("### W1 (2026-10-02 to 2026-11-11)", md)

    def test_wave2(self):
        res = census.grade(sample(with_w2=True), {}, "w02")
        p = res["predictions"]
        self.assertEqual((p["P8"]["verdict"], p["P8"]["value"]), ("failed", "W2 1 of 2 vs W1 3 of 4"))
        self.assertEqual((p["P9"]["verdict"], p["P9"]["value"]), ("held", "federal communications commission"))
        self.assertEqual((p["P7"]["verdict"], p["P7"]["value"]), ("failed", "12 of 13"))
        self.assertEqual(sorted(res["counts"]), ["W0", "W1", "W2"])

    def test_empty(self):
        res = census.grade([], {}, "w01")
        p = res["predictions"]
        for k in ("P1", "P2", "P3", "P5", "P6"):
            self.assertEqual(p[k]["verdict"], "not testable")
        self.assertEqual(p["P4"]["verdict"], "held")
        self.assertEqual(p["P7"]["verdict"], "failed")

    def test_rows_csv(self):
        docs = sample()
        docs[0]["terms_matched"] = {"super intelligence", "artificial intelligence"}
        out = census.rows_csv(docs).splitlines()
        self.assertEqual(out[0], ",".join(census.ROW_FIELDS))
        self.assertEqual(len(out), len(docs) + 1)
        self.assertTrue(out[1].startswith("d9,2026-09-01,W0,Rule,Energy Department,"))
        self.assertTrue(any("artificial intelligence; super intelligence" in line for line in out))


def fake_fetch_factory(pages, fail=False):
    def fetch(url):
        if fail:
            raise OSError("down")
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        key = (qs["conditions[term]"][0], qs["conditions[publication_date][gte]"][0], qs["page"][0])
        return pages.get(key, {"count": 0, "total_pages": 0})
    return fetch


class TestJob(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_search_all(self):
        A = {"document_number": "A", "publication_date": "2026-10-05", "type": "Rule", "agencies": OTHER}
        B = {"document_number": "B", "publication_date": "2026-10-06", "type": "Notice", "agencies": SEC}
        C = {"document_number": "C", "publication_date": "2026-10-07", "type": "Presidential Document",
             "agencies": []}
        pages = {
            ('"artificial intelligence"', "2026-10-02", "1"): {"count": 3, "total_pages": 2, "results": [A, B]},
            ('"artificial intelligence"', "2026-10-02", "2"): {"count": 3, "total_pages": 2, "results": [C]},
            ('"super intelligence"', "2026-10-02", "1"): {"count": 1, "total_pages": 1, "results": [B]},
        }
        log = []
        docs, queries, failed, truncated = run_job.search_all(("W0", "W1"), log, fake_fetch_factory(pages),
                                                              sleep=lambda s: None)
        self.assertEqual(sorted(docs), ["A", "B", "C"])
        self.assertEqual(docs["B"]["terms_matched"], {"artificial intelligence", "super intelligence"})
        self.assertEqual(docs["A"]["window"], "W1")
        self.assertEqual(docs["B"]["agency_class"], "listed_independent")
        self.assertEqual(docs["C"]["agency_class"], "presidential")
        self.assertEqual(docs["A"]["top_agency"], "Energy Department")
        self.assertEqual((failed, truncated, len(queries)), (0, 0, 6))
        q = [x for x in queries if x["window"] == "W1" and x["term"] == '"artificial intelligence"'][0]
        self.assertEqual((q["count"], q["rows"], q["pages"]), (3, 3, 2))

    def test_search_all_fails(self):
        log = []
        docs, queries, failed, truncated = run_job.search_all(("W0", "W1"), log, fake_fetch_factory({}, True),
                                                              sleep=lambda s: None)
        self.assertEqual((len(docs), failed), (0, 6))

    def test_fetch_texts(self):
        good = ("Super Intelligence " * 40).encode()

        def fetch(url):
            if url == "u1":
                return good
            raise urllib.error.HTTPError(url, 404, "nf", None, None)
        docs = [{"document_number": "1", "raw_text_url": "u1", "top_agency": "X"},
                {"document_number": "2", "raw_text_url": "u2"},
                {"document_number": "3"}]
        ex = []
        self.assertIsNone(run_job.fetch_texts(docs, ex, fetch, sleep=lambda s: None))
        self.assertEqual([d["fetch_status"] for d in docs], ["ok", "http_404", "no_url"])
        self.assertEqual([d["readable"] for d in docs], [True, False, False])
        self.assertEqual((docs[0]["category"], docs[0]["counts"]["si"]), ("si_only", 40))
        self.assertEqual(len(ex), 1)

    def test_fetch_texts_stops(self):
        docs = [{"document_number": str(i), "raw_text_url": "u"} for i in range(20)]

        def fetch(url):
            raise OSError("down")
        self.assertEqual(run_job.fetch_texts(docs, [], fetch, sleep=lambda s: None),
                         run_job.MAX_CONSECUTIVE_FAILURES - 1)

    def test_main_w02_too_early(self):
        with mock.patch.object(census, "now", return_value="2026-11-20T00:00:00Z"):
            rc = run_job.main(["--out-dir", self.tmp, "--wave", "w02"])
        self.assertEqual(rc, 4)
        with open(os.path.join(self.tmp, "status.json"), encoding="utf-8") as fh:
            self.assertIn("w02", json.load(fh)["result"])

    def test_main_plan_not_public(self):
        with mock.patch.object(run_job, "wait_for_plan", return_value=(None, None, None)):
            rc = run_job.main(["--out-dir", self.tmp, "--wave", "w01"])
        self.assertEqual(rc, 3)


if __name__ == "__main__":
    unittest.main()
