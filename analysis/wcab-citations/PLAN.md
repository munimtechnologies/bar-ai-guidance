# Pre-registration: fabricated citations in California Workers' Compensation Appeals Board panel decisions, 2024-2026 (census 1.0.0)

Status: **frozen before the code reads any decision text in the frame other than the six documents named below.** Written 2026-11-12 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a state workers' compensation tribunal, not legal advice.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Done so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md) and the [MSPB](../mspb-citations.md). Queued: the [BIA](../bia-citations/PLAN.md), the [USPTO's discipline archive](../uspto-oed-citations/PLAN.md), the [California OTA](../ota-citations/PLAN.md) and the [New York tax tribunals](../nydta-citations/PLAN.md).

California's Workers' Compensation Appeals Board (WCAB) decides petitions for reconsideration from its trial judges. Under Labor Code section 5813 it can sanction a party or a lawyer up to $2,500 for bad-faith filings. It posts its panel decisions on one public page (https://www.dir.ca.gov/wcab/wcab-Decisions.htm), in year tables that held 1,088 (2024), 1,118 (2025) and 915 (2026, to date) PDF links on 12 Nov 2026. MV2's [hand-checked list](../agency-hand-list.md) found four WCAB cases from 2025-2026 in which the Board said a filing cited authority that does not exist. In one of them the lawyer said the citations came from a legal publisher's own AI research tool. On 11 Nov 2026 the tracker had **no row whose court is the WCAB**. No count of such decisions exists that we could find (searched 2026-11-12; firm blogs and trade press discuss individual cases such as *Sedano*). The questions:

1. How many WCAB panel decisions from 2024 to November 2026 say that a filing cited authority that does not exist, and how many of them mention AI?
2. Is it growing (2024 vs 2025 vs 2026)? How often does the Board reach for its sanctions statute?
3. Does the tracker list them?

## What was seen before freezing, stated plainly

- **The listing.** MV2's hand-check job (`handcheck-wcab-v1`, 12 Nov 2026) read the listing page once: 5,863 PDF links in six year tables (2021-2026). Each row has a date (M/D/YYYY) and the applicant's name linked to a PDF under `/wcab/Panel-Decisions-<year>/`; the file name carries the ADJ case number(s). robots.txt (read 12 Nov 2026) does not block these folders and sets no crawl delay.
- **Six documents in the frame were read in full** for the [hand-checked list](../agency-hand-list.md): ADJ17550375 (2025), ADJ17889413 (2025 and 2026), ADJ12865802 (2025) and ADJ16902178 (2025 and 2026). All six describe fabricated or nonexistent citations. Two mention AI (ADJ17889413 both times; ADJ12865802 raises it as a question). So **P1 is a recall check, not a blind prediction,** and P2 to P8 were set knowing these six exist.
- Press and firm reports (searched 12 Nov 2026) say WCAB judges are issuing notices of intent to sanction for "hallucinated" pleadings, without counts.
- **The database (downloaded 2026-11-11) has no WCAB row,** so **P7 is not blind**: it checks that nothing has changed.

## Frame

- **Listing:** every table row on https://www.dir.ca.gov/wcab/wcab-Decisions.htm whose PDF sits in the 2024, 2025 or 2026 folder (or, with no link, whose listed date falls in those years), as listed when the job runs. Rows repeating an earlier row's PDF link are skipped and counted.
- **Stops, before any decision is fetched:** the page fails; the frame holds fewer than 2,600 or more than 3,800 decisions; fewer than three tables carry the expected "Date / Panel Decision" header; or more than 20 rows in the frame have no readable date or no link. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 decisions in a row fail. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's OTA and USPTO censuses, unchanged. "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, portion, passage, page or parenthetical. Also "cited ... do(es) not exist", "cases/citations/... (that) do not exist", "a case/citation/... that does not exist", and "locate the cases ... cited".
- `ai_mention`: artificial intelligence; generative AI; AI-generated, -drafted, -assisted, -based, -powered, AI tool or platform; "(AI)"; ChatGPT; **ChatSOC** (added for this census: the tool named in ADJ17889413); large language model. `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- `hallucination`: any word starting "hallucinat". `noland`: the word "Noland" (the 2025 Court of Appeal sanctions case). `sedano`: the word "Sedano" (the WCAB's 2025 sanctions decision, reported at 90 Cal.Comp.Cases 1190).
- `lc5813`: the number 5813 (Labor Code section 5813). `nit`: "notice of intent(ion) to (impose/issue/order) sanction(s)". These two are recorded for every decision but do not by themselves flag a decision.
- `in_db`: any database row quotes one of the decision's ADJ numbers, or a row whose court is the WCAB has a case name containing a distinctive word of the applicant's name. Names are used only for this check and are never published.
- A **case** is the first ADJ number in the file name; a decision and a later decision in the same case count as two decisions and one case.

## Predictions (fixed now)

- **P1 (recall check, not blind):** all six hand-checked decisions are in the frame and have a fabricated-citation phrase.
- **P2:** 10 to 40 decisions in the frame have a fabricated-citation phrase.
- **P3:** at most one 2024 decision has one.
- **P4:** more 2026 decisions than 2025 decisions have one (2026 covers about ten and a half months).
- **P5:** fewer than half of the fabricated-citation decisions mention an AI term. (A guess: two of the six hand-checked documents name AI; the Board's stated position in *Sedano* is that the misstatement matters more than how it was made.)
- **P6:** at least three quarters of the fabricated-citation decisions cite Labor Code section 5813.
- **P7 (not blind):** the database, as downloaded by the job, has no WCAB-court row, and at least three cases with a fabricated-citation decision are not in it.
- **P8:** at least two fabricated-citation decisions other than the six hand-checked ones mention *Sedano*.
- **P9 (method check):** at least 98% of the decisions in the frame are readable.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged decision. They will report false matches, and decisions the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record who filed the document (applicant's attorney, defendant, lien claimant, unrepresented party), what the Board did (notice of intent, sanction amount, referral), whether it named AI, and whether the tracker lists it (also checked by hand on the tracker's live search).

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (the page's size, SHA-256, row counts and parser checks) and `sources.json`. `rows.csv` has one row per decision: a row id (the first 12 hex digits of SHA-256 of `year|ADJ numbers|date`, lower case, with `|n` added for the n-th repeat), folder year, listed date, fetch status, text length, the PDF's SHA-256, `in_db`, whether it was hand-checked, and the flags. **ADJ numbers are published only for flagged decisions. Applicants' names and file names (which carry them) are never published,** even though the WCAB publishes them: these are injured workers. Texts and excerpts stay private to the job.

## Limits

Panel decisions are what the Board chose to write about. A fake citation that a decision does not mention is invisible here, and trial-level orders by workers' compensation judges are not on this page. A decision that describes a fake citation in other words would be missed; the review looks for missed cases only among flagged texts. The census counts what decisions say. It does not judge any worker, lawyer, representative, company or official, and it is not legal advice.
