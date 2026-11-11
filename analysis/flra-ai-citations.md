# How many FLRA decisions deal with AI-fabricated citations, and does the tracker have them? Result of census 1.0.1

Status: **graded on 10 November 2026** against the plan frozen in commit `012f770` ([PLAN](flra-ai-citations/PLAN.md)) and its listing-parser-only [amendment 1](flra-ai-citations/AMENDMENT-1.md) (commit `fddf8cb`, census 1.0.1). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `74e25825...`). Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions, not legal advice.

## Short answer

**One.** The census read all **310** Federal Labor Relations Authority decisions issued from 1 January 2022 to 10 November 2026, taken from the FLRA's own decisions list. All 310 were readable. Exactly **one** mentions AI: [74 FLRA No. 87](https://www.flra.gov/decisions/v74/74-87) (21 October 2026), and the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) already lists it. For the FLRA, then, the tracker misses nothing. The prediction that it would (P2) could not be tested on one decision. The FLRA's first AI-citation decision is also its only one so far.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | the frame holds at least 2 AI-citation decisions | **failed** | 1 |
| P2 | fewer than half of them are in the database | not testable (n = 1, needs 3) | 1 of 1 is |
| P3 | at most half name a sanction, referral, reprimand or disqualification | not testable (n = 1) | 0 of 1 |
| P4 | at least half cite another agency or adjudicator near an AI term | not testable (n = 1) | 1 of 1 |
| P5 | method check: no AI-citation decision is dated before 2023-01-01 | **held** | 0 |
| P6 | Mata v. Avianca is cited in fewer than half | not testable (n = 1) | 0 of 1 |
| P7 | a larger share of 2026 decisions than of 2023 decisions mention an AI term | not testable (2026 has 37 readable decisions, needs 50) | 2023: 0 of 73; 2026: 1 of 37 |

Decisions by year: 2022: 115, 2023: 73, 2024: 60, 2025: 25, 2026 (to 10 Nov): 37. Full outputs are in [results/](flra-ai-citations/results/): `results.md`, `results.json`, `rows.csv` (one row per decision: citation, reporter cite, date, link, page SHA-256 and flags), `sources.json` and `status.json`. Page texts stay private to the job.

## What reading the matched passages showed (corrections; the verdicts stay as graded)

- **74 FLRA No. 87 is a true match.** The Authority found that 22 of the 29 footnotes in an agency's exceptions brief, and 35 of its 42 legal or record citations, were "fictitious, erroneous, or irrelevant". It said the agency "may have used a generative artificial-intelligence (AI) tool". It added that nothing prohibits parties from using AI tools, cautioned them to verify AI-generated material, and imposed no sanction. Its authority for the caution is borrowed: footnote 53 cites the NLRB's *American Backflow & Fire Prevention, Inc.*, 375 NLRB No. 31 (2026), and the other footnotes cite GAO, the Department of Education and the USPTO (details in MV2's [agency AI-authority census](agency-ai-authority.md)).
- **Its `own_rule` flag is real but not about AI.** It points to 5 CFR 2425.6(b) and (e)(1), the FLRA's rules on what an exceptions brief must explain and when an argument is denied for failing to support it. The decision uses those rules to deny the exception on its merits. It does not use them as an AI rule. The FLRA has none, consistent with MV2's [CFR census](cfr-ai-census.md).
- **The `in_db` column has one false positive that affects no verdict.** Under the frozen code, any decision dated within 7 days of the database's single FLRA row is marked `in_db`. So [74 FLRA No. 88](https://www.flra.gov/decisions/v74/74-88) (26 October 2026, no AI mention) also carries `in_db = True` and the same database row id. Only AI-citation decisions enter the predictions, so nothing graded changes. Read `in_db` only for 74 FLRA No. 87.
- **No other decision in the 310 matched an AI term**, so there were no other AI excerpts to read. A decision that discusses fabricated citations without any AI word would not appear here. That is a stated limit of the frame.

## What this means

1. For the FLRA, AI-fabricated citations are a single event, not a trend: one decision in almost five years of the Authority's decisions, and the tracker has it.
2. MV2's earlier finding was that the main tracker holds very few agency decisions. Here that reflects how rare such decisions are at the FLRA, not missing coverage. The [Tax Court census](tax-court-citations.md), run the same day on the court's own search, found one document the tracker lacks. The MSPB census ([plan](mspb-citations/PLAN.md)) is queued.
3. The FLRA's one decision still matters for its reasoning: an agency tribunal with no AI rule of its own borrowed four other bodies' statements.

## Limits

The frame is the FLRA's own list of Authority decisions. It does not include administrative law judge decisions, regional director decisions, Federal Service Impasses Panel decisions, or unpublished orders. The AI terms are a fixed list, and a decision about fake citations that never uses an AI word is outside this count. One decision cannot support rates. This counts what decisions say. It does not judge any party or representative, and it is not legal advice.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `cac050d5...` (2,197,049 bytes), fetched 2026-11-10T20:38:26Z. FLRA decisions read from flra.gov, one request every 3 seconds. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
