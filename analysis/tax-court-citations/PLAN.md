# Pre-registration: fabricated citations in the U.S. Tax Court's own records, 2023-2026 (census 1.0.0)

Status: **frozen before the code reads any document text in the frame.** Written 2026-11-10 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py` and `test_run_job.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public court documents, not legal advice.

## Why

Two of MV2's earlier studies found that the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database, holds few agency and Tax Court decisions: [agency AI-authority census](../agency-ai-authority.md). Trackers hold what contributors find. The U.S. Tax Court runs its own public search over the full text of its orders and opinions, DAWSON, through an open JSON API with no login. That makes it possible to ask the question from both sides for one federal court:

1. How many Tax Court orders and opinions since 2023 say that a filing cited cases or authorities that are fictitious or do not exist, and how many of them does the tracker list?
2. Does the court's own search find the Tax Court decisions that the tracker lists?
3. What do those documents rest on: the Tax Court's own Rule 33(b) (a signature certifies that a filing is warranted by existing law), the section 6673 penalty, or AI at all?

## Prior art (searched 2026-11-10)

The trackers (AI Hallucination Cases Database, legalaigovernance.com, court-order trackers) list single Tax Court decisions, and law-firm and tax-press posts discuss a few of them, such as Thomas (Docket 10795-22, October 2024). We found no count of fabricated-citation orders taken from the Tax Court's own records, no measure of how much of them a tracker covers, and no test of the court's search against a tracker.

## What was seen before freezing, stated plainly

The agents read **search result metadata only**: docket number, date, document type and judge. They read no document text. Here is what they saw:

- Order search for `"artificial intelligence"` returned 3 orders: 10795-22 (2024-10-23), 21959-16 (2021) and 255-18 (2020). Opinion search returned 8 opinions, including 2249-25 (2026-09-15) and 8077-23 (2026-02-09).
- Order search for `ChatGPT` returned 1 order (6165-24, 2025-12-31). Order search for `nonexistent cases` returned 20 orders, 7 of them from 2023 on (including 8206-24, 2025-12-30). Order search for `nonexistent` alone returned 32 orders, and 8206-24 was not among them. The exact phrase `"nonexistent cases"` returned none. Opinion search for `nonexistent` returned more than 180 opinions, 57 of them from 2023 on, most about entities or transactions rather than citations. Opinion search for `"large language model"` returned 1 (8077-23), and for `generative` 2 (one in the window, 8077-23). Opinion search for `fabricated` returned 167 (21 in the window). Order search for `fictitious` returned 42 (6 in the window), and for `fake` 12 (3 in the window).
- The database (as downloaded 2026-11-10) lists 5 U.S. Tax Court rows: Thomas 2024-10-23, Bauche 2025-05-20, Clinco 2026-02-09, Riddle Aggregates 2026-03-18 and Moore 2026-09-15. From the metadata alone, 4 of them (Thomas, Bauche, Clinco and Moore) appear to match documents those searches return. Riddle Aggregates was not seen. **P7 was set knowing this,** so it is a check on matching and on Riddle Aggregates, not a blind prediction.
- The search behaves unevenly. A broader term returned fewer orders than a narrower one, and the exact phrase returned nothing. That is why the frame is built from a fixed list of many searches, not one. P8 tests the search directly.

## Frame

- **Searches:** each of the 27 keyword searches listed in `census.QUERIES`, run once against order search and once against opinion search. They cover AI terms (artificial intelligence, ChatGPT, generative, large language model, four forms of hallucinat-), citation-problem words alone and paired with "cases" or "citations" (nonexistent, non-existent, fictitious, fake, fabricated, bogus), and Avianca. Phrases such as "cases do not exist" or "unable to locate case" are **not** searched. On metadata checks they returned hundreds to thousands of documents, because the court's search matches the words, not the phrase: opinion search for "case does not exist" returns most opinions. Those phrases are still looked for in the text of every frame document. The opinion types searched are memorandum, summary, T.C. and bench opinions (`MOP,OST,SOP,TCOP`). Each search covers all dates and is filtered by the job to filing dates **2023-01-01 to 2026-11-10**.
- **Frame:** the union of all in-window results. A document filed in several consolidated dockets has one docket-entry id and counts once. Requests run one at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`.
- **Stops, before any document text is fetched:** more than 3 searches fail; the frame holds fewer than 20 documents; or it holds more than 2,000. Any change goes in a published amendment before any text is read.
- **Text:** each document's PDF, fetched through the court's public download route. **Readable:** fetched, and at least 300 characters of text once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite` (a **fabricated-citation document**): one of these phrases appears:
  - fictitious, nonexistent, fabricated, fake, hallucinated, made-up, bogus, phantom or invented, followed within two words (not counting function words) by a kind of authority: case, citation, authority, quotation, opinion, decision, case law or precedent;
  - "cited ... do/does/did not exist";
  - "cases, citations or authorities (that) do/did not exist";
  - "locate the cases ... cited".
- `ai_mention`: an AI term (artificial intelligence; generative AI; AI-generated, -drafted, -assisted, AI tool or platform; "(AI)"; ChatGPT; large language model; LLM). "AI" may also appear as "Al", case-sensitive. `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase. `ai_phrase`: the words "artificial intelligence".
- Coded for fabricated-citation documents only: `rule_33` (Rule 33(b)), `sec_6673` (the number 6673), `mata` (Mata v. Avianca), and `action` (sanction, Rule 202, disciplinary, or a penalty under section 6673).
- **Kind:** an opinion if its event code is MOP, OST, SOP or TCOP; otherwise an order.
- **In the database:** a database row whose Court is "Tax Court", "US Tax Court" or "U.S. Tax Court" (not a state tax court, not Canada), dated within 7 days of the document, with a party-name word of the row (4+ letters, common words like "Estate" or "Commissioner" dropped) in the document's caption.

## Predictions (fixed now)

- **P1:** the frame holds at least 10 readable fabricated-citation documents.
- **P2:** fewer than half of the fabricated-citation documents are in the database. Not testable below 3, or if the database could not be downloaded.
- **P3:** fewer than half of the fabricated-citation documents mention an AI term. Not testable below 3.
- **P4:** at least half of the fabricated-citation documents are orders, not opinions. Not testable below 3.
- **P5:** at least half of the fabricated-citation documents cite Rule 33(b). Not testable below 3.
- **P6:** fewer than half of the fabricated-citation documents cite section 6673. Not testable below 3.
- **P7 (coverage check, not blind; see above):** every U.S. Tax Court row of the database dated in the window matches a document in the frame.
- **P8 (search check):** at least 90% of readable frame documents whose text contains "artificial intelligence" were returned by the exact-phrase search for it. Not testable below 3.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt of a fabricated-citation document and of an AI mention. They will report false matches, and documents the patterns missed, separately, with corrected counts beside the graded ones. The verdicts stay as graded. Each database match will be checked by hand.

## Outputs

`results.json`, `results.md`, `rows.csv` and `searches.json` (every search with its result counts), plus `sources.json`. `rows.csv` has one row per document: docket-entry id, docket numbers, date, kind, event code, document type, signing judge, pages, a link to the public case page, the PDF's SHA-256 and flags. **Case captions (party names) are not published.** Documents are named by docket number. Texts and excerpts stay private to the job.

## Limits

The frame is only what the court's search returns for these words. A fabricated-citation order phrased in other words ("the Court could not find these opinions") is outside it unless another search catches it. Regular expressions can miss unusual phrasing or catch an unrelated one, and the excerpt review is there to show how often. Party-name matching to the database can fail on an unusual caption, so each match is checked by hand. Orders the court has sealed are not public and not counted. This counts what documents say. It does not judge any taxpayer, practitioner or judge, and it is not legal or tax advice.
