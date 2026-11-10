# Agency AI-authority census 1.0.0: results

Data: AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0), CSV SHA-256 `bcd49cf6e3cb05f4ade4ac51aabcebe9a6aa731fc0a61bfa0291329aa2f92d20`, fetched 2026-11-10T06:15:25Z. Decision texts: the documents the database links. Information about public decisions, not legal advice. Made with AI agents working in MV2's name.

Counts: `{"rows_in_scope": 8, "by_forum": {"OTHER_FED": 2, "USPTO": 1, "TAXCT": 5}, "by_doc_status": {"ok": 7, "no_document": 1}, "unreadable": 0, "readable": 7, "readable_by_forum": {"OTHER_FED": 2, "USPTO": 1, "TAXCT": 4}, "readable_by_year": {"2025": 1, "2026": 5, "2024": 1}, "readable_by_party": {"pro_se": 2, "lawyer": 4, "other": 1}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| Q1 | agency decisions citing a named AI instrument (USPTO 2024 guidance or EOIR PM 25-40) < 25% | not testable | `{"n": 3, "k": 1, "share": 0.333}` |
| Q2 | agency decisions citing the forum's own signature/sanction/conduct regulation >= 40% | not testable | `{"n": 3, "k": 1, "share": 0.333}` |
| Q3 | agency decisions: forum's own regulation cited more often than FRCP 11 | not testable | `{"forum_rule": {"n": 3, "k": 1, "share": 0.333}, "frcp_11": {"n": 3, "k": 1, "share": 0.333}}` |
| Q4 | USPTO decisions citing 37 CFR 11.18 >= 50% | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| Q5 | USPTO decisions from 2024-04-11 citing the USPTO AI guidance < 50% | not testable | `{"n": 1, "k": 0, "share": 0.0}` |
| Q6 | Tax Court decisions citing 26 U.S.C. 6673 < 50% | not testable | `{"n": 4, "k": 0, "share": 0.0}` |
| Q7 | method check: AI-instrument patterns match at most 1 decision dated before 2024-04-11 | held | `{"n": 0, "matches": 0}` |
| Q8 | Mata v. Avianca cited in >= 15% of all readable decisions | not testable | `{"n": 7, "k": 0, "share": 0.0}` |

## Flags by forum (k of n readable)

| forum | n | ai_instrument | uspto_ai_guidance_2024 | eoir_pm_25_40 | forum_rule | uspto_11_18 | tax_6673 | frcp_11 | inherent | model_rules | usc_1001 | mata | ai_words |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OTHER_FED | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |
| TAXCT | 4 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 4 |
| USPTO | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

Decisions citing none of: AI instrument, forum rule, FRCP 11, inherent authority, Model Rules, 18 U.S.C. 1001: `{"n": 2, "of": 7}`
