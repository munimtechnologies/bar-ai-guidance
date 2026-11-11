# Pre-registration: fabricated citations in the New York Division of Tax Appeals' and Tax Appeals Tribunal's published documents (census 1.0.0)

Status: **frozen before the code reads any document text in the frame.** Written 2026-11-11 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs and the standard library to read `.docx` files). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public documents of a state tax tribunal, not legal or tax advice.

## Why

MV2's censuses compare tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Graded so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md) and the [MSPB](../mspb-citations.md). Queued: the [BIA](../bia-citations/PLAN.md), the [USPTO's discipline archive](../uspto-oed-citations/PLAN.md) and California's [Office of Tax Appeals](../ota-citations/PLAN.md), the first state tribunal. This census is the **second state tribunal** and a check on the first: New York's Division of Tax Appeals (administrative law judges' determinations and orders) and its Tax Appeals Tribunal (decisions and orders on exceptions). Both hear disputes with the Department of Taxation and Finance, and many petitioners represent themselves.

On 11 Nov 2026 the tracker's CSV had **no row for either body**. Its New York rows are all courts (state Supreme, Civil, Family and appellate courts, and the federal districts), and no row's court or case name mentions the Division of Tax Appeals or the Tax Appeals Tribunal. The questions:

1. How many of these documents say that a party cited authorities that do not exist, and how many mention AI?
2. Is the pattern seen in courts and the U.S. Tax Court visible in a state tax tribunal with no reported case?
3. Does the tracker list any of them?

## Prior art (searched 2026-11-11)

Web searches for New York Division of Tax Appeals or Tax Appeals Tribunal documents about nonexistent, fictitious or hallucinated citations found only New York **court** decisions (for example the Appellate Division's *Landberg v City of New York*, 2026 NY Slip Op 03935, and *Deutsche Bank Natl. Trust Co. v LeTennier*, 2026 NY Slip Op 00040) and U.S. Tax Court cases. We found no report of such a document from either New York tax body, no count across them and no check of the tracker's coverage of them.

## What was seen before freezing, stated plainly

- **Listing metadata only.** The agents read summaries of the four listing pages and of the site's robots.txt (which allows everything and sets no crawl delay) and sitemap. Each listing is one table with the columns Name (the petitioner, linked to a PDF or occasionally a `.docx`), Number (one or more six-digit DTA numbers) and Date ("Month D, YYYY"). The summaries reported about 580 ALJ determinations (4 Nov 2021 to 29 Oct 2026), about 94 ALJ orders (18 Nov 2021 to 29 Oct 2026), about 230 Tribunal decisions (8 May 2018 to 22 Oct 2026) and 12 Tribunal orders (22 Aug 2013 to 18 Dec 2025). They also reported date typos ("May 29, 2925", "Apil 6, 2023", "October 9. 2025"), irregular file names, and a few rows whose link does not match the listed number or repeats another row's file. **So P8 is not blind.** **No document text in the frame was read for this study.**
- **The database (downloaded 2026-11-11, 02:34 UTC) has no row for either body,** so **P6 is not blind**: it checks that nothing has changed.

## Frame

- **Listings:** every table row after the header row on four pages: https://www.dta.ny.gov/determinations/ (ALJ determinations), https://www.dta.ny.gov/determinations/orders.htm (ALJ orders), https://www.dta.ny.gov/decisions/ (Tribunal decisions) and https://www.dta.ny.gov/decisions/orders.htm (Tribunal orders), as listed when the job runs. Columns are read by header. A row's links are those in its Name and Number cells, tried in order until one returns a PDF or a `.docx`.
- **No date window:** the frame is whatever the four pages list. A row whose first link was already taken by an earlier row is skipped and counted. Duplicate DTA numbers are kept and counted.
- **Dates:** "Month D, YYYY", with misspelt months matched to the closest month name. A year outside 2013 to 2026 counts as unreadable. Predictions that use years leave such rows out (see P2).
- **Stops, before any document is fetched:** a listing page fails; the frame holds fewer than 650 or more than 1,400 documents; a page lacks the header row; more than 10 rows have no six-digit DTA number; or more than 10 rows have no link. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 documents in a row fail. **Readable:** a file whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's USPTO and OTA censuses, unchanged. "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, portion, passage, page or parenthetical. Also "cited ... do(es) not exist", "cases/citations/... (that) do not exist", "a case/citation/... that does not exist", and "locate the cases ... cited".
- `ai_mention`: artificial intelligence; generative AI; AI-generated, -drafted, -assisted, -based, -powered, AI tool or platform; "(AI)"; ChatGPT; large language model. `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase. `hallucination`: any word starting "hallucinat".
- `in_db`: any database row quotes one of the document's DTA numbers after "DTA" (for example "DTA No. 851687"), or a row whose court or case name names the Division of Tax Appeals or the Tax Appeals Tribunal has a case name containing a distinctive word of the petitioner's name. Petitioners' names are used only for this check and are never published.
- Tribunal documents: rows from the two `decisions/` pages. The others are ALJ documents.

## Predictions (fixed now)

- **P1:** 0 to 3 documents in the frame have a fabricated-citation phrase. (MV2's federal censuses found such passages rare in agency decisions: 1 in 3,567 MSPB Board decisions.)
- **P2:** no document dated before 2025 has one. (Not testable if a fabricated-citation document has no readable year and none is dated before 2025.)
- **P3:** at most one document has an AI term within 2,000 characters of a fabricated-citation phrase.
- **P4:** fewer than 10 readable documents mention an AI term at all.
- **P5:** no Tax Appeals Tribunal decision or order has a fabricated-citation phrase.
- **P6 (not blind):** the database, as downloaded by the job, has no New York tax-tribunal row, and no fabricated-citation document is in it. (Not testable if there is no fabricated-citation document.)
- **P7 (method check):** at least 98% of the documents in the frame are readable.
- **P8 (listing check, not blind):** at most 2% of the documents in the frame have no readable year.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged document. They will report false matches, and documents the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record whether the petitioner was represented, what the ALJ or Tribunal did, whether it named AI, and whether the tracker lists it (also checked by hand on the tracker's live search). If California's OTA census has graded by then, the write-up will set the two state tribunals' rates side by side, descriptively; that comparison is not a prediction.

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (each page's size, SHA-256, row counts and parser checks) and `sources.json`. `rows.csv` has one row per document: a row id (the first 12 hex digits of SHA-256 of `page|number|date as listed`, lower case, with `|n` added for the n-th repeat), page (det, detord, dec or decord), first DTA number, year, month, fetch status, text length, the file's SHA-256, `in_db` and the flags. **Petitioners' names and file names are not published,** even though the Division publishes them. Texts and excerpts stay private to the job.

## Limits

These documents are what the judges and the Tribunal chose to write; a fake citation that a document does not mention is invisible here, and one described in other words would be missed. The review looks for missed cases only among flagged texts. The listings may change before the job runs (the pages describe themselves as covering the past year, though they list more). The census counts what documents say. It does not judge any taxpayer, representative or official, and it is not legal or tax advice.
