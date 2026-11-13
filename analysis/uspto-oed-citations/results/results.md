# USPTO OED discipline-archive fabricated-citation census 1.0.0: results

Frame: every decision in the USPTO's OED FOIA reading room dated 2023-01-01 to 2026-11-10. Information about public decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "200007c20495c85f66c938e9b023e784953c9b0f", "date": "2026-11-11T07:04:27Z"}, "census_commit": {"sha": "200007c20495c85f66c938e9b023e784953c9b0f", "date": "2026-11-11T07:04:27Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-13T09:45:55Z", "bytes": 2200099, "sha256": "f828f95f0698eb881e7d5f23566333424446f462c280b095da72681a621f999f", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "oed": {"page": "https://foiadocuments.uspto.gov/oed/", "failed": 0, "in_frame": 160, "built_at": "2026-11-13T09:45:56Z"}}`

Listing: `{"url": "https://foiadocuments.uspto.gov/oed/", "bytes": 207826, "sha256": "e27afc1c9862dfa7cfc6c19e15144bd39f9bd0fb561824ca4f69c2214905d3cb", "table_rows": 942, "entries": 941, "header_found": true, "bad_date": 0, "bad_date_new": 0, "in_window": 160, "same_link_skipped": 0, "no_link_in_window": 0}`

Counts: `{"in_frame": 160, "readable": 133, "fake_cite": 1, "fake_cite_proceedings": 1, "ai_mention": 1, "ai_mention_proceedings": 1, "ai_citation": 1, "guidance": 0, "fetch_status": {"ok": 160}, "by_type": {"Discipline": 140, "Moral": 1, "Reinstatement": 18, "Technical": 1}, "by_year": {"2023": {"readable": 38, "fake_cite": 0, "ai_mention": 0}, "2024": {"readable": 35, "fake_cite": 0, "ai_mention": 0}, "2025": {"readable": 41, "fake_cite": 1, "ai_mention": 1}, "2026": {"readable": 19, "fake_cite": 0, "ai_mention": 0}}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | D2026-16 is readable and has both a fabricated-citation phrase and an AI term (pattern check, not blind) | not testable | `{"rows": 1, "readable": 0}` |
| P2 | D2025-13 is readable and has a fabricated-citation phrase (pattern check, not blind) | held | `{"rows": 1, "readable": 1}` |
| P3 | 2 to 4 proceedings in the frame have a readable decision with a fabricated-citation phrase | failed | `{"n": 1}` |
| P4 | fewer than 5 proceedings in the frame have a readable decision that mentions an AI term | held | `{"n": 1}` |
| P5 | at least one fabricated-citation decision cites the USPTO's April 2024 AI guidance | failed | `{"n": 1, "k": 0}` |
| P6 | every fabricated-citation decision cites the competence rule, 37 C.F.R. 11.101 (not blind for D2026-16) | failed | `{"n": 1, "k": 0}` |
| P7 | at least half of the fabricated-citation decisions cite 37 C.F.R. 11.18 (signature and certification) | held | `{"n": 1, "k": 1}` |
| P8 | the database has exactly one USPTO row, and it matches a readable decision in the frame (not blind) | failed | `{"uspto_rows": 1, "matched_proceedings": []}` |
| P9 | at least one fabricated-citation proceeding in the frame is not in the database (not blind for D2025-13) | held | `{"n": 1, "missing": ["D2025-13"]}` |

## Decisions with a fabricated-citation phrase

| row | proceeding | decision | type | date | in database | flags |
|---|---|---|---|---|---|---|
| dfb2d3986490 | D2025-13 | Final Order | Discipline | 2025-03-06 | False | fake_cite, ai_mention, ai_citation, r11_18, r11_804 |

## Decisions that mention an AI term

| row | proceeding | date | flags |
|---|---|---|---|
| dfb2d3986490 | D2025-13 | 2025-03-06 | fake_cite, ai_mention, ai_citation, r11_18, r11_804 |
