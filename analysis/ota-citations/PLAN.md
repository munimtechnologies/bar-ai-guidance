# Pre-registration: fabricated citations in the California Office of Tax Appeals' opinions, 2024-2026 (census 1.0.0)

Status: **frozen before the code reads any opinion text in the frame.** Written 2026-11-11 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (it uses `pypdf` to read PDFs). Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public opinions of a state tax tribunal, not legal or tax advice.

## Why

MV2's earlier censuses compared tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). Done so far: the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md) and the [MSPB](../mspb-citations.md). Queued: the [BIA](../bia-citations/PLAN.md) and the [USPTO's discipline archive](../uspto-oed-citations/PLAN.md). All of them are federal. This census is the first **state** tribunal in the series. California's Office of Tax Appeals (OTA) hears appeals from the Franchise Tax Board and the CDTFA. Many appellants represent themselves. It publishes every opinion, about 550 to 700 a year, on year pages at ota.ca.gov.

In July 2026 Bloomberg Tax reported ("California Tax Tribunal Mulls AI Rules as Fake Citations Surface") that the OTA had addressed "hallucinated or fictitious citations" for the first time, in an opinion marked pending precedential, and that it was considering guidance on AI use. On 11 Nov 2026 the tracker's CSV had **no row whose court is the OTA** (or the Board of Equalization), and no California tax-tribunal row of any kind. The questions:

1. How many OTA opinions from 2024 to November 2026 say that a party cited authorities that do not exist, and how many mention AI?
2. Is that confined to the one reported opinion, and is it growing (2024 vs 2025 vs 2026)?
3. Does the tracker list them?

## Prior art (searched 2026-11-11)

The Bloomberg Tax report above (headline and search-result summary only; the article is paywalled), and practitioner and press coverage of California Court of Appeal sanctions (*Noland v. Land of the Free*, 2025). We found no count across OTA opinions and no check of the tracker's coverage of any state tax tribunal.

## What was seen before freezing, stated plainly

- **Listing metadata only.** The agents read summaries of the 2026 franchise and income tax (FIT) page, the 2026 and 2024 business tax (BT) pages, and parts of the 2025 and 2024 FIT pages. Each is one table with the columns Decisions (party name, linked to a PDF), Month, Year, Cite (for example 2026-OTA-564, with suffixes P and SCP, and one malformed as "2026=OTA=551"), Decision Type (Nonprecedential, Precedential, Pending Precedential) and Issues. Highest cites seen: 2024-OTA-685, 2025-OTA-664, 2026-OTA-564. The summaries listed four 2026 FIT opinions as Pending Precedential. robots.txt allows everything outside /wp-admin/ and asks for a 10-second crawl delay. **No opinion text in the frame was read for this study,** and the July 2026 opinion has not been identified.
- **One opinion is not blind.** From the press report: a 2026 opinion marked pending precedential calls nonexistent citations "concerning and inappropriate", declines to consider arguments without real authority, and cites a 2025 Court of Appeal ruling (we guess *Noland*). So **P1 and P7 are not blind,** and P2 was set knowing at least one exists.
- **The database (downloaded 2026-11-11, 02:34 UTC) has no OTA row,** so **P8 is not blind**: it checks that nothing has changed.

## Frame

- **Listings:** every table row on six pages: https://ota.ca.gov/2026-franchise-income-tax-opinions/, .../2025-franchise-income-tax-opinions/, .../2024-franchise-income-tax-opinions/, .../2026-business-tax-opinions/, .../2025-business-tax-opinions/ and .../2024-business-tax-opinions/. Columns are read by header. A row's links are those in its Decisions and Cite cells, tried in order until one returns a PDF.
- **Window:** the year in the row's cite (or the Year cell if the cite cannot be read) is 2024, 2025 or 2026, as listed when the job runs. Rows whose first link was already taken by an earlier row are skipped and counted. Duplicate cite numbers are kept and counted.
- **Stops, before any opinion is fetched:** a listing page fails; the frame holds fewer than 1,300 or more than 2,600 opinions; a page lacks the expected header row; more than 10 rows have no readable cite; or more than 10 rows in the frame have no link. Any change goes in a published amendment before any text is read.
- **Fetching:** one request at a time, 10 seconds apart (the site's crawl delay), as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. The job stops if 15 opinions in a row fail. **Readable:** a PDF whose text is at least 300 characters once whitespace is collapsed.

## Definitions (as coded in census.py)

- `fake_cite`: the fabricated-citation patterns of MV2's USPTO census, unchanged. "Fictitious", "nonexistent", "fabricated", "fake", "hallucinated", "made-up", "bogus", "phantom" or "invented", followed within two words (not function words) by a case, citation, authority, quotation, opinion, decision, case law, precedent, portion, passage, page or parenthetical. Also "cited ... do(es) not exist", "cases/citations/... (that) do not exist", "a case/citation/... that does not exist", and "locate the cases ... cited".
- `ai_mention`: artificial intelligence; generative AI; AI-generated, -drafted, -assisted, -based, -powered, AI tool or platform; "(AI)"; ChatGPT; large language model. `ai_citation`: an AI term within 2,000 characters of a fabricated-citation phrase.
- `hallucination`: any word starting "hallucinat". `noland`: the word "Noland".
- `in_db`: any database row quotes the opinion's cite (for example "2026-OTA-311", leading zeros ignored), or a row whose court is the OTA or the Board of Equalization has a case name containing a distinctive word of the party's name. Party names are used only for this check and are never published.
- Precedential: Decision Type "Precedential" or "Pending Precedential".

## Predictions (fixed now)

- **P1 (not blind):** at least one 2026 opinion designated precedential or pending precedential has a fabricated-citation phrase.
- **P2:** 2 to 8 opinions in the frame have a fabricated-citation phrase.
- **P3:** no 2024 opinion has one.
- **P4:** at least as many 2026 opinions as 2025 opinions have one.
- **P5:** fewer than half of the fabricated-citation opinions mention an AI term. (A genuine guess: in MV2's Tax Court census 2 of 3 such documents named AI, which went against this; the one MSPB decision did not name AI. The OTA's reported wording, "hallucinated or fictitious citations", describes the citations without naming a tool.)
- **P6:** at least half of the fabricated-citation opinions are franchise and income tax opinions (where individual appellants are most common).
- **P7 (not blind for the July 2026 opinion):** at least one fabricated-citation opinion cites *Noland*.
- **P8 (not blind):** the database, as downloaded by the job, has no OTA-court row, and at least one fabricated-citation opinion is not in it.
- **P9 (method check):** at least 98% of the opinions in the frame are readable.

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read every excerpt and the full text of every flagged opinion. They will report false matches, and opinions the patterns missed among flagged texts, separately, with corrected counts beside the graded ones; the verdicts stay as graded. For each true case they will record whether the appellant was represented, what the OTA did, whether it named AI, and whether the tracker lists it (also checked by hand on the tracker's live search).

## Outputs

`results.json`, `results.md`, `rows.csv`, `listing.json` (each page's size, SHA-256, row counts and parser checks) and `sources.json`. `rows.csv` has one row per opinion: a row id (the first 12 hex digits of SHA-256 of `page|cite|month|year`, lower case, with `|n` added for the n-th repeat), cite, page (fit or bt), month, year, decision type, the OTA's issue summary, fetch status, text length, the PDF's SHA-256, `in_db` and the flags. **Party names and file names (which carry them) are not published,** even though the OTA publishes them. Texts and excerpts stay private to the job.

## Limits

The OTA's opinions are what the panel chose to write; a fake citation that an opinion does not mention is invisible here, and an opinion that describes one in other words would be missed. The review looks for missed cases only among flagged texts. The census counts what opinions say. It does not judge any taxpayer, representative or official, and it is not legal or tax advice.
