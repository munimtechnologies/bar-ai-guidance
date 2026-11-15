# Pre-registration: fabricated citations in U.S. Employees' Compensation Appeals Board decisions, 2024-2026 (census 1.0.0)

Status: **frozen before the code reads any ECAB decision text.** Written 2026-11-15 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a federal workers' compensation appeals board, not legal advice.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Done so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md), the [MSPB](../mspb-citations.md), the [BIA](../bia-citations.md), the [New York tax tribunals](../nydta-citations.md), the [California OTA](../ota-citations.md) and the [California WCAB](../wcab-citations.md). The WCAB census found 10 decisions in 7 workers' compensation cases that say a filing cited authority that does not exist, none of them in the tracker, and 5 of the 7 began with filings by employers' or insurers' lawyers.

The Employees' Compensation Appeals Board (ECAB) of the U.S. Department of Labor hears appeals from federal employees whose claims under the Federal Employees' Compensation Act (FECA) were decided by the Office of Workers' Compensation Programs (OWCP). Unlike the WCAB, the other side is a federal agency, appellants may appear without a lawyer, and the Board names appellants by initials only. It posts every decision and order on public month pages (https://www.dol.gov/agencies/ecab/decisions). If AI-drafted filings by people without lawyers reach this Board, its decisions are where it would show. The questions:

1. How many ECAB decisions and orders from January 2024 to October 2026 say that a filing cited authority that does not exist, and how many mention AI?
2. Are those filings by appellants without a lawyer?
3. Does the tracker list them?

## What was seen before freezing, stated plainly

- **No decision text was read.** We read the index page and two month pages (January 2026: 72 entries, 26 of them orders; June 2025: 82 entries, 11 orders) through a summarizing web reader. Each month page has one table, "Docket No. / Date Issued / Parties"; the docket number links to a PDF under `/sites/dolgov/files/ecab/decisions/<year>/<MON>/` named like `23-0094.pdf`, `23-0477_O.pdf` (an order) or `22-0251_Reissue.pdf`; dates are written like "June 11, 2025"; parties are initials and the employing agency. The index lists 12 month pages for 2024, 11 for 2025 (it says there were no decisions in October 2025) and 10 for 2026 (January to October). dol.gov's robots.txt (read 15 Nov 2026) does not block these paths and sets no crawl delay.
- **The tracker:** its live search returned 0 matches for "ECAB", "Employees' Compensation" and "FECA" on 15 Nov 2026. So the first half of **P1 is not blind.**
- A web search on 15 Nov 2026 found no report of an ECAB decision about fabricated or AI-generated citations. We do not know whether any exist; P2 to P7 are guesses.

## Frame

- **Listing:** every PDF linked from the decision tables of the month pages that the index lists for 2024, 2025 and 2026, as listed when the job runs; decisions, orders and reissued decisions alike (the `kind` column tells them apart). Rows repeating an earlier row's PDF link are skipped and counted. A document's year is the year of the month page that lists it.
- **Stops, before any decision is fetched:** the index or any month page fails (after retries); the index lists fewer than 30 month pages for 2024-2026; the frame holds fewer than 1,500 or more than 3,600 documents; or more than 40 rows have no readable date. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 documents in a row fail. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's WCAB, OTA and USPTO censuses, unchanged. "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, portion, passage, page or parenthetical. Also "cited ... do(es) not exist", "cases/citations/... (that) do not exist", "a case/citation/... that does not exist", and "locate the cases ... cited".
- `ai_mention`: the WCAB census's AI terms, unchanged (artificial intelligence; generative AI; AI-generated, -drafted, -assisted, -based, -powered, AI tool or platform; "(AI)"; ChatGPT; ChatSOC; large language model). `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- New for ECAB, because its decisions discuss medical evidence: `hallucination` (any word starting "hallucinat") is recorded but **does not flag** a decision, since psychiatric evidence uses the word. `hallucinated_cite` flags "hallucinat..." within 300 characters of a citation word (citation, cites, cited, citing, case law, authority, precedent, quotation). `not_located` flags "unable to / could not / cannot locate, find, identify or verify (the) ... case(s), citation(s), decision(s), authority, precedent(s) or case law". `pro_se`: the words "Appellant, pro se" (the Board's appearances line); recorded, does not flag.
- `in_db`: a tracker row that mentions ECAB or the Employees' Compensation Appeals Board anywhere quotes the document's docket number.

## Predictions (fixed now)

- **P1 (first half not blind):** the tracker, as downloaded by the job, has no row whose court is ECAB, and it lists none of the documents with a fabricated-citation phrase.
- **P2:** at least one document in the frame has a fabricated-citation phrase.
- **P3:** at most five documents have one.
- **P4:** no 2024 document has one.
- **P5:** fewer than ten documents mention an AI term.
- **P6:** at least half of the readable decisions (orders excluded) record the appellant as pro se.
- **P7:** every document with a fabricated-citation phrase records the appellant as pro se.
- **P8 (method check):** at least 98% of the documents in the frame are readable.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read the full text of every flagged document. They will report false matches, and cases the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record who filed the document (appellant, representative, OWCP/Director), what the Board did about it, whether it named AI, and whether the tracker lists it (also checked by hand on the tracker's live search).

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (the index and month pages' sizes, SHA-256 and parser checks) and `sources.json`. `rows.csv` has one row per document: a row id (the first 12 hex digits of SHA-256 of the lower-cased PDF link), year and month of the listing page, date issued, docket number, kind, fetch status, text length, the PDF's SHA-256, `in_db`, and the flags. The Board already identifies appellants only by initials; the parties column is still left out of every public file. Texts and excerpts stay private to the job.

## Limits

Decisions are what the Board chose to write about. A fake citation that a decision does not mention is invisible here, and OWCP's own decisions are not on these pages. A decision that describes a fake citation in other words would be missed; the review looks for missed cases only among flagged texts. A null result would say only that the Board's decisions do not describe such filings in these words. The census counts what decisions say. It does not judge any appellant, representative, agency or official, and it is not legal advice.
