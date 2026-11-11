# MSPB fabricated-citation census 1.0.0: results

Frame: every Board decision issued 2024-01-01 to 2026-11-09 in the MSPB's public decision listings. Information about public decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "306535b192545537fb2776406e752e9ceecc1361", "date": "2026-11-10T20:37:17Z"}, "census_commit": {"sha": "306535b192545537fb2776406e752e9ceecc1361", "date": "2026-11-10T20:37:17Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-11T02:34:38Z", "bytes": 2197049, "sha256": "cac050d540f21e708436491720383f019184eaa9babf3e452a0c8e542ebc77b1", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "mspb": {"base": "https://www.mspb.gov/decisions/", "manifests": 6, "main_failed": 0, "in_frame": 3567, "built_at": "2026-11-11T02:34:58Z"}}`

Counts: `{"in_frame": 3567, "readable": 3567, "fake_cite": 1, "ai_mention": 1, "ai_citation": 0, "pro_se_readable": 2076, "precedential_readable": 35, "fetch_status": {"ok": 3567}, "by_kind": {"final": 2796, "opinion": 35, "other_order": 290, "remand": 446}, "by_year": {"2024": {"readable": 2308, "fake_cite": 0, "ai_mention": 1, "ai_citation": 0}, "2025": {"readable": 373, "fake_cite": 0, "ai_mention": 0, "ai_citation": 0}, "2026": {"readable": 886, "fake_cite": 1, "ai_mention": 0, "ai_citation": 0}}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | the frame holds at least 5 readable decisions with a fabricated-citation phrase | failed | `{"n": 1}` |
| P2 | fewer than half of the fabricated-citation decisions mention an AI term | not testable | `{"n": 1, "k": 0, "share": 0.0}` |
| P3 | the share of readable decisions with a fabricated-citation phrase is higher from 2025-07-01 on than before | not testable | `{"early": {"n": 2600, "k": 0, "share": 0.0}, "late": {"n": 967, "k": 1, "share": 0.001}}` |
| P4 | at least two thirds of the fabricated-citation decisions have a pro se appellant | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| P5 | the pro se share among fabricated-citation decisions is higher than among all readable decisions | not testable | `{"fake_cite": {"n": 1, "k": 1, "share": 1.0}, "readable": {"n": 3567, "k": 2076, "share": 0.582}}` |
| P6 | fewer than half of the fabricated-citation decisions mention sanctions or 5 C.F.R. 1201.43 | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| P7 | at least half of the fabricated-citation decisions are final orders | not testable | `{"n": 1, "k": 1, "share": 1.0}` |
| P8 | the AI Hallucination Cases Database has no row whose court is the MSPB | held | `{"court_rows": 0, "review_rows": 2}` |

## Manifests

| manifest | rows | in window | earliest | latest | error |
|---|---|---|---|---|---|
| nonprecedential/NonPrecedentialDecisions_Manifest.json | 10805 | 3521 | 2007-12-27 | 2026-11-09 |  |
| precedential/PrecedentialDecisions_Manifest.json | 108 | 35 | 2022-03-24 | 2026-10-22 |  |
| nonprecedential/NonPrecedentialDecisions_Manifest_Table.json | 5385 | 3425 | 2018-11-30 | 2026-09-17 |  |
| nonprecedential/NonPrecedentialDecisions_Manifest-updmar2025.json | 10691 | 3407 | 2007-12-27 | 2026-09-17 |  |
| precedential/PrecedentialDecisions_Manifest_Table.json | 106 | 33 | 2022-03-24 | 2026-09-01 |  |
| precedential/PrecedentialDecisions_Manifest_updMar2025.json | 16816 | 33 | 0891-01-01 | 2026-09-01 |  |

## Decisions with a fabricated-citation phrase

| id | docket | date | kind | agency | flags |
|---|---|---|---|---|---|
| d59c9d3211c9 | CH-0752-25-1198-I-1 | 2026-10-29 | final | Department of Homeland Security | fake_cite, pro_se, action |
