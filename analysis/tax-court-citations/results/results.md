# U.S. Tax Court fabricated-citation census 1.0.0: results

Frame: every order and opinion filed 2023-01-01 to 2026-11-10 that the court's own DAWSON search returns for a fixed list of keyword searches. Coverage check against the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Information about public court documents, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "5e75b67d0bae5cf74dc0fc4beba2a88143485ff4", "date": "2026-11-10T16:39:54Z"}, "census_commit": {"sha": "5e75b67d0bae5cf74dc0fc4beba2a88143485ff4", "date": "2026-11-10T16:39:54Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-10T23:51:06Z", "bytes": 2197049, "sha256": "cac050d540f21e708436491720383f019184eaa9babf3e452a0c8e542ebc77b1", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "dawson": {"api": "https://public-api-green.dawson.ustaxcourt.gov/public-api", "searches": 54, "failed": 0, "in_frame": 78, "built_at": "2026-11-10T23:54:12Z"}}`

Counts: `{"in_frame": 78, "readable": 78, "fake_cite": 3, "fake_cite_orders": 1, "ai_mention": 8, "ai_citation": 2, "by_year": {"2023": {"readable": 19, "fake_cite": 0, "ai_citation": 0}, "2024": {"readable": 23, "fake_cite": 1, "ai_citation": 1}, "2025": {"readable": 18, "fake_cite": 1, "ai_citation": 0}, "2026": {"readable": 18, "fake_cite": 1, "ai_citation": 1}}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | the frame holds at least 10 readable documents with a fabricated-citation phrase | failed | `{"n": 3}` |
| P2 | fewer than half of the fabricated-citation documents are in the AI Hallucination Cases Database | failed | `{"n": 3, "k": 3, "share": 1.0}` |
| P3 | fewer than half of the fabricated-citation documents mention an AI term | failed | `{"n": 3, "k": 2, "share": 0.667}` |
| P4 | at least half of the fabricated-citation documents are orders, not opinions | failed | `{"n": 3, "k": 1, "share": 0.333}` |
| P5 | at least half of the fabricated-citation documents cite Tax Court Rule 33(b) | held | `{"n": 3, "k": 2, "share": 0.667}` |
| P6 | fewer than half of the fabricated-citation documents cite section 6673 | held | `{"n": 3, "k": 0, "share": 0.0}` |
| P7 | every US Tax Court row of the database dated in the window matches a document in the frame | failed | `{"n": 5, "missed_case_ids": ["1703"]}` |
| P8 | search check: at least 90% of readable frame documents whose text contains 'artificial intelligence' were returned by the exact-phrase search for it | held | `{"n": 5, "k": 5, "share": 1.0}` |

## Searches

| search | results | in window |
|---|---|---|
| order `"artificial intelligence"` | 3 | 1 |
| opinion `"artificial intelligence"` | 8 | 4 |
| order `artificial intelligence` | 3 | 1 |
| opinion `artificial intelligence` | 10 | 6 |
| order `ChatGPT` | 1 | 1 |
| opinion `ChatGPT` | 0 | 0 |
| order `generative` | 0 | 0 |
| opinion `generative` | 2 | 1 |
| order `"large language model"` | 1 | 1 |
| opinion `"large language model"` | 1 | 1 |
| order `hallucinated` | 0 | 0 |
| opinion `hallucinated` | 1 | 1 |
| order `hallucination` | 1 | 1 |
| opinion `hallucination` | 1 | 1 |
| order `hallucinations` | 1 | 1 |
| opinion `hallucinations` | 2 | 1 |
| order `hallucinate` | 0 | 0 |
| opinion `hallucinate` | 0 | 0 |
| order `nonexistent` | 32 | 7 |
| opinion `nonexistent` | 357 | 57 |
| order `non-existent` | 37 | 5 |
| opinion `non-existent` | 51 | 1 |
| order `nonexistent cases` | 20 | 7 |
| opinion `nonexistent cases` | 316 | 54 |
| order `nonexistent case` | 28 | 4 |
| opinion `nonexistent case` | 336 | 49 |
| order `nonexistent citations` | 1 | 0 |
| opinion `nonexistent citations` | 58 | 11 |
| order `fictitious` | 42 | 6 |
| opinion `fictitious` | 417 | 15 |
| order `fictitious cases` | 15 | 3 |
| opinion `fictitious cases` | 335 | 12 |
| order `fictitious case` | 41 | 6 |
| opinion `fictitious case` | 401 | 15 |
| order `fictitious citations` | 6 | 2 |
| opinion `fictitious citations` | 96 | 4 |
| order `fake` | 12 | 3 |
| opinion `fake` | 38 | 8 |
| order `fake cases` | 2 | 1 |
| opinion `fake cases` | 27 | 6 |
| order `fake citations` | 0 | 0 |
| opinion `fake citations` | 7 | 1 |
| order `fabricated` | 18 | 1 |
| opinion `fabricated` | 167 | 21 |
| order `fabricated citations` | 3 | 0 |
| opinion `fabricated citations` | 19 | 1 |
| order `fabricated cases` | 7 | 1 |
| opinion `fabricated cases` | 117 | 21 |
| order `fabricated quotations` | 0 | 0 |
| opinion `fabricated quotations` | 5 | 0 |
| order `bogus` | 29 | 2 |
| opinion `bogus` | 98 | 10 |
| order `Avianca` | 1 | 0 |
| opinion `Avianca` | 0 | 0 |

## Documents with a fabricated-citation phrase

| docket | date | kind | in database | flags |
|---|---|---|---|---|
| [10795-22](https://dawson.ustaxcourt.gov/case-detail/10795-22) | 2024-10-23 | order | True | fake_cite, ai_mention, ai_citation, ai_phrase, rule_33, action |
| [12241-20](https://dawson.ustaxcourt.gov/case-detail/12241-20) | 2025-05-20 | opinion | True | fake_cite, action |
| [8077-23](https://dawson.ustaxcourt.gov/case-detail/8077-23) | 2026-02-09 | opinion | True | fake_cite, ai_mention, ai_citation, ai_phrase, rule_33, action |
