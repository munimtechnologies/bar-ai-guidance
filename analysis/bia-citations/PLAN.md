# Pre-registration: fabricated citations in the precedent decisions of the Board of Immigration Appeals and the Attorney General, 2020-2026 (census 1.0.0)

Status: **frozen before the code reads any decision text in the frame.** Written 2026-11-11 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a federal agency, not legal advice.

## Why

The immigration courts and the Board of Immigration Appeals (BIA), both part of the Justice Department's Executive Office for Immigration Review (EOIR), make up the largest adjudication system in the federal government. In August 2025, EOIR issued Policy Memorandum 25-40 on the use of generative AI. MV2's earlier censuses found that the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database, covers the Federal Labor Relations Authority's and the Tax Court's own records better than expected ([FLRA](../flra-ai-citations.md), [Tax Court](../tax-court-citations.md)). It has no row for any EOIR body, although it lists many federal appeals-court decisions on petitions for review of BIA orders. The immigration courts do not publish their decisions, and the BIA publishes only a few dozen a year as precedents, in volumes of *Administrative Decisions under Immigration and Nationality Laws* (I&N Dec.). Those precedents are the BIA's only public record that can be read in full. The questions:

1. How many BIA and Attorney General precedents issued since 2020 address fabricated citations, and in what kind of case?
2. Which authority do they rely on: EOIR's own AI memo, its practitioner-discipline rules (8 C.F.R. 1003.101-1003.109), or neither? This is the same question as MV2's [agency AI-authority census](../agency-ai-authority.md).
3. Does the tracker list them?

## Prior art (searched 2026-11-11)

Searches found commentary on *Matter of Sethi*, 30 I&N Dec. 112 (BIA 2026), which practitioners' blogs describe as the BIA's first precedent disciplining an attorney over AI-fabricated citations. They also found a law firm's list of every BIA precedent since January 2025 and tracker pages summarising PM 25-40. We found no count of fabricated-citation passages across the BIA's precedents, and no check of whether the tracker covers them.

## What was seen before freezing, stated plainly

- **Listing metadata only.** The agents read summaries of EOIR's three listing pages (https://www.justice.gov/eoir/volume-28, -29, -30): about 100, 155 and 33 entries; Interim Decision numbers 3985-4273, with 4248 missing from the volume 30 page; link formats; issuers (mostly BIA, a few A.G., one AAO, one DIR). Headnotes were not read for this study. No decision text in the frame was read.
- **Matter of Sethi is not blind.** Search summaries said it is a reciprocal-discipline decision after a Ninth Circuit order (*Lnu v. Blanche*, 3 June 2026) about fabricated citations, that it suspends the attorney for six months, and that it refers to 8 C.F.R. 1003.106. So **P1 is a check of the patterns, not a prediction.** P2, P4 and P5 were set knowing at least one such decision exists.
- **The database, as downloaded on 2026-11-10, has no row naming an EOIR body as its court** and no row for Matter of Sethi. It does have *Malkeet Lnu v. Blanche* (9th Cir., 2026-06-03). So **P7 and P8 are not blind**: they check that nothing has changed.
- justice.gov's robots.txt allows these paths and asks for a 10-second crawl delay, which the job keeps.

## Frame

- **Listing pages:** EOIR's pages for volumes 28, 29 and 30. An entry is an "ID nnnn" marker (an Interim Decision number between 3900 and 4500). Its citation is the last citation of the same volume within 600 characters before the marker. Its links are the non-empty links touching the marker, tried in order until one returns a PDF. Duplicate IDs keep the first.
- **Stops, before any decision is fetched:** a listing page fails; the frame holds fewer than 250 or more than 400 decisions; or more than 15 entries have no citation, no link, or a citation already taken by another entry. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 10 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 decisions in a row fail. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's MSPB census, plus singular forms ("a case that does not exist", "cites ... does not exist"). That is: "fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a kind of authority; "cited/cites ... do(es) not exist"; "cases/citations/authorities/decisions (that) do not exist"; "locate the cases ... cited".
- `ai_mention`: artificial intelligence; generative AI; AI-generated, -drafted, -assisted, AI tool or platform; "(AI)"; ChatGPT; large language model. "AI" may appear as "Al" only in the compound forms. "LLM" is left out because in immigration records it is usually a law degree. `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- `pm2540`: "PM 25-40", "Policy Memorandum 25-40" or the memo's title. `disc_reg`: 8 C.F.R. 1003.101-1003.109 or 1292.3 cited anywhere. `discipline`: in the first 4,000 characters, a word for suspension, expulsion, disbarment or discipline together with "practice before", "practitioner" or "disciplinary". This keeps out "suspension of deportation".
- `issuer`: BIA, AG, AAO or DIR, read from the citation.

## Predictions (fixed now)

- **P1 (pattern check, not blind):** *Matter of Sethi*, 30 I&N Dec. 112, is readable and has a fabricated-citation phrase.
- **P2:** 1 to 3 readable decisions in the frame have a fabricated-citation phrase.
- **P3:** no readable decision cites EOIR Policy Memorandum 25-40.
- **P4:** every fabricated-citation decision cites the practitioner-discipline rules. Not testable if there are none.
- **P5:** every fabricated-citation decision is a practitioner-discipline decision. Not testable if there are none.
- **P6:** fewer than 5 readable decisions mention an AI term.
- **P7 (not blind):** the database, as downloaded by the job, has no row whose court is an EOIR body.
- **P8 (not blind for Sethi):** no database row quotes the citation of any fabricated-citation decision in the frame. Failed if one does. Not testable if there are no such decisions, or if the database has an EOIR-court row, which then needs a hand check.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged decision. They will report false matches, and decisions the patterns missed, separately, with corrected counts beside the graded ones; the verdicts stay as graded. They will also search the database by hand for each fabricated-citation decision by name.

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (each page's size, SHA-256, entry count, ID gaps) and `sources.json`. `rows.csv` has one row per decision: Interim Decision number, citation, issuer, year, fetch status, text length, the PDF's SHA-256, the URL fetched and the flags. Party names are not published (the citation identifies each public precedent). Texts and excerpts stay private to the job.

## Limits

Precedents are a small, selected slice of the BIA's work. Most of its tens of thousands of yearly decisions are unpublished, and immigration judges' decisions are not published at all. A low count here says nothing about how often fabricated citations reach immigration courts. It shows only what the BIA has chosen to say in precedent. Regular expressions can miss unusual wording or catch unrelated phrases (asylum cases often discuss fraudulent documents). The excerpt review is there to show how often. The census counts what decisions say. It does not judge any respondent, practitioner or Board member, and it is not legal advice.
