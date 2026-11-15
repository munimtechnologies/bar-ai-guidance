# California WCAB fabricated-citation census 1.0.0: results

Frame: every panel decision listed on the WCAB's panel-decision page in its 2024 to 2026 folders. Information about public decisions of a state workers' compensation tribunal, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "e50471046c1328e5e74318d2e14e1edaa9a9ed99", "date": "2026-11-12T08:58:24Z"}, "census_commit": {"sha": "e50471046c1328e5e74318d2e14e1edaa9a9ed99", "date": "2026-11-12T08:58:24Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-15T00:12:29Z", "bytes": 2199394, "sha256": "74aa53afdb861f4e90fae6a2742d5a14d1bd5ea42b289d9972f25b37dea49e99", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "wcab": {"listing": "https://www.dir.ca.gov/wcab/wcab-Decisions.htm", "failed": 0, "in_frame": 3123, "built_at": "2026-11-15T00:12:34Z"}}`

Listing: `{"url": "https://www.dir.ca.gov/wcab/wcab-Decisions.htm", "table_rows": 5891, "entries": 5885, "headers": 6, "no_date": 22, "no_link": 8, "no_folder_year": 0, "no_adj": 25, "date_folder_mismatch": 0, "bytes": 1935377, "sha256": "a2edd167b8be6f52ebc20077efd09350275aab5314e8719f70fd10dba425ced5", "fetched_at": "2026-11-15T00:12:34Z", "in_frame": 3123, "same_link_skipped": 4, "outside_years": 2758, "no_date_in_frame": 0, "no_link_in_frame": 0, "known_in_frame": 6, "in_frame_by_year": {"2024": 1089, "2025": 1119, "2026": 915}}`

Counts: `{"in_frame": 3123, "readable": 3121, "fake_cite": 12, "fake_cite_cases": 9, "ai_mention": 5, "ai_citation": 3, "hallucination": 6, "noland": 3, "sedano": 3, "lc5813": 238, "nit": 60, "fetch_status": {"extract_error": 1, "http_404": 1, "ok": 3121}, "by_year": {"2024": {"readable": 1089, "fake_cite": 0, "ai_mention": 0, "hallucination": 1, "lc5813": 71, "nit": 20}, "2025": {"readable": 1117, "fake_cite": 7, "ai_mention": 2, "hallucination": 2, "lc5813": 95, "nit": 21}, "2026": {"readable": 915, "fake_cite": 5, "ai_mention": 3, "hallucination": 3, "lc5813": 72, "nit": 19}}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | recall check (not blind): every one of the six hand-checked decisions is in the frame and has a fabricated-citation phrase | held | `{"known_in_frame": 6, "flagged": 6}` |
| P2 | 10 to 40 decisions in the frame have a fabricated-citation phrase | held | `{"n": 12}` |
| P3 | at most one 2024 decision has a fabricated-citation phrase | held | `{"n_2024": 0}` |
| P4 | more 2026 decisions than 2025 decisions have a fabricated-citation phrase | failed | `{"n_2025": 7, "n_2026": 5}` |
| P5 | fewer than half of the fabricated-citation decisions mention an AI term | held | `{"n": 12, "k": 4}` |
| P6 | at least three quarters of the fabricated-citation decisions cite Labor Code section 5813 (the WCAB's sanctions statute) | held | `{"n": 12, "k": 9}` |
| P7 | the database has no WCAB-court row, and at least three cases with a fabricated-citation decision are not in it (not blind: no WCAB row on 11 Nov 2026) | held | `{"wcab_rows": 0, "cases": 9, "missing": 9}` |
| P8 | at least two fabricated-citation decisions other than the six hand-checked ones mention Sedano (the WCAB's published 2025 sanctions decision) | failed | `{"k": 0}` |
| P9 | method check: at least 98% of the decisions in the frame are readable | held | `{"readable": 3121, "in_frame": 3123, "share": 0.9994}` |

## Decisions with a fabricated-citation phrase

| row | folder | date | ADJ | in database | hand-checked | flags |
|---|---|---|---|---|---|---|
| 7c8cb284c732 | 2026 | 2026-09-24 | ADJ17817958+ADJ17817957 | False | False | fake_cite, ai_mention, ai_citation, hallucination, noland, lc5813, nit |
| 3ea6e0d458bf | 2026 | 2026-07-28 | ADJ8963138 | False | False | fake_cite |
| 590bec41f942 | 2026 | 2026-06-26 | ADJ17889413 | False | True | fake_cite, ai_mention, ai_citation, hallucination, noland, sedano, lc5813, nit |
| f49373b74505 | 2026 | 2026-04-16 | ADJ16902178 | False | True | fake_cite, lc5813, nit |
| d8a369bbe378 | 2026 | 2026-04-13 | ADJ14015513 | False | False | fake_cite |
| 2c4ba1b28017 | 2025 | 2025-12-23 | ADJ16902178 | False | True | fake_cite, lc5813, nit |
| 13865e0f8cdc | 2025 | 2025-12-04 | ADJ10934327 | False | False | fake_cite |
| 3d6cddb32fbf | 2025 | 2025-12-01 | ADJ17889413 | False | True | fake_cite, ai_mention, ai_citation, hallucination, lc5813, nit |
| f8e8e07903f1 | 2025 | 2025-10-13 | ADJ17817958+ADJ17817957 | False | False | fake_cite, lc5813, nit |
| df3d85cd6f5b | 2025 | 2025-09-22 | ADJ12865802 | False | True | fake_cite, ai_mention, lc5813, nit |
| 3610a4cb752f | 2025 | 2025-08-18 | ADJ10983565 | False | False | fake_cite, lc5813 |
| 49c58bc824ec | 2025 | 2025-07-29 | ADJ17550375+ADJ17550386 | False | True | fake_cite, sedano, lc5813, nit |

## Other decisions with an AI term, 'hallucinat...', Noland or Sedano

| row | folder | date | ADJ | flags |
|---|---|---|---|---|
| 5a5cac4ea72e | 2026 | 2026-10-30 | ADJ21873454 | sedano |
| 5fd30e0baebe | 2026 | 2026-06-08 | ADJ9898563+ADJ10657938 | ai_mention |
| 6b65b288cff5 | 2026 | 2026-05-26 | ADJ12239672+ADJ13283843 | hallucination |
| e3feb8358a79 | 2026 | 2026-02-20 | ADJ12214919+ADJ12214918 | noland |
| aa4d6ea964a8 | 2025 | 2025-11-03 | ADJ15406376 | hallucination |
| ccb78c2f2ca7 | 2024 | 2024-09-30 | ADJ7850534+ADJ7904327 | hallucination |
