# Do the BIA's and the Attorney General's precedent decisions deal with fabricated citations? Result of census 1.0.0: one in 288

Status: **graded on 12 November 2026** against the plan frozen in commit `837f7e1` ([PLAN](bia-citations/PLAN.md)). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `67b2cd4a...`). No amendment was needed. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions of a federal agency, not legal advice.

## Short answer

**One.** The census read every decision listed on the Justice Department's Executive Office for Immigration Review (EOIR) pages for volumes 28, 29 and 30 of *Administrative Decisions under Immigration and Nationality Laws* (I&N Dec.): **288 precedent decisions from 2020 to 2026, all 288 readable** (267 by the Board of Immigration Appeals, 19 by the Attorney General, one by USCIS's Administrative Appeals Office and one by the EOIR Director). Only **one** says that a filing cited authority that does not exist, and it is the only one of the 288 that mentions AI at all:

- ***Matter of Sethi*, 30 I&N Dec. 112 (BIA 2026)**, Interim Decision #4254, decided 1 October 2026. This is reciprocal discipline. On 3 June 2026 the Ninth Circuit suspended an attorney from practice before it for six months after a brief with AI-generated errors, including a nonexistent case, and false statements to the court about his AI use (*Malkeet Lnu v. Blanche*, 177 F.4th 1014 (9th Cir. 2026)). The Board suspends him from practice before the Board, the Immigration Courts and DHS for the same six months, effective 13 June 2026. It relies on EOIR's practitioner-discipline rules (8 C.F.R. 1003.103 and 1003.106) and does not mention EOIR's own AI memo.

**No decision cites EOIR Policy Memorandum 25-40**, EOIR's August 2025 memo on generative AI. The AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) had **no row naming an EOIR body as its court** when the job downloaded it, and **no row for *Matter of Sethi***. By hand we found only a different 2025 federal criminal case with the same surname. It **does** have the Ninth Circuit order that *Sethi* follows (*Malkeet Lnu v. Blanche*, 2026-06-03).

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | *Matter of Sethi* is readable and has a fabricated-citation phrase (pattern check, not blind) | **held** | found |
| P2 | 1 to 3 readable decisions have a fabricated-citation phrase | **held** | 1 |
| P3 | no readable decision cites EOIR Policy Memorandum 25-40 | **held** | 0 |
| P4 | every fabricated-citation decision cites the practitioner-discipline rules | **held** | 1 of 1 |
| P5 | every fabricated-citation decision is a practitioner-discipline decision | **held** | 1 of 1 |
| P6 | fewer than 5 readable decisions mention an AI term | **held** | 1 |
| P7 | the database has no row whose court is an EOIR body (not blind) | **held** | 0 rows |
| P8 | no fabricated-citation decision in the frame is in the database (not blind for *Sethi*) | **held** | 0 of 1 |

All eight held. P1, P7 and P8 were checks rather than forecasts, as the plan said.

Readable decisions by year: 2020: 20; 2021: 29; 2022: 23; 2023: 13; 2024: 14; 2025: 70; 2026: 119. The 2026 volume is the biggest by far, yet it holds only one such decision. Interim Decision 4248 has no entry on the volume 30 page, and two IDs (4037 and 4038) link to the same PDF; both are recorded in [results/](bia-citations/results/).

## Hand check (as promised in the plan; the verdicts stay as graded)

The agents read every excerpt and the opening pages and orders of every flagged decision.

- **Fabricated citations:** *Sethi* is a true match. The excerpts quote the Ninth Circuit's findings that the brief cited a nonexistent case, which the attorney first called a "typographical error". The other six decisions the job kept had no fabricated-citation passage under wider wording (fabricated, fictitious, nonexistent, "does not exist", hallucinated, frivolous, artificial). **Corrected count: 1, unchanged.**
- **The `discipline` flag (not graded) caught 7 decisions; 2 were false matches.** 28 I&N Dec. 169 (2020) and 29 I&N Dec. 757 (2026) are ineffective-assistance motions to reopen that discuss the bar-complaint requirement of *Matter of Lozada*, not practitioner discipline. The 5 real practitioner-discipline precedents are 28 I&N Dec. 653 (2022, disbarment for practising while suspended), 29 I&N Dec. 240 (2025, practising while suspended; disbarment sought), 29 I&N Dec. 850 (2026, reinstatement denied), 30 I&N Dec. 59 (2026, reciprocal one-year suspension) and *Sethi*. **Corrected count: 5 discipline precedents, one of them about AI.**

## What this means

1. **Another quiet follow-on.** The tracker has the court ruling (*Lnu v. Blanche*) but not the agency discipline that followed it. The Tax Court addendum and the PERB, WCAB and NLRB hand lists show the same pattern ([Tax Court](tax-court-citations.md), [hand list](agency-hand-list.md)): the decisions the database misses are usually short follow-on orders from bodies outside the court system.
2. **The AI memo is not the authority.** As in MV2's [agency AI-authority census](agency-ai-authority.md), the tribunal acts under its general practitioner-conduct rules, not its own AI guidance. *Sethi* never cites PM 25-40.
3. **A small number from a selected slice.** The BIA publishes only a few dozen of its tens of thousands of yearly decisions as precedents, and immigration judges' decisions are not published at all. One in 288 says nothing about how often fabricated citations reach immigration courts. It shows only what the Board has chosen to make precedent, and its first AI precedent is a discipline case, not a ruling on a respondent's filing.

## Limits

The census reads only the precedents EOIR lists. Regular expressions can miss unusual wording. The job kept full texts only for flagged decisions, so unflagged ones could not be re-read with wider wording. It counts what decisions say. It does not judge any respondent, practitioner or Board member, and it is not legal advice. As the plan promised, `rows.csv` has citations and EOIR's own links but no party names. *Sethi* is named here because the plan and its public commentary already name it.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `f828f95f...` (2,200,099 bytes), fetched 2026-11-12T12:51:07Z. Decisions read from www.justice.gov, one request every 10 seconds, 2026-11-12 12:51-13:40 UTC. Full outputs: [results/](bia-citations/results/) (`results.md`, `results.json`, `rows.csv`, `listing.json`, `sources.json`, `status.json`). Text of this write-up: CC BY 4.0. Code: Apache-2.0.
