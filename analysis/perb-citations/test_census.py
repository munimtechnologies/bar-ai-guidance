# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""Unit tests for the California PERB fabricated-citation census (no network)."""
import json
import os
import shutil
import tempfile
import unittest
import urllib.error
from unittest import mock

import census
import run_job

S_3041 = ("<p><strong>Description:</strong> Charging party filed seven charges.</p><p><strong>Disposition:</strong> "
          "The Board found that the charging party cited fabricated authority and imposed non-monetary sanctions for "
          "abuse of process.</p>")
S_3040 = ("<p>Description: The charging party alleged a breach of the duty of fair representation.</p><p>Disposition: "
          "OGC had admonished the party about citations to six nonexistent PERB decisions, citing Atwater.</p>")
S_2995EA = ("<p>Description: Corrected version of the decision issued on December 15, 2025.</p><p>Disposition: The "
            "Board issued an errata to correct the caption of the decision.</p>")
S_2995 = ("<p>Description: The charging party alleged that the association breached its duty of fair "
          "representation.</p><p>Disposition: In a precedential decision, the Board affirmed the dismissal and warned "
          "parties about briefs.</p>")
S_2950 = ("<p>Description: The union alleged that the district unilaterally changed its parking policy.</p>"
          "<p>Disposition: The Board reversed the proposed decision and dismissed the complaint.</p>")

FILLER = " The Board affirmed the dismissal of the unfair practice charge." * 6
FULL_FAKE = ("DECISION. The charging party's appeal cited fabricated authority and quotations that do not exist. "
             "The Board finds an abuse of process." + FILLER)
FULL_AI = ("DECISION. The charging party admitted that a generative AI tool drafted the appeal. The cases cited do not "
           "exist, and such hallucinated citations waste public resources." + FILLER)
FULL_OTHER = ("DECISION. The complaint is dismissed. The fictitious business name of the employer is irrelevant."
              + FILLER)


def item(i, slug, date, summary):
    return {"id": i, "slug": slug, "date": date, "link": "https://perb.ca.gov/decision/%s/" % slug,
            "title": {"rendered": slug.upper()}, "content": {"rendered": summary, "protected": False}}


PAGE_A = json.dumps([item(1, "3041h", "2026-07-16T16:23:09", S_3041),
                     item(2, "3040m", "2026-07-15T10:00:00", S_3040),
                     item(3, "2995ea", "2025-12-20T09:00:00", S_2995EA)]).encode("utf-8")
PAGE_B = json.dumps([item(1, "3041h", "2026-07-16T16:23:09", S_3041),
                     item(4, "2995e", "2025-12-15T12:00:00", S_2995),
                     item(5, "2950e", "2024-03-01T12:00:00", S_2950),
                     item(6, "2800e", "2021-12-30T12:00:00", S_2950)]).encode("utf-8")


def page_html(heading, date, kind, link=""):
    return ('<html><head><title>PERB</title></head><body>'
            '<div class="banner">Notice on generative AI: see <a href="https://perb.ca.gov/decision/2995E/">Atwater</a>'
            '</div><h1 class="entry-title">Decision %s</h1>'
            '<p><strong>Decision Date:</strong> %s</p><p><strong>Decision Type:</strong> %s</p>%s'
            '<aside><a href="/decision/3074M">3074M</a></aside></body></html>') % (heading, date, kind, link)


ATW = "2995E &#8211; Atwater Elementary Teachers Association, CTA/NEA (Garcia)"
PAGES = {
    "3041h": page_html("3041H &#8211; Regents of the University of California and Jane McKeown", "July 16, 2026",
                       "PERB Decision", '<a href="https://perb.ca.gov/wp-content/uploads/decisionbank/'
                                        'decision-3041h.pdf">View Full Text (PDF)</a>'),
    "3040m": page_html("3040M &#8211; County of Somewhere and Jane Roe", "July 15, 2026",
                       "PERB Decision (Non-Precedential)"),
    "2995ea": page_html(ATW.replace("2995E", "2995EA"), "December 20, 2025", "PERB Decision"),
    "2995e": page_html(ATW, "December 15, 2025", "PERB Decision",
                       '<a href="/wp-content/uploads/decisionbank/decision-2995e.pdf?ver=2">View Full Text (PDF)</a>'),
    "2950e": page_html("2950E &#8211; Fresno Unified School District", "March 1, 2024", "PERB Decision",
                       '<a href="https://perb.ca.gov/wp-content/uploads/decisionbank/decision-2950e.pdf">PDF</a>'),
}
PDF = "https://perb.ca.gov/wp-content/uploads/decisionbank/decision-"

CSV_PLAIN = ("case_id,Case Name,Court,State(s),Date,Details\n"
             "2625,In the Matter of X,USPTO,USA,2026-07-27,\n"
             "10,Thorogood v. MSPB,Fed. Cir.,USA,2026-10-08,\n")
CSV_NUM = CSV_PLAIN + "11,Doe v. Union,Cal. Ct. App.,USA,2026-09-01,Appeal from PERB Decision No. 3041-H\n"
CSV_PERB = CSV_PLAIN + "978,Christina Garcia v. Atwater Elementary Teachers Association,California PERB,USA,2025-12-15,\n"


def two_pages(url):
    if "&page=1&" in url:
        return PAGE_A
    if "&page=2&" in url:
        return PAGE_B
    raise AssertionError("unexpected listing page: " + url)


class Parsing(unittest.TestCase):
    def test_html_text_and_url(self):
        self.assertEqual(census.html_text("<p>A&amp;B</p><p>C</p><script>x()</script>"), "A&B C")
        self.assertIn("&page=2&", census.listing_url(2))
        self.assertIn("_fields=", census.listing_url(2))
        self.assertEqual(census.page_url({"link": "https://evil.example/decision/x/", "slug": "3041h"}),
                         "https://perb.ca.gov/decision/3041h/")
        self.assertEqual(census.page_url({"link": "https://perb.ca.gov/decision/3041h/", "slug": "x"}),
                         "https://perb.ca.gov/decision/3041h/")

    def test_slugs(self):
        s = census.parse_slug("3041h")
        self.assertEqual((s["prefix"], s["number"], s["suffix"], s["decision_key"], s["slug_ok"]),
                         ("", "3041", "h", "3041h", True))
        s = census.parse_slug("a530ha")
        self.assertEqual((s["prefix"], s["number"], s["suffix"], s["decision_key"]), ("a", "530", "ha", "a530h"))
        self.assertEqual(census.parse_slug("i063e")["decision_key"], "i063e")
        self.assertEqual(census.parse_slug("2889hb")["decision_key"], "2889h")
        s = census.parse_slug("weird-slug")
        self.assertEqual((s["decision_key"], s["slug_ok"], s["number"]), ("weird-slug", False, None))

    def test_api_page(self):
        got = census.parse_api_page(PAGE_A)
        self.assertEqual([e["slug"] for e in got], ["3041h", "3040m", "2995ea"])
        self.assertEqual([e["date"] for e in got], ["2026-07-16", "2026-07-15", "2025-12-20"])
        self.assertTrue(got[0]["summary"].startswith("Description: Charging party filed seven charges."))
        self.assertEqual(got[2]["decision_key"], "2995e")
        self.assertEqual(census.parse_api_page(b"[]"), [])
        with self.assertRaises(ValueError):
            census.parse_api_page(b'{"code": "rest_post_invalid_page_number"}')
        self.assertTrue(census.in_window({"date": "2022-01-01"}))
        self.assertFalse(census.in_window({"date": "2021-12-31"}))
        self.assertFalse(census.in_window({"date": None}))

    def test_page(self):
        p = census.parse_page(PAGES["3041h"], "3041h", "https://perb.ca.gov/decision/3041h/")
        self.assertEqual((p["pdf_url"], p["pdf_links"], p["decision_date"], p["nonprecedential"]),
                         (PDF + "3041h.pdf", 1, "2026-07-16", False))
        self.assertEqual(p["heading"], "Decision 3041H – Regents of the University of California and Jane McKeown")
        p = census.parse_page(PAGES["2995e"].encode("utf-8"), "2995e", "https://perb.ca.gov/decision/2995e/")
        self.assertEqual((p["pdf_url"], p["decision_date"]), (PDF + "2995e.pdf", "2025-12-15"))
        p = census.parse_page(PAGES["3040m"], "3040m", "https://perb.ca.gov/decision/3040m/")
        self.assertEqual((p["pdf_url"], p["pdf_links"], p["nonprecedential"]), ("", 0, True))
        two = ('<a href="/wp-content/uploads/decisionbank/a.pdf">x</a>'
               '<a href="/wp-content/uploads/decisionbank/b.pdf">y</a>')
        p = census.parse_page(two, "3041h", "https://perb.ca.gov/decision/3041h/")
        self.assertEqual((p["pdf_url"], p["pdf_links"], p["decision_date"], p["heading"]), ("", 2, None, ""))
        self.assertEqual(census.parse_long_date("December 15, 2025"), "2025-12-15")
        self.assertIsNone(census.parse_long_date("Sept. 5, 2025"))
        self.assertTrue(run_job.on_site(PDF + "3041h.pdf"))
        self.assertFalse(run_job.on_site("https://perb.ca.gov.evil.com/x.pdf"))


class Classify(unittest.TestCase):
    def test_full_ai(self):
        r = census.classify(FULL_AI)
        for k in ("fake_cite", "ai_mention", "ai_citation", "hallucination"):
            self.assertTrue(r[k], k)
        self.assertFalse(r["atwater"])
        self.assertIn("fake_cite", r["excerpts"])

    def test_summaries(self):
        r = census.classify(census.html_text(S_3040))
        self.assertTrue(r["fake_cite"] and r["atwater"])
        self.assertFalse(r["ai_mention"])
        r = census.classify(census.html_text(S_3041))
        self.assertTrue(r["fake_cite"] and r["abuse_of_process"])
        for s in (S_2995EA, S_2995, S_2950):
            r = census.classify(census.html_text(s))
            self.assertFalse(any(r[k] for k in census.FLAG_KEYS), s)

    def test_other(self):
        r = census.classify(FULL_OTHER)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))
        self.assertFalse(census.classify("Al Capone testified about the LL.M. program.")["ai_mention"])
        self.assertTrue(census.classify("This is an abuse of the PERB's process.")["abuse_of_process"])
        r = census.classify("")
        self.assertEqual(r["chars"], 0)
        self.assertFalse(any(r[k] for k in census.FLAG_KEYS))

    def test_combine(self):
        d = census.combine({}, census.classify(census.html_text(S_2995)), census.classify(FULL_AI))
        self.assertEqual((d["fake_summary"], d["fake_full"], d["fake_cite"], d["ai_mention"], d["summary_ok"]),
                         (False, True, True, True, True))
        d = census.combine({}, census.classify("short"), None)
        self.assertEqual((d["fake_cite"], d["summary_ok"], d["chars_full"]), (False, False, 0))


class Database(unittest.TestCase):
    def test_rows(self):
        db = census.db_check(CSV_PLAIN)
        self.assertEqual((len(db["perb_rows"]), len(db["joined"])), (0, 2))
        self.assertEqual(len(census.db_check(CSV_PERB)["perb_rows"]), 1)
        self.assertEqual(len(census.db_check(CSV_NUM)["perb_rows"]), 0)

    def test_tokens(self):
        self.assertEqual(census.name_tokens("Decision 2995E – Atwater Elementary Teachers Association, CTA/NEA "
                                            "(Garcia)"), ["Atwater", "Garcia"])

    def test_in_db(self):
        d41 = {"number": "3041", "suffix": "h",
               "heading": "Decision 3041H – Regents of the University of California and Jane McKeown"}
        d95 = {"number": "2995", "suffix": "e",
               "heading": "Decision 2995E – Atwater Elementary Teachers Association, CTA/NEA (Garcia)"}
        wrong = {"number": "3041", "suffix": "e", "heading": ""}
        self.assertTrue(census.in_db(census.db_check(CSV_NUM), d41))
        self.assertFalse(census.in_db(census.db_check(CSV_NUM), wrong))
        self.assertFalse(census.in_db(census.db_check(CSV_NUM), d95))
        self.assertFalse(census.in_db(census.db_check(CSV_PLAIN), d41))
        self.assertFalse(census.in_db(census.db_check(CSV_PERB), d41))
        self.assertTrue(census.in_db(census.db_check(CSV_PERB), d95))
        self.assertFalse(census.in_db(None, d95))


class Frame(unittest.TestCase):
    def setUp(self):
        self.p = mock.patch.object(run_job, "DELAY_S", 0)
        self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_two_pages(self):
        seen = []

        def fetch(url):
            seen.append(url)
            return two_pages(url)
        docs, info, failed = run_job.build_frame([], fetch)
        self.assertEqual((failed, len(seen), info["pages"], info["complete"]), (0, 2, 2, True))
        self.assertEqual([d["slug"] for d in docs], ["3041h", "3040m", "2995ea", "2995e", "2950e"])
        self.assertEqual((info["posts_read"], info["same_slug_skipped"], info["in_frame"], info["outside_window"]),
                         (7, 1, 5, 1))
        self.assertEqual((info["decisions_in_frame"], info["known_in_frame"], info["later_versions_in_frame"],
                          info["prefixed_in_frame"], info["unparsed_slugs_in_frame"]), (4, 4, 1, 0, 0))
        self.assertEqual(info["in_frame_by_year"], {"2024": 1, "2025": 2, "2026": 2})

    def test_empty_page_ends(self):
        docs, info, failed = run_job.build_frame([], lambda u: PAGE_A if "&page=1&" in u else b"[]")
        self.assertEqual((failed, len(docs), info["pages"], info["complete"]), (0, 3, 2, True))

    def test_http_400_ends(self):
        def fetch(url):
            if "&page=1&" in url:
                return PAGE_A
            raise urllib.error.HTTPError(url, 400, "bad page", {}, None)
        docs, info, failed = run_job.build_frame([], fetch)
        self.assertEqual((failed, len(docs), info["pages"], info["complete"]), (0, 3, 1, True))

    def test_incomplete_and_failure(self):
        docs, info, failed = run_job.build_frame([], lambda u: PAGE_A)
        self.assertEqual((failed, len(docs), info["pages"], info["complete"]), (0, 3, run_job.MAX_PAGES, False))

        def boom(url):
            raise OSError("down")
        docs, info, failed = run_job.build_frame([], boom)
        self.assertEqual((docs, failed), ([], 1))
        self.assertIn("error", info)


class Grade(unittest.TestCase):
    def test_no_fake(self):
        doc = {"slug": "2950e", "decision_key": "2950e", "date": "2024-03-01", "summary_ok": True,
               "pdf_posted": True, "readable_full": True}
        v = {k: x["verdict"] for k, x in census.grade([doc], census.db_check(CSV_PLAIN))["predictions"].items()}
        self.assertEqual(v, {"P1": "failed", "P2": "failed", "P3": "held", "P4": "failed", "P5": "not testable",
                             "P6": "not testable", "P7": "held", "P8": "failed"})
        self.assertEqual(census.grade([doc], None)["predictions"]["P6"]["verdict"], "not testable")
        v = census.grade([], None)["predictions"]
        self.assertEqual((v["P4"]["verdict"], v["P7"]["verdict"]), ("not testable", "failed"))


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_get(self, url, tries=3, timeout=120, accept="*/*"):
        if url == run_job.CSV_URL:
            return CSV_PERB.encode("utf-8"), "text/csv"
        if url.startswith(census.API):
            return two_pages(url), "application/json"
        if url.endswith(".pdf"):
            return b"%PDF-" + url.encode("utf-8"), "application/pdf"
        for slug, body in PAGES.items():
            if url == "https://perb.ca.gov/decision/%s/" % slug:
                return body.encode("utf-8"), "text/html"
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)

    @staticmethod
    def fake_text(data):
        if b"3041h" in data:
            return FULL_FAKE
        if b"2995e" in data:
            return FULL_AI
        return FULL_OTHER

    def run_main(self, extra=()):
        ps = [mock.patch.object(run_job, "DELAY_S", 0),
              mock.patch.object(run_job, "get_retry", self.fake_get),
              mock.patch.object(run_job, "pdf_text", self.fake_text),
              mock.patch.object(run_job, "wait_for_plan", lambda m, s: ({"sha": "a"}, {"sha": "b"}, s))] + list(extra)
        for p in ps:
            p.start()
        try:
            return run_job.main(["--out-dir", self.tmp])
        finally:
            for p in reversed(ps):
                p.stop()

    def test_main(self):
        rc = self.run_main([mock.patch.object(census, "MIN_FRAME", 1)])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.tmp, "results.json"), encoding="utf-8") as fh:
            body = fh.read()
        res = json.loads(body)
        v = {k: x["verdict"] for k, x in res["predictions"].items()}
        self.assertEqual(v, {"P1": "failed", "P2": "failed", "P3": "held", "P4": "held", "P5": "held",
                             "P6": "failed", "P7": "held", "P8": "failed"})
        self.assertEqual(res["predictions"]["P4"]["detail"]["full_only"], ["2995e"])
        self.assertEqual(res["predictions"]["P6"]["detail"]["missing"], ["3040m", "3041h"])
        c = res["counts"]
        self.assertEqual((c["in_frame"], c["decisions"], c["pdf_posted"], c["readable_full"], c["fake_cite_posts"],
                          c["fake_cite_decisions"], c["fake_summary"], c["fake_full"], c["nonprecedential"]),
                         (5, 4, 3, 3, 3, 3, 2, 2, 1))
        self.assertEqual((c["ai_mention"], c["hallucination"], c["atwater"], c["abuse_of_process"]), (1, 1, 1, 1))
        for name in ("McKeown", "Garcia", "Christina", "Somewhere", "Fresno"):
            self.assertNotIn(name, body)
        with open(os.path.join(self.tmp, "rows.csv"), encoding="utf-8") as fh:
            rows = fh.read()
        self.assertEqual(len(rows.splitlines()), 6)
        for name in ("McKeown", "Garcia", "Fresno", "Description"):
            self.assertNotIn(name, rows)
        self.assertEqual(sorted(os.listdir(os.path.join(self.tmp, "private", "texts"))),
                         ["2995e.txt", "3040m.txt", "3041h.txt"])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "private", "excerpts.txt")))

    def test_main_stops_small_frame(self):
        self.assertEqual(self.run_main(), 6)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "results.json")))


if __name__ == "__main__":
    unittest.main()
