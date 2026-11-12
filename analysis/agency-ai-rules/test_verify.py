# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify  # noqa: E402

TEXT = ("Any party who uses generative AI must disclose it and certify that each citation was verified. "
        "Fictitious cases may be stricken. See 29 C.F.R. 18.35 and 1 Tex. Admin. Code 155.303. "
        "Issued July 8, 2026. A Model Note of SI Use; super intelligence.")


class TestVerify(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(verify.normalize(" a \n\n b\tc "), "a b c")
        self.assertEqual(verify.normalize(None), "")

    def test_html_to_text(self):
        page = "<html><style>p{x:1}</style><script>var a=1;</script><p>Order&nbsp;on <b>AI</b></p></html>"
        self.assertEqual(verify.html_to_text(page), "Order on AI")

    def test_hits(self):
        counts, ex = verify.find_hits(TEXT)
        self.assertEqual(counts["ai_term"], 2)
        self.assertEqual(counts["super_intel"], 2)
        self.assertEqual(counts["disclos"], 1)
        self.assertEqual(counts["certif"], 1)
        self.assertEqual(counts["verif"], 1)
        self.assertEqual(counts["fictitious"], 1)
        self.assertEqual(counts["sanction"], 1)
        self.assertEqual(counts["cfr"], 1)
        self.assertEqual(counts["state_rule"], 1)
        self.assertEqual(counts["dated"], 1)
        self.assertEqual(counts["evidence"], 0)
        self.assertTrue(any(k == "disclos" and "must disclose" in s for k, _, s in ex))

    def test_ai_term_is_case_sensitive_for_ai(self):
        self.assertEqual(verify.find_hits("PAID; said; aide; Sign")[0]["ai_term"], 0)
        self.assertEqual(verify.find_hits("Artificial Intelligence")[0]["ai_term"], 1)
        self.assertEqual(verify.find_hits("Simple; SIGN")[0]["super_intel"], 0)

    def test_is_pdf(self):
        self.assertTrue(verify.is_pdf(b"%PDF-1.6 rest"))
        self.assertFalse(verify.is_pdf(b"<html>"))

    def test_fixed_list(self):
        self.assertLessEqual(len(verify.DOCS), verify.MAX_DOCS)
        self.assertEqual(len({u for _, u in verify.DOCS}), len(verify.DOCS))
        self.assertEqual(len({i for i, _ in verify.DOCS}), len(verify.DOCS))
        self.assertTrue(all(u.startswith("https://") for _, u in verify.DOCS))
        self.assertGreaterEqual(verify.DELAY_S, 10)


if __name__ == "__main__":
    unittest.main()
