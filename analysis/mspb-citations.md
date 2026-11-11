# How often do the MSPB's own decisions deal with fabricated citations, and does the tracker have them? Result of census 1.0.0

Status: **graded on 11 November 2026** against the plan frozen in commit `306535b` ([PLAN](mspb-citations/PLAN.md)). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `79655cf2...`). No amendment was needed. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions of a federal agency, not legal advice.

## Short answer

**Once in 3,567 decisions.** The census read every Board decision that the Merit Systems Protection Board (MSPB) issued from 1 January 2024 to 9 November 2026, as listed in its own public decision manifests: **3,567 decisions, all readable** (35 precedential, 3,532 nonprecedential). Exactly **one** says that a filing cited cases that do not exist: a nonprecedential final order of **29 October 2026** (docket CH-0752-25-1198-I-1, a removal appeal against the Department of Homeland Security, appellant pro se). The AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) has **no row whose court is the MSPB**, so it does not have this one either (also checked by searching the live database on 11 November 2026).

The decision mentions no AI term. The fabricated citations were in the **appellant's** petition for review. The **agency** asked the Board to dismiss the petition as a sanction for "having cited several cases that do not exist". The Board denied the petition on the merits and **dismissed the agency's sanction motion as moot**. So the Board said nothing about the citations themselves and imposed no sanction.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | the frame holds at least 5 fabricated-citation decisions | **failed** | 1 |
| P2 | fewer than half of them mention an AI term | not testable (n = 1, needs 3) | 0 of 1 |
| P3 | a higher share from 2025-07-01 on than before | not testable (n = 1) | before: 0 of 2,600; from: 1 of 967 |
| P4 | at least two thirds have a pro se appellant | not testable (n = 1) | 1 of 1 |
| P5 | pro se share higher than among all decisions | not testable (n = 1) | 1 of 1 vs 2,076 of 3,567 (58.2%) |
| P6 | fewer than half mention sanctions or 5 C.F.R. 1201.43 | not testable (n = 1) | 1 of 1 (see correction below) |
| P7 | at least half are final orders | not testable (n = 1) | 1 of 1 |
| P8 | the database has no row whose court is the MSPB (not blind) | **held** | 0 court rows; 2 Federal Circuit rows review MSPB cases |

Decisions by year: 2024: 2,308; 2025: 373; 2026 (to 9 November): 886. The 2025 dip is the Board's lost quorum: it had a single member from 10 April to 27 October 2025 ([MSPB FAQ, 14 Nov 2025](https://www.mspb.gov/FAQs%20Absence%20of%20Board%20Quorum%2011-14-25.pdf)), and one member cannot issue Board decisions. By kind: 2,796 final orders, 446 remand orders, 290 other orders, 35 opinions and orders. Full outputs are in [results/](mspb-citations/results/): `results.md`, `results.json`, `rows.csv` (one row per decision: an id anyone can recompute from the manifest, docket, date, agency, kind, PDF SHA-256 and flags), `manifests.json` and `sources.json`. As the plan promised, appellants' names, file names, texts and excerpts are not published.

## What reading the matched passages showed (corrections; the verdicts stay as graded)

- **The one fabricated-citation match is true.** The passage describes the appellant's petition-for-review filing, as the agency characterised it in its motion. The Board did not make its own finding about the citations.
- **Its `action` flag is a false positive in substance.** The word "sanction" appears because the agency asked for one. The Board dismissed that request as moot. Corrected: the Board took action on fabricated citations in **0 of 1** decisions.
- **The one AI mention is not about fabricated citations.** In a final order of 29 May 2024 (docket DC-3443-22-0296-I-1), the appellant had attached "a series of communications with an artificial intelligence system which assisted him in drafting his pleading". The Board said he had not explained their relevance and that they gave no basis to disturb the initial decision. No citation was said to be fake.
- **Misses could only be checked from outside.** The job kept the text of flagged decisions only, so unflagged decisions could not be re-read with wider wording. A web search for MSPB orders that call citations nonexistent or fictitious found none beyond this one. The database's two MSPB-related rows are Federal Circuit decisions (15 December 2025 and 8 October 2026) about fabricated citations in briefs filed **in the Federal Circuit**, not at the Board.

## What this means

1. At the Board level, fabricated citations are rare: 1 in 3,567 decisions. The caption marks the appellant as pro se in 58% of these decisions, so the low count is not because few appellants represent themselves.
2. The tracker misses the Board's one case, but the miss looks like the ones MV2 found at the Tax Court: an **incidental remark**. The fabricated citations come up only in a motion that the Board mooted. The decision never rules on them, so a search for rulings on AI or sanctions would not surface it.
3. The fuller picture likely sits one level down, in administrative judges' initial decisions, which the MSPB does not publish in bulk. A Board decision is only made when someone petitions for review.

This is the third archive in MV2's series that checks a tribunal's own records against the tracker. The others are the [FLRA](flra-ai-citations.md) (1 AI decision in 310, tracked) and the [Tax Court](tax-court-citations.md) (3 of 4 fabricated-citation documents tracked). A census of BIA and Attorney General precedent decisions is [pre-registered](bia-citations/PLAN.md).

## Limits

Board decisions only: no initial decisions, no orders of administrative judges, no compliance or arbitration documents outside the manifests. The phrases are a fixed list. A decision that says "we could not locate" a case, or describes fake authority in other words, would be missed, and the job did not keep texts to check this. One decision cannot support rates or trends. This counts what decisions say. It does not judge any appellant, representative, agency or Board member, and it is not legal advice.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `cac050d5...` (2,197,049 bytes), fetched 2026-11-11T02:34:38Z. MSPB decisions read from mspb.gov, one request every 3 seconds, 2026-11-11 02:35-06:17 UTC. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
