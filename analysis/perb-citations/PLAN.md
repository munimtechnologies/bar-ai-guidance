# Pre-registration: fabricated citations in California PERB decisions, 2022-2026 (census 1.0.0)

Status: **frozen before the code reads any full decision text in the frame.** Written 2026-11-13 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public decisions of a state labor-relations board, not legal advice.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Done so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md), the [MSPB](../mspb-citations.md), the [BIA](../bia-citations.md) and the [New York tax tribunals](../nydta-citations.md) (a control with none). Queued: the [California WCAB](../wcab-citations/PLAN.md), the [California OTA](../ota-citations/PLAN.md) and the [USPTO's discipline archive](../uspto-oed-citations/PLAN.md).

California's Public Employment Relations Board (PERB) decides unfair-practice and representation cases for public employers and unions. MV2's [first look](../perb-fabricated-authority.md) read only the Board's monthly summaries (December 2025 to October 2026, 88 decisions and orders) and found **four decisions** in which the Board said a party cited fabricated or nonexistent authority: 2995-E (*Atwater*, precedential, AI named), 3037-H, 3040-M and 3041-H. The tracker lists only *Atwater*. That look did not read full texts or any month before December 2025. The questions:

1. Over every decision and order PERB posted from January 2022 to November 2026, how many say a party cited authority that does not exist, and how many mention AI?
2. Did it start only recently?
3. **Do the Board's own one-paragraph summaries mention it whenever the full decision does?** PERB posts a summary for every decision, but full texts only for some (its site says non-precedential PDFs are not posted). If summaries leave it out, any count built from summaries, including MV2's first look, is a floor.
4. Does the tracker list them?

## What was seen before freezing, stated plainly

- The monthly summaries for December 2025 to October 2026 and the four decision pages above (12 Nov 2026). So **P1 is a recall check, not a blind prediction**, and P2 to P8 were set knowing these four exist.
- On 13 Nov 2026, to design the frame: the slugs and post dates on REST listing pages 1, 2 and 4 (no summaries read beyond the item for 3041-H), robots.txt (no path blocked; `Crawl-delay: 10`), and the pages of 3041-H (precedential; links `decision-3041h.pdf`) and 3040-M (non-precedential; no PDF link). **No full decision text was read.**
- **The database (downloaded 2026-11-11) has one row whose court is PERB** (*Atwater*), so **P6 is not blind**: it checks that little has changed.

## Frame

- **Listing:** the Board's public WordPress listing of its `decision` posts (`https://perb.ca.gov/wp-json/wp/v2/decision`, newest first, 100 a page, with each post's summary), read page by page until a page reaches posts dated before **1 January 2022**. The frame is every post whose post date is on or after 1 January 2022, as listed when the job runs. A slug already seen on an earlier page is skipped and counted. Posts include Board decisions (for example `3041h`), administrative orders (`a530h`) and later versions of a decision (`2995ea`). A later version counts as a separate **post** but the same **decision** (`decision_key`: prefix, number and first suffix letter).
- **Stops, before any decision page is fetched:** the listing fails or does not reach 2022 within 12 pages; the frame holds fewer than 250 or more than 600 posts; or more than 10 frame posts have a slug the parser does not recognise. Any change goes in a published amendment before any text is read.
- **Fetching:** for every post, its decision page; if the page links a full-text PDF under `/decisionbank/` on perb.ca.gov (the one whose file name carries the slug, or else the only one), that PDF. One request at a time, **10 seconds apart** (robots.txt), as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 decision pages in a row fail. **Summary OK:** 100+ characters. **Full text readable:** a PDF whose text is 300+ characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's WCAB, OTA and USPTO censuses, unchanged: "fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, portion, passage, page or parenthetical; "cited ... do(es) not exist"; "cases/citations/... (that) do not exist"; "a case/citation/... that does not exist"; "locate the cases ... cited". A post has `fake_cite` if its **summary or its full text** has one (`fake_summary`, `fake_full` are kept separately).
- `ai_mention`, `ai_citation` (an AI term within 2,000 characters of a fabricated-citation phrase) and `hallucination`: as in the WCAB census. `atwater`: the word "Atwater". `abuse_of_process`: "abuse of (the) (PERB's) process" (recorded, does not flag a post).
- `in_db`: a database row that mentions PERB quotes the decision number with its letter (2995-E or 2995E), or a PERB-court row's case name contains a distinctive word (5+ letters, not boilerplate) of the decision page's heading.

## Predictions (fixed now)

- **P1 (recall check, not blind):** 2995-E, 3037-H, 3040-M and 3041-H are in the frame and each has a fabricated-citation phrase in its summary or full text.
- **P2:** 5 to 12 decisions in the frame have a fabricated-citation phrase.
- **P3:** no decision posted before 1 January 2025 has one.
- **P4:** at least one decision whose full text is posted has a fabricated-citation phrase in the full text but not in its summary.
- **P5:** fewer than half of the decisions with a fabricated-citation phrase mention an AI term.
- **P6 (not blind):** the database, as downloaded by the job, has at most one PERB-court row, and at least three decisions with a fabricated-citation phrase are not in it.
- **P7 (method check):** at least 98% of frame posts have a summary of 100+ characters, and at least 95% of posted full texts are readable.
- **P8:** at least two decisions with a fabricated-citation phrase, other than *Atwater* itself, mention *Atwater*.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text (or summary, where no full text is posted) of every flagged post. They will report false matches, and cases the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record who cited the authority (individual charging party, union, employer, lawyer), what the Board did (warning, dismissal, sanction), whether it named AI, and whether the tracker lists it (also checked by hand on its live search).

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (pages read, their SHA-256 and parser checks) and `sources.json`. `rows.csv` has one row per post: slug, decision key, post date, decision date, whether the page says non-precedential, whether a full text is posted, fetch statuses, text lengths, the PDF's SHA-256, `in_db`, whether it was one of the four known decisions, and the flags. **Decision numbers are public identifiers and are published; names, page headings, summaries and texts are not** (they stay private to the job), even though PERB publishes them: many charging parties are individual employees.

## Limits

Decisions are what the Board chose to write. Most full texts of non-precedential decisions are not posted, so for them only the summary is read, and P4 can only be tested on precedential decisions. A decision that describes a fake citation in other words would be missed; the review looks for missed cases only among flagged texts. Post dates are when the decision was posted, usually its issue date. The census counts what decisions say. It does not judge any employee, union, employer, lawyer or official, and it is not legal advice.
