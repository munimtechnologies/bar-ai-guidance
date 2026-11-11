# FLRA archive AI-citation census 1.0.1: results

Frame: every FLRA Authority decision issued 2022-01-01 to 2026-11-10, read from flra.gov. Coverage check against the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Information about public decisions, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "012f7707b96948d60685c8e1ac342bb0cb29b24a", "date": "2026-11-10T11:44:11Z"}, "amendment_commit": {"sha": "fddf8cb4ac6ac595d54ee2ac473b76056221f66e", "date": "2026-11-10T14:54:43Z"}, "census_commit": {"sha": "fddf8cb4ac6ac595d54ee2ac473b76056221f66e", "date": "2026-11-10T14:54:43Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-10T20:38:26Z", "bytes": 2197049, "sha256": "cac050d540f21e708436491720383f019184eaa9babf3e452a0c8e542ebc77b1", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "flra": {"listing": "https://www.flra.gov/decisions/authority-decisions?order=issuance_date&sort=desc&page=0", "listing_pages": 32, "in_frame": 310, "without_html_link": 0, "undated_listing_rows": 0, "reached_start": true, "built_at": "2026-11-10T20:40:56Z"}}`

Counts: `{"in_frame": 310, "readable": 310, "ai_mention": 1, "ai_citation": 1, "by_year": {"2022": {"readable": 115, "ai_mention": 0, "ai_citation": 0}, "2023": {"readable": 73, "ai_mention": 0, "ai_citation": 0}, "2024": {"readable": 60, "ai_mention": 0, "ai_citation": 0}, "2025": {"readable": 25, "ai_mention": 0, "ai_citation": 0}, "2026": {"readable": 37, "ai_mention": 1, "ai_citation": 1}}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | the FLRA frame holds at least 2 AI-citation decisions | failed | `{"n": 1}` |
| P2 | fewer than half of the AI-citation decisions are in the AI Hallucination Cases Database | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| P3 | at most half of the AI-citation decisions name a sanction, referral, reprimand or disqualification | not testable | `{"n": 1, "k": 0, "share": 0.0}` |
| P4 | at least half of the AI-citation decisions cite another agency or adjudicator within 2,500 characters of an AI term | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| P5 | method check: no AI-citation decision is dated before 2023-01-01 | held | `{"n_before": 0, "ids": []}` |
| P6 | Mata v. Avianca is cited in fewer than half of the AI-citation decisions | not testable | `{"n": 1, "k": 0, "share": 0.0}` |
| P7 | a larger share of 2026 decisions than of 2023 decisions mention an AI term | not testable | `{"2023": {"n": 73, "k": 0, "share": 0.0}, "2026": {"n": 37, "k": 1, "share": 0.027}, "all": {"n": 310, "k": 1, "share": 0.003}}` |

## AI-citation decisions

| citation | date | in database | flags |
|---|---|---|---|
| [74 FLRA No. 87](https://www.flra.gov/decisions/v74/74-87) | 2026-10-21 | True | ai_mention, ai_citation, own_rule, other_body |
