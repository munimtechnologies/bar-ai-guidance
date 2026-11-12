# BIA / A.G. precedent fabricated-citation census 1.0.0: results

Frame: every decision listed on EOIR's pages for volumes 28, 29, 30 of I&N Dec. Information about public decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name.

Sources: `{"plan_commit": {"sha": "837f7e19b582d1350bb91ac16b33eabddb886629", "date": "2026-11-11T03:47:48Z"}, "census_commit": {"sha": "837f7e19b582d1350bb91ac16b33eabddb886629", "date": "2026-11-11T03:47:48Z"}, "database": {"url": "https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv", "fetched_at": "2026-11-12T12:51:07Z", "bytes": 2200099, "sha256": "f828f95f0698eb881e7d5f23566333424446f462c280b095da72681a621f999f", "licence": "CC BY 4.0, AI Hallucination Cases Database, Damien Charlotin"}, "eoir": {"pages": ["https://www.justice.gov/eoir/volume-28", "https://www.justice.gov/eoir/volume-29", "https://www.justice.gov/eoir/volume-30"], "failed": 0, "in_frame": 288, "built_at": "2026-11-12T12:51:28Z"}}`

Counts: `{"in_frame": 288, "readable": 288, "fake_cite": 1, "ai_mention": 1, "ai_citation": 1, "pm2540": 0, "discipline": 7, "fetch_status": {"ok": 288}, "by_issuer": {"AAO": 1, "AG": 19, "BIA": 267, "DIR": 1}, "by_year": {"2020": {"readable": 20, "fake_cite": 0, "ai_mention": 0, "discipline": 1}, "2021": {"readable": 29, "fake_cite": 0, "ai_mention": 0, "discipline": 0}, "2022": {"readable": 23, "fake_cite": 0, "ai_mention": 0, "discipline": 1}, "2023": {"readable": 13, "fake_cite": 0, "ai_mention": 0, "discipline": 0}, "2024": {"readable": 14, "fake_cite": 0, "ai_mention": 0, "discipline": 0}, "2025": {"readable": 70, "fake_cite": 0, "ai_mention": 0, "discipline": 1}, "2026": {"readable": 119, "fake_cite": 1, "ai_mention": 1, "discipline": 4}}, "same_pdf_for_several_ids": {"de5acaeda7eb": [4037, 4038]}}`

| prediction | text | verdict | detail |
|---|---|---|---|
| P1 | Matter of Sethi, 30 I&N Dec. 112, is readable and has a fabricated-citation phrase (not blind) | held | `{"found": true, "readable": true}` |
| P2 | 1 to 3 readable decisions in the frame have a fabricated-citation phrase | held | `{"n": 1}` |
| P3 | no readable decision cites EOIR Policy Memorandum 25-40 | held | `{"n": 0}` |
| P4 | every fabricated-citation decision cites the EOIR practitioner-discipline rules (8 C.F.R. 1003.101-1003.109 or 1292.3) | held | `{"n": 1, "k": 1}` |
| P5 | every fabricated-citation decision is a practitioner-discipline decision | held | `{"n": 1, "k": 1}` |
| P6 | fewer than 5 readable decisions mention an AI term | held | `{"n": 1}` |
| P7 | the AI Hallucination Cases Database has no row whose court is an EOIR body (not blind) | held | `{"court_rows": 0, "pfr_rows": 3}` |
| P8 | no fabricated-citation decision in the frame is in the database (not blind for Sethi) | held | `{"n": 1, "cited_in_db": [], "eoir_court_rows": 0}` |

## Listing pages

| volume | entries | no citation | no link | ID gaps | error |
|---|---|---|---|---|---|
| 28 | 100 | 0 | 0 | [] |  |
| 29 | 155 | 0 | 0 | [] |  |
| 30 | 33 | 0 | 0 | [4248] |  |

## Decisions with a fabricated-citation phrase

| id | citation | issuer | year | flags |
|---|---|---|---|---|
| 4254 | 30 I&N Dec. 112 | BIA | 2026 | fake_cite, ai_mention, ai_citation, disc_reg, discipline |
