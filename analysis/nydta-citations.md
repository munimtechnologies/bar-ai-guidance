# Do New York's tax tribunals' own documents deal with fabricated citations? Result of census 1.0.0: none in 917

Status: **graded on 12 November 2026** against the plan frozen in commit `460b47e` ([PLAN](nydta-citations/PLAN.md)). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `c8429dae...`). No amendment was needed. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public documents of a state tax tribunal, not legal or tax advice.

## Short answer

**None.** The census read every document listed on the four public listing pages of New York's Division of Tax Appeals and Tax Appeals Tribunal (www.dta.ny.gov) on 12 November 2026: **917 documents, 916 readable** (582 administrative law judge determinations, 93 ALJ orders, 229 Tribunal decisions and 12 Tribunal orders; one ALJ order's link returned 404). **Not one** says that a filing cited authorities that do not exist, and none uses any word starting "hallucinat". Most of the documents date from 2022 to 2026 (764 of 916), the period in which such passages became common in U.S. courts and in the U.S. Tax Court.

Only **one** document mentions an AI term at all, and it has nothing to do with citations. An ALJ determination of 2026 quotes a company's answer to an auditor's information request, which said that its products related to "operating and applications software, artificial intelligence, computer modeling and simulation" and other emerging technologies as described in a New York statute (Public Authorities Law § 3102-e). The agents read the passage and the text around it.

The AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) had **no row** for either body when the job downloaded it, and with nothing found there was nothing for it to miss.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | 0 to 3 documents have a fabricated-citation phrase | **held** | 0 |
| P2 | none dated before 2025 has one | **held** | 0 |
| P3 | at most one has an AI term within 2,000 characters of such a phrase | **held** | 0 |
| P4 | fewer than 10 readable documents mention an AI term | **held** | 1 |
| P5 | no Tribunal decision or order has a fabricated-citation phrase | **held** | 0 |
| P6 | the database has no New York tax-tribunal row, and no flagged document is in it (not blind) | not testable (no flagged document) | 0 rows |
| P7 | method check: at least 98% of the frame readable | **held** | 916 of 917 (99.9%) |
| P8 | listing check: at most 2% of the frame without a readable year (not blind) | **held** | 1 of 917 |

Readable documents by year: 2013-2015: 3; 2018: 34; 2019: 35; 2020: 25; 2021: 54; 2022: 155; 2023: 193; 2024: 155; 2025: 158; 2026: 103; one with no readable year. The listings repeat a DTA number in 134 rows (for example when a determination and the Tribunal's decision on exception carry the same number) and one link repeated an earlier row's file, so it was skipped, as the plan said. Full outputs are in [results/](nydta-citations/results/): `results.md`, `results.json`, `rows.csv` (one row per document: an id anyone can recompute from the listing, page, DTA number, year, month, fetch status, length, file SHA-256 and flags), `listing.json` (each listing page's size, SHA-256 and parser checks) and `sources.json`. As the plan promised, petitioners' names, file names, texts and excerpts are not published.

## What this means

1. **A real zero, not a gap in the tracker.** Every prediction that could be tested held, and the predictions expected few or none. In these two bodies the problem the series looks for does not show up in what the judges and the Tribunal write, at least not in words like "nonexistent", "fictitious" or "fabricated" citations.
2. **Why it may differ from the U.S. Tax Court**, which had four such documents since 2023 ([result](tax-court-citations.md)). These are guesses, not findings: many New York petitioners may be represented by accountants or lawyers who handle many such cases, the records are built largely on audit files rather than briefs, and an ALJ may simply decide a case without remarking on a bad citation. The census cannot tell these apart.
3. **The series now has a control.** So far the tribunals' own archives have shown fabricated-citation decisions at the U.S. Tax Court (4), the MSPB (1 in 3,567), California's PERB (4 in 11 months, from its monthly summaries), California's Workers' Compensation Appeals Board (6 decisions found by hand) and the NLRB (2). New York's tax tribunals add a large archive with none. The places where the problem shows up are not just "every tribunal": the next censuses (California's Office of Tax Appeals, the WCAB's full 2024-2026 archive, the BIA and the USPTO's discipline records) will show whether it clusters in particular kinds of tribunal.

## Limits

The census reads only what the listing pages show when the job runs, and those pages describe themselves as covering about the past year although they list more. A fabricated citation that a document does not mention is invisible here, and one described in other words would be missed. The job kept texts only for flagged documents, so unflagged documents could not be re-read with wider wording. It counts what documents say. It does not judge any taxpayer, representative or official, and it is not legal or tax advice.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `86fd2101...` (2,194,006 bytes), fetched 2026-11-12T08:39:44Z. Documents read from www.dta.ny.gov, one request every 3 seconds, 2026-11-12 08:39-09:34 UTC. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
