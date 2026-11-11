# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review  # noqa: E402

ROWS = (
    "docket_entry_id,dockets,date,kind,event_code\n"
    "e87a6f9d-54aa-42d6-9477-25440d55797e,6165-24,2025-12-31,order,ODD\n"
    "9f88fb85-fa99-47bc-9688-44f0057af74f,17165-19;17206-19,2025-03-25,opinion,MOP\n"
    ",1-23,2025-01-01,order,O\n"
)


class TestReview(unittest.TestCase):
    def test_parse_rows_first_docket_and_skips_blank_ids(self):
        rows = review.parse_rows(ROWS)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("e87a6f9d-54aa-42d6-9477-25440d55797e", "6165-24", "2025-12-31", "order"))
        self.assertEqual(rows[1][1], "17165-19")

    def test_review_pattern_catches_the_known_miss(self):
        text = ("the declaration cites a Tax Court case (“93 T.C. 125”) that does not exist, "
                "and resembles output from chatbots such as ChatGPT.")
        spans = review.hits(text, width=20)
        terms = {t for s in spans for t in s[2]}
        self.assertIn("does not exist", terms)
        self.assertIn("chatgpt", terms)

    def test_review_pattern_other_forms(self):
        for s in ("we were unable to locate the case", "the Court could not find any such opinion",
                  "no such case", "a fictitious opinion", "hallucinated", "large language model",
                  "AI tools", "non-existent"):
            self.assertTrue(review.REVIEW.search(s), s)
        self.assertFalse(review.REVIEW.search("the aid was paid"))
        self.assertFalse(review.REVIEW.search("ai lowercase is not matched"))

    def test_hits_merge_overlapping_windows_and_cap(self):
        text = "fake " * 3 + "x" * 1000 + " bogus"
        spans = review.hits(text, width=10)
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0][2], ["fake"])
        self.assertEqual(spans[1][2], ["bogus"])
        many = " ".join("fake " + "y" * 50 for _ in range(10))
        self.assertEqual(len(review.hits(many, width=1, cap=3)), 3)

    def test_normalize_joins_split_words(self):
        self.assertEqual(review.normalize("non-\n existent  cases"), "non-existent cases")

    def test_urls(self):
        self.assertEqual(review.search_url("opinion", "Tellock"),
                         review.API + "/opinion-search?keyword=Tellock&dateRange=allDates"
                         "&opinionTypes=MOP,OST,SOP,TCOP")
        self.assertEqual(review.download_url("6165-24", "abc"),
                         review.API + "/6165-24/abc/public-document-download-url")


if __name__ == "__main__":
    unittest.main()
