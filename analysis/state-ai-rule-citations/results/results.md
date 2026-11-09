# State AI rule citation census 1.0.0: results

Data: AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0), CSV SHA-256 `bcd49cf6e3cb05f4ade4ac51aabcebe9a6aa731fc0a61bfa0291329aa2f92d20`, fetched 2026-11-09T15:25:28Z. Decision texts: the documents the database links. Information about public decisions, not legal advice. Made with AI agents working in MV2's name.

Counts: {"rows_in_scope": 87, "by_doc_status": {"no_document": 2, "ok": 85}, "unreadable": 1, "readable": 84}

| state | rule | effective | post: cite / readable | pre: cite / readable |
|---|---|---|---|---|
| NY | 22 NYCRR Part 161 | 2026-06-01 | 0 / 15 | 0 / 25 |
| FL | Fla. R. Gen. Prac. & Jud. Admin. 2.515 | 2026-06-15 | 8 / 11 | 2 / 13 |
| CT | Connecticut Practice Book Section 4-9 | 2026-06-23 | 2 / 2 | 0 / 2 |
| IN | Indiana Trial Rule 11 (and 11.1, 11.2) | 2026-08-01 | 1 / 4 | 1 / 12 |

| prediction | verdict | detail |
|---|---|---|
| H1 | held | `{"n": 32, "cites": 11, "share": 0.344}` |
| H2 | held | `{"n": 15, "part_130": 9, "part_161": 0}` |
| H3 | held | `{"post": {"n": 11, "cites": 8, "share": 0.727}, "pre": {"n": 13, "cites": 2, "share": 0.154}}` |
| H4 | held | `{"post": {"n": 4, "cites": 1, "share": 0.25}, "pre": {"n": 12, "cites": 1, "share": 0.083}}` |
| H5 | failed | `{"lawyer": {"n": 16, "cites": 5, "share": 0.312}, "pro_se": {"n": 16, "cites": 6, "share": 0.375}}` |
| H6 | held | `{"n": 15, "matches": 0}` |

Secondary (post period): `{"ny_part_130": 9, "fl_2515_d2": 8, "fl_57105": 0, "ct_85_2_or_62_6": 1, "in_11_1_or_11_2": 0}`

Secondary (pre period): `{"ny_part_130": 11, "fl_2515_d2": 2, "fl_57105": 1, "ct_85_2_or_62_6": 0, "in_11_1_or_11_2": 0}`
