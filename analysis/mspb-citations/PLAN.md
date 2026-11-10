# Pre-registration: fabricated citations in the Merit Systems Protection Board's own decisions, 2024-2026 (census 1.0.0)

Status: **frozen before the code reads any decision text in the frame.** Written 2026-11-10 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py` and `test_run_job.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a federal agency, not legal advice.

## Why

MV2's earlier studies found that the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database, holds few decisions of agency tribunals ([agency AI-authority census](../agency-ai-authority.md); a Tax Court census is pre-registered in [tax-court-citations](../tax-court-citations/PLAN.md)). The Merit Systems Protection Board (MSPB) hears federal employees' appeals, and many appellants file without a lawyer. It publishes every Board decision as a PDF and lists them in public JSON manifests behind https://www.mspb.gov/decisions/. Its own full-text search is switched off ("full text search is not currently available"). So nobody can currently search the Board's decisions for fabricated citations, and the tracker lists none. The questions:

1. How many Board decisions issued since 2024 say that a filing cited cases or authorities that are fictitious or do not exist, and is that share growing?
2. Do those decisions mention AI, and do they involve appellants without a lawyer?
3. Does the Board act on them (sanctions under 5 C.F.R. 1201.43), or just note them?

## Prior art (searched 2026-11-10)

Web searches for MSPB decisions on fabricated or AI-generated citations found only federal court decisions and a practitioner blog warning MSPB appellants about AI tools. An open daily copy of the MSPB decision listing exists (abigailhaddad/mspb-decisions, on Hugging Face). It holds metadata only, no decision text, and does no citation analysis. We found no count of fabricated-citation passages in MSPB decisions.

## What was seen before freezing, stated plainly

- **Manifest metadata only.** The agents read parts of the nonprecedential and precedential listing manifests: field names, dates, docket numbers, file names. `DOCUMENT_CONTENT` is empty in every row read, so no decision text came with them. One decision PDF was fetched to check that the download works. Its text is compressed and was not read.
- From the manifest sizes, the frame should hold roughly 3,000 to 3,500 decisions (about 135 rows per 100,000 characters; September 2024 sits about 1.1 million characters in, April 2024 about 2.0 million).
- **The database (downloaded 2026-11-10) has no row whose court is the MSPB.** It has two Federal Circuit rows that review MSPB decisions (2025-12-15 and 2026-10-08). The text of one says the MSPB had flagged a passage as possibly AI-generated. So **P8 is not blind**: it checks that nothing changed. P2 was set knowing that at least one MSPB proceeding raised AI.

## Frame

- **Manifests:** the two main listings (`nonprecedential/NonPrecedentialDecisions_Manifest.json` and `precedential/PrecedentialDecisions_Manifest.json`) and four older ones that may be stale or missing (`..._Manifest_Table.json`, and the `updmar2025` versions). The job stops if a main manifest cannot be read. Rows are merged by collection and file name (case ignored). The first manifest read wins.
- **Window:** issued 2024-01-01 to 2026-11-09, by the manifest's `ISSUED_DATE`. Rows with an unreadable date are counted and left out.
- **Stops, before any PDF is fetched:** a main manifest fails, the frame holds fewer than 500 decisions, or it holds more than 4,500. Any change goes in a published amendment before any text is read.
- **Fetching:** each decision's PDF, from the MSPB's public decisions folder. One request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. robots.txt allows /decisions/. The job stops if 25 fetches in a row fail; a 404 is counted but does not count toward this stop. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite` (a **fabricated-citation decision**): one of these phrases appears.
  - "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words by a kind of authority: case, citation, authority, quotation, opinion, decision, case law or precedent. The two words may not be function words or possessives, so "fabricated a case against him" and "fabricated its decision" do not count.
  - "Cited ... do/does/did not (appear to) exist".
  - "Cases, citations, authorities or decisions (that) do/did not (appear to) exist".
  - "Locate the cases ... cited".
- `ai_mention`: an AI term appears. The terms are artificial intelligence; generative AI; AI-generated, AI-drafted, AI-assisted, AI tool or platform; "(AI)"; ChatGPT; large language model; LLM. "AI" may also appear as "Al" (case-sensitive). `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- `pro_se`: the words "pro se" in the first 4,000 characters (the caption and representation block).
- `kind`: read from the heading in the first 4,000 characters. REMAND ORDER makes it remand; OPINION AND ORDER makes it opinion; FINAL ORDER makes it final; any other ORDER makes it other_order.
- `action` is coded for fabricated-citation decisions only: "sanction(s/ed)" or 5 C.F.R. 1201.43 appears.

## Predictions (fixed now)

- **P1:** the frame holds at least 5 readable fabricated-citation decisions.
- **P2:** fewer than half of the fabricated-citation decisions mention an AI term. Not testable below 3.
- **P3:** decisions issued from 2025-07-01 on have a higher share of fabricated-citation decisions than decisions issued before that date. Not testable below 3 fabricated-citation decisions, or below 100 readable decisions in either period.
- **P4:** at least two thirds of the fabricated-citation decisions have a pro se appellant. Not testable below 3.
- **P5:** the pro se share is higher among fabricated-citation decisions than among all readable decisions. Not testable below 3.
- **P6:** fewer than half of the fabricated-citation decisions mention sanctions or 5 C.F.R. 1201.43. Not testable below 3.
- **P7:** at least half of the fabricated-citation decisions are final orders. Not testable below 3.
- **P8 (not blind; see above):** the AI Hallucination Cases Database, as downloaded by the job, has no row whose court is the MSPB.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt for a fabricated-citation decision and every AI mention. They will report false matches, and decisions the patterns missed, separately, with corrected counts beside the graded ones. The verdicts stay as graded.

## Outputs

`results.json`, `results.md`, `rows.csv`, `manifests.json` (each manifest's size, SHA-256, row counts and date range) and `sources.json`. `rows.csv` has one row per decision: an id (the first 12 hex digits of SHA-256 of `collection/file name` in lower case, so anyone can recompute it from the manifest), collection, docket number, issued date, agency, kind, fetch status, text length, the PDF's SHA-256 and the flags. **Appellants' names and file names (which carry them) are not published,** even though the MSPB publishes them. Texts and excerpts stay private to the job.

## Limits

This census covers only Board decisions, not administrative judges' initial decisions, which the MSPB does not list. If an initial decision dealt with fake citations and nobody petitioned for review, it is outside the frame. Regular expressions can miss unusual wording ("we could not find these decisions") or catch an unrelated phrase. The excerpt review is there to show how often. A fabricated-citation passage may describe either party's filing; the review will say which. The census counts what decisions say. It does not judge any appellant, representative, agency or Board member, and it is not legal advice.
