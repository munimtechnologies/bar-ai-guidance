# Pre-registration: fabricated citations in NLRB Board decisions, 2024-2026 (census 1.0.0)

Status: **frozen before the code reads any decision in the frame except the four named below.** Written 2026-11-13 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a federal labor board, not legal advice.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Done so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md), the [MSPB](../mspb-citations.md), the [BIA](../bia-citations.md) and the [New York tax tribunals](../nydta-citations.md) (a control with none). Queued: the [California WCAB](../wcab-citations/PLAN.md), the [California OTA](../ota-citations/PLAN.md), [USPTO discipline](../uspto-oed-citations/PLAN.md) and [California PERB](../perb-citations/PLAN.md).

In *American Backflow & Fire Prevention, Inc.*, 375 NLRB No. 31 (25 Aug 2026), the National Labor Relations Board said fabricated "ghost citations" "are not an isolated incident before the Board". MV2's [hand-checked list](../agency-hand-list.md) holds three Board decisions on citations that do not exist. The questions:

1. Over every Board decision the NLRB lists from 1 January 2024 to the day the job runs, how many say a party cited authority that does not exist, and how many mention AI?
2. Did it start only in 2026?
3. Does the Board now cite *American Backflow* when it meets the problem again, and how often does it refer anyone for discipline?
4. Does the tracker list them?

## What was seen before freezing, stated plainly

- *American Backflow* (375 NLRB No. 31), read in full on 12 Nov 2026.
- *Rivas Painting, Inc.*, 374 NLRB No. 30 (28 Jan 2026), read in full on 13 Nov 2026: a one-page order denying a request for review, whose footnote 1 says the request "cites to cases that, as far as we can determine, do not exist". No AI, no referral.
- A sizing probe (`handcheck-nlrb-v1`, 13 Nov 2026) read the first 19 pages of the Board-decisions listing (380 rows, volumes 372 to 375; by listed date 34 in 2023, 155 in 2024, 8 in 2025, 183 in 2026; every row had a document id and a case number) and fetched the three newest listed decisions through the mirror, to check the mirror covers them. **One of those three was a hit:** *Pepperjacks of Annapolis Junction LLC d/b/a Notch 8 Brewery*, 375 NLRB No. 65 (30 Oct 2026), footnote 1 (a pro se respondent's exceptions brief included "case citations that do not exist"; the Board cites *American Backflow*; no AI named, no referral). The other two (375 NLRB Nos. 67 and 68) had no such phrase.
- A web search on 13 Nov 2026 for *Pepperjacks* found the NLRB Edge newsletter's summary of 2 Nov 2026, which mentions its nonexistent cases. Apart from the 11 Nov 2026 searches that led to *American Backflow* and *Rivas*, no search was made for other NLRB decisions on the subject.
- **So P1 is a recall check, not a blind prediction; P2 to P8 were set knowing these three exist.** No other decision text in the frame was read.
- The database's live search on 13 Nov 2026 (last updated 12 Nov) has one NLRB row, *American Backflow*; searches for Pepperjacks and Rivas return nothing. **P5 is therefore not blind.**

## Frame

- **Listing:** the NLRB's public Board-decisions listing (`https://www.nlrb.gov/cases-decisions/decisions/board-decisions?page=N`, newest first, 20 rows a page; allowed by nlrb.gov's robots.txt), read from page 0 until a page whose dated rows are all before **1 January 2024**. A row counts if it carries an "NNN NLRB No. N" citation. The frame is every citation whose listed date is on or after 1 January 2024. A citation already seen is skipped and counted.
- **Stops, before any decision is fetched:** the listing fails, has no rows on page 0, or does not finish within 30 pages; the frame holds fewer than 250 or more than 600 decisions; or more than 10 frame rows lack a document id. Any change goes in a published amendment before any text is read.
- **Fetching:** each decision's PDF by its NLRB document id from **nlrbresearch.com's mirror** (`/pdfs/<id>.pdf`, allowed by that site's robots.txt; `apps.nlrb.gov/link/` is disallowed by its robots.txt and is never requested). One request at a time, **5 seconds apart**, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 decisions in a row fail. **Readable:** a PDF whose text is 300+ characters once whitespace is collapsed. Published Board decisions usually carry the administrative law judge's decision as an attachment; the whole PDF is read, and the review says which part a phrase is in.

## Definitions (as coded in census.py)

- `fake_series`: the fabricated-citation patterns of MV2's WCAB, OTA, USPTO and PERB censuses, unchanged.
- `fake_nlrb`: **one addition for this census**, needed because *Rivas Painting*'s wording ("cites to cases that, as far as we can determine, do not exist") escapes the series patterns: an authority word (case, citation, cites, authority, decision, quotation, precedent, case law) followed within 100 characters, before any `.`, `;` or `:`, by "do/does/did not (appear to) exist".
- `fake_cite` = `fake_series` or `fake_nlrb`. Both are reported, so the series count stays comparable.
- Patterns run on the text as extracted and on a copy with line-break hyphens joined ("cita- tions" to "citations"); a flag is set if either matches.
- `ai_mention`, `ai_citation` (an AI term within 2,000 characters of a fabricated-citation phrase), `hallucination`: as in the series. `backflow`: "American Backflow". `ghost`: "ghost citation(s)". Recorded, not flags: `referral` ("Investigating Officer" or "102.177"), `pro_se` ("pro se").
- `in_db`: any database row quotes the decision's "VVV NLRB No. S" citation, or an NLRB-court row's case name contains a distinctive word (5+ letters, not boilerplate) of the listed case name.

## Predictions (fixed now)

- **P1 (recall check, not blind):** 374 NLRB No. 30, 375 NLRB No. 31 and 375 NLRB No. 65 are in the frame and each has a fabricated-citation phrase.
- **P2:** 4 to 10 decisions in the frame have a fabricated-citation phrase (so at least one the agents do not yet know of).
- **P3:** no decision dated before 1 January 2026 has one.
- **P4:** fewer than half of the decisions with a fabricated-citation phrase mention an AI term.
- **P5 (not blind):** the database, as downloaded by the job, has at most one NLRB-court row, and at least two decisions with a fabricated-citation phrase are not in it.
- **P6:** at least two decisions with a fabricated-citation phrase, other than *American Backflow* itself, mention *American Backflow* (not blind for one: *Pepperjacks* does).
- **P7 (method check):** at least 97% of the frame's decisions have a readable text from the mirror.
- **P8:** at most one decision with a fabricated-citation phrase mentions the Investigating Officer or Sec. 102.177.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged decision. They will report false matches (for example an ALJ's or the Board's own wording about something else), and cases the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record who filed the bad citations (lawyer, non-attorney representative, pro se party, union, employer, General Counsel), whether the phrase is in the Board's decision or the ALJ's, what the Board did (a note, a warning, a referral), whether it named AI, and whether the tracker lists it (also checked by hand on its live search).

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (pages read, their SHA-256, counts by year and volume) and `sources.json`. `rows.csv` has one row per decision: citation, listed date, case number, NLRB document id, fetch status, page count, text length, the PDF's SHA-256, `in_db`, whether it was one of the three known decisions, and the flags. **Citations, case numbers and document ids are public identifiers and are published; listed case names, texts and excerpts are not** (they stay private to the job), even though the NLRB publishes them: some parties are individuals.

## Limits

Board decisions are what the Board chose to write; administrative law judges' decisions that no one excepted to, and unpublished Board orders, are not in this listing. The listing shows only 8 decisions dated 2025, so the 2025 count says little. The mirror is a third-party copy of the NLRB's documents, checked by document id; a decision it lacks is counted as unreadable, not guessed. A decision that describes a fake citation in other words would be missed; the review looks for missed cases only among flagged texts. The census counts what decisions say. It does not judge any worker, union, employer, representative or official, and it is not legal advice.
