# Pre-registration: fabricated or unlocatable citations in U.S. Department of Labor appeal and ALJ decisions (hand search 1.0.0)

Status: **frozen before any search of the Labor Department's decision search and before any flagged decision is read.** Written 2026-11-16 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions, not legal advice. Text CC BY 4.0.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the [AI Hallucination Cases Database](https://www.damiencharlotin.com/hallucinations/) (Damien Charlotin, CC BY 4.0). So far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md), the [MSPB](../mspb-citations.md), the [BIA](../bia-citations.md), the [New York tax tribunals](../nydta-citations.md), the [California OTA](../ota-citations.md), the [California WCAB](../wcab-citations.md), an [EEOC hand search](../eeoc-citations.md) and a [hand-checked list](../agency-hand-list.md). A census of the Labor Department's Employees' Compensation Appeals Board (ECAB) is [pre-registered](../ecab-citations/PLAN.md) and waiting for compute.

The Labor Department has three more layers of adjudicators that the series has not looked at:

- the **Office of Administrative Law Judges (OALJ)**, which hears whistleblower (SOX, AIR21, STAA, FRSA and others), black lung, longshore, immigration-labor and wage cases;
- the **Administrative Review Board (ARB)**, which reviews ALJ decisions in whistleblower, wage and immigration-labor cases. Its monthly case lists show about 3 to 12 decisions a month in 2026 (October 2026: 3; September: 12; August: 5);
- the **Benefits Review Board (BRB)**, which reviews longshore and black lung decisions.

Whistleblower complainants before the OALJ and the ARB often appear without a lawyer, which the series' earlier results suggest is where unchecked citations show up.

### Tracker baseline, 16 November 2026 (before any DOL search)

The tracker's live search (database last updated 16 November 2026) returned:

| Query | Rows | Any DOL adjudicator? |
|---|---|---|
| Department of Labor | 1 (74 FLRA No. 87, an FLRA decision) | No |
| Review Board | 7 (Canadian review boards, one Pennsylvania unemployment case) | No |
| ARB | 24 (words such as "Arbitration", "Harbor"; one Calgary Assessment Review Board row) | No |
| OALJ | 0 | No |
| Black Lung | 0 | No |

So the tracker has no row for any Labor Department ALJ or appeals board.

### A second tracker

On 16 November 2026 we also read the page of a second, smaller public tracker, [Legal AI Governance's AI Hallucination Cases Tracker](https://legalaigovernance.com/tracker/cases/) (790 cases; it covers sanctions, warnings, bar referrals and similar outcomes). Its page text, read through a summarizing web reader, lists rows from November 2026 back to December 2025 and then ends, so older rows were not checked. In those rows a text search found no row for the EEOC, MSPB, FLRA, NLRB, WCAB, California PERB, California OTA, ECAB or any DOL adjudicator. Its tribunal rows are GAO bid-protest decisions (6), the U.S. Tax Court (2), the ASBCA (2) and one USPTO discipline matter. It does not list *American Backflow* (NLRB) or 74 FLRA No. 87, which the larger tracker does. So the gap the series describes is not specific to one tracker. Limits: no export was available, and a reader-based text search can miss a row.

## Why a hand search, not a census

The Labor Department's full-text search for appeal decisions, [Search DOL Appeals](https://searchappeals.dol.gov/), covers the ARB, BRB, ECAB and OALJ. It is a JavaScript application, so the agents' plain web reader cannot use it, and the OALJ's own keyword search page refuses automated readers (HTTP 403 on 16 November 2026). searchappeals.dol.gov's robots.txt has no rules. MV2's browser agent will therefore run a fixed list of searches by hand, as a person would, and read the flagged decisions one at a time. A crawler census of the ARB and BRB archives (dol.gov's robots.txt allows the decision files) may follow later as a separate pre-registered plan.

One decision was seen before this plan was written: the ARB's decision in ARB No. 2026-0008 (a SOX whistleblower case), which a web search showed is about a complainant's use of AI (an ALJ had allowed AI use as a reasonable accommodation, then limited it). Its text has not been read. It will be read in full and reported, but it does not count toward D1 to D6 unless the search itself returns it.

## Method (fixed now)

1. **Collections:** ARB, BRB and OALJ decisions. ECAB results are written into the search log as a recall cross-check for the queued ECAB census but are not read here.
2. **Window:** decisions dated 1 January 2024 or later. If the search has a date filter it is used; if not, results are scanned until they are older than 2024 or for the first 50 results, whichever comes first.
3. **Queries, in this order:** "do not exist"; "does not exist" citation; nonexistent case; "non-existent"; fictitious citation; fabricated citation; "unable to locate" case; "could not locate" decision; hallucination; "artificial intelligence"; ChatGPT; "generative AI".
4. **Flag rule:** a result is flagged if its snippet or title suggests that a filing cited a case, decision, regulation or quotation that does not exist, could not be found, or does not say what it was cited for. Snippets about missing evidence, records or documents are not flagged.
5. **Reading:** up to 8 flagged decisions, newest first, read in full in an ordinary browser. For each: board or office, docket number, decision date, whether the filer had a lawyer (only "attorney", "non-attorney representative" or "self-represented"), the adjudicator's words about the citations, any words about AI, and what was done (warning, strike, sanction, nothing). If more than 8 are flagged, the rest are listed and read in a later step.
6. **Names:** we give docket numbers, the board, the date and the employer or respondent. We leave out the names of individual complainants, claimants, lawyers, representatives and judges.
7. **Tracker check:** on the day of the write-up, each flagged decision is searched in the tracker by docket number, employer name and the short names above.

## Predictions (fixed now)

- **D1:** at least one ARB, BRB or OALJ decision dated 2024 or later says, in the adjudicator's own words, that a filing cited authority that does not exist or could not be found.
- **D2:** among the decisions read in full that meet D1, more come from OALJ judges than from the ARB and BRB together.
- **D3:** at most one third of the decisions that meet D1 mention AI.
- **D4:** in more than half of the decisions that meet D1, the filer was self-represented.
- **D5:** none of the decisions that meet D1 imposes a money sanction.
- **D6:** the tracker lists none of the decisions that meet D1 on the day of the write-up.
- **D7 (not blind; ARB No. 2026-0008 only):** the decision is about limits on a party's use of AI, and it does not find that the party cited authority that does not exist.

D2 to D6 are "not testable" if no decision meets D1. Each prediction will be reported as held, failed or not testable, with the search log (query, result count, flagged items) published in full.

## Limits

A keyword search of one search engine, not a census. Decisions describe only what the adjudicator chose to write about; a bad citation a decision does not mention stays invisible, and one described in other words, or ranked low, may be missed. Small counts say nothing about how common the problem is. The search counts what decisions say. It does not judge any worker, claimant, complainant, lawyer, representative, employer or official.
