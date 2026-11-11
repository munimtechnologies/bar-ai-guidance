# Pre-registration: fabricated citations in the USPTO's practitioner-discipline archive, 2023-2026 (census 1.0.0)

Status: **frozen before the code reads any decision text in the frame.** Written 2026-11-11 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a federal agency, not legal advice.

## Why

MV2's earlier censuses compared tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). The [FLRA](../flra-ai-citations.md), the [Tax Court](../tax-court-citations.md) and the [MSPB](../mspb-citations.md) are done. The pattern so far: the tracker covers tribunals' main rulings well. What it misses are incidental remarks, records that cannot be searched, and **follow-on discipline**, the later proceeding in which a regulator disciplines the lawyer. The USPTO's Office of Enrollment and Discipline (OED) disciplines patent and trademark practitioners and publishes its decisions in an [electronic FOIA reading room](https://foiadocuments.uspto.gov/oed/). It is the federal archive of follow-on discipline that is easiest to read in full. In April 2024 the USPTO also issued its own AI guidance for practitioners ("Guidance on Use of Artificial Intelligence-Based Tools in Practice Before the United States Patent and Trademark Office", 89 FR 25609), so the archive can show whether a regulator with its own AI guidance cites it when it disciplines. That is the question of MV2's [agency AI-authority census](../agency-ai-authority.md). The questions:

1. How many OED decisions since 2023 deal with fabricated or nonexistent citations, and how many mention AI?
2. Which rules do they rely on: the competence rule (37 C.F.R. 11.101), the signature and certification rule (11.18), misconduct (11.804), and the USPTO's own 2024 AI guidance?
3. Does the tracker list them?

## Prior art (searched 2026-11-11)

Practitioner press (IPWatchdog, 28 Aug 2026; IP Update / National Law Review, Sept 2026; Woods Rogers, Sept 2026; Patently-O's "OED Orders from Summer 2026") covers *In re Mitchell*, D2026-16, a public reprimand of 27 July 2026 over AI-generated citations to nonexistent parts of a patent's record. A practitioner blog (IPethics & INsights) discusses D2025-13, a public reprimand of 6 March 2025 over a Trademark Trial and Appeal Board brief that cited nonexistent case law, with CLE on AI ordered. We found no count across the OED archive and no check of the tracker's coverage of it.

## What was seen before freezing, stated plainly

- **Listing metadata only.** The agents read a summary of the reading-room listing page: one table with the columns Proceeding Number, Decision Related Text, Respondent Name, Decision Type and Decision Date; PDF links in the first two columns; types Discipline, Reinstatement, Technical, Moral, Legal and Other. The summary's rough count for 2023-2026 was about 160 rows (about 140 of them Discipline). robots.txt allows everything. No decision text in the frame was read for this study.
- **Two decisions are not blind.** From the press and blog summaries above: D2026-16 involves AI-generated citations to nonexistent parts of a patent's specification and record, with violations including competence and misconduct. D2025-13 describes "citation to non-existent case law" and refers to 37 C.F.R. 11.18. So **P1 and P2 check the patterns, not the world,** and P3, P6 and P9 were set knowing these two exist.
- **The database (downloaded 2026-11-10) has exactly one row whose court is the USPTO**: the D2026-16 matter. A search of its CSV for the D2025-13 respondent found no row. So **P8 and P9 are not blind**: they check that nothing has changed.

## Frame

- **Listing:** every table row on https://foiadocuments.uspto.gov/oed/, read by header (the column order is taken from the header row if one is found). A row's links are those in its Proceeding Number and Decision Related Text cells, tried in order until one returns a PDF.
- **Window:** Decision Date from 2023-01-01 to 2026-11-10. All decision types are kept and reported by type. Rows whose first link was already taken by an earlier row are skipped and counted.
- **Stops, before any decision is fetched:** the page fails; the window holds fewer than 100 or more than 300 rows; more than 5 rows with a 2022-or-later proceeding number (D2022-... onward) have no readable date; or more than 10 rows in the window have no link. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 decisions in a row fail. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed. Scanned decisions with no text layer count as unreadable and are reported.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's BIA census, widened for patent records. "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, **portion, passage, page or parenthetical**. Also "cited ... do(es) not exist", "cases/citations/quotations/portions/passages/pages (that) do not exist", "a case/citation/quotation/portion/passage/page that does not exist", and "locate the cases ... cited".
- `ai_mention`: artificial intelligence; generative AI; AI-generated, -drafted, -assisted, -based, -powered, AI tool or platform; "(AI)"; ChatGPT; large language model. "AI" may appear as "Al" only in the compound forms. "LLM" is left out (a law degree). `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- `guidance`: "89 FR 25609" (or "Fed. Reg.", pin cites 25,609-25,619) or the guidance's title. `r11_18`, `r11_101`, `r11_804`: "11.18", "11.101", "11.804" anywhere in the text.
- `in_db`: a database row whose court is the USPTO, PTAB, TTAB or OED names the respondent's surname, or any database row quotes the proceeding number. Respondents' names are used only for this check and are never published.

## Predictions (fixed now)

- **P1 (pattern check, not blind):** a readable decision of D2026-16 has both a fabricated-citation phrase and an AI term.
- **P2 (pattern check, not blind):** a readable decision of D2025-13 has a fabricated-citation phrase.
- **P3:** 2 to 4 proceedings in the frame have a readable decision with a fabricated-citation phrase.
- **P4:** fewer than 5 proceedings in the frame have a readable decision that mentions an AI term.
- **P5:** at least one fabricated-citation decision cites the USPTO's April 2024 AI guidance. Not testable if there are none.
- **P6 (not blind for D2026-16):** every fabricated-citation decision cites the competence rule, 37 C.F.R. 11.101.
- **P7:** at least half of the fabricated-citation decisions cite 37 C.F.R. 11.18.
- **P8 (not blind):** the database, as downloaded by the job, has exactly one USPTO-court row, and it matches a readable decision in the frame.
- **P9 (not blind for D2025-13):** at least one fabricated-citation proceeding in the frame is not in the database.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged decision. They will report false matches, and decisions the patterns missed, separately, with corrected counts beside the graded ones; the verdicts stay as graded. They will also say, for each fabricated-citation decision, which tribunal or court first caught the citations and whether the tracker lists that first decision.

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (page size, SHA-256, row counts, date and link checks) and `sources.json`. `rows.csv` has one row per decision: a row id (the first 12 hex digits of SHA-256 of `proceeding|date|decision text`, lower case), proceeding number, decision text (e.g. "Final Order"), type, date, fetch status, text length, the PDF's SHA-256, `in_db` and the flags. **Respondents' names and file names (which carry them) are not published,** even though the USPTO publishes them. Texts and excerpts stay private to the job.

## Limits

The reading room holds what OED chose to publish. Settled matters may be described only briefly, and some decisions are scanned images. A decision about fake citations that uses other words would be missed, and the review will look for this only among flagged texts. The census counts what decisions say. It does not judge any practitioner or official, and it is not legal advice.
