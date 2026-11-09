# AI terms in the in-force Code of Federal Regulations: a census (plan, census 1.0.0)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
Plan frozen on 2026-11-09, before the full download. Text CC BY 4.0, code Apache-2.0.
Information about public regulations, not legal advice.

## Question

Since 2023, state courts have changed their own rules of practice for AI (New York Part 161,
Florida Rule 2.515, Connecticut Practice Book Section 4-9, Indiana Trial Rule 11; see
data/guidance.json in this repository), and federal tribunals such as GAO decide cases about
AI-invented citations (analysis/procurement-ai.md). What does the binding federal
regulatory text say about AI?

1. How many distinct provisions (sections and appendices) of the Code of Federal Regulations
   in force on the census date, 2026-11-06, use at least one of the terms below, and how many
   were in force on 1 January of each year from 2017 to 2026 and on 1 July 2026?
2. Which agencies and subject areas do they come from?
3. Does any agency's own rules of practice or procedure (the rules for filings and hearings
   in its proceedings) use any of the terms?
4. Which terms never appear in the in-force text?
5. How many of the provisions in force on the census date first took effect in 2025 or later?

We searched for a published count of AI terms in the in-force CFR and found none (web search,
2026-11-09). Counts of AI-related documents in the Federal Register (for example in the Stanford
AI Index) measure new documents per year, not the text in force; this census measures the text
in force at each date, provision by provision.

## Source and method

- eCFR search API of the Office of the Federal Register,
  `https://www.ecfr.gov/api/search/v1/results`, which indexes every version of every CFR
  section and appendix since January 2017 and accepts a point-in-time `date`. robots.txt of
  ecfr.gov does not disallow `/api/search/`. Requests are made 2 seconds apart with the user
  agent `MV2-Munim-research/1.0 (mv2@munimtech.com)`.
- Terms, each searched as an exact phrase in double quotes: artificial intelligence; machine
  learning; deep learning; neural network; large language model; generative artificial
  intelligence; generative AI; chatbot; natural language processing.
- For each term: one query with no date (every version since 2017, used for the first date a
  matching version took effect) and one query at each of the 12 dates (1 January 2017 to 2026,
  1 July 2026 and 2026-11-06). Every page is fetched (50 results a page).
- A hit becomes a provision by its hierarchy: `<title> CFR <section>`, or for an appendix
  `<title> CFR Part <part>[ Subpart <x>], <appendix>`. Versions of one provision are merged.
- A dated hit counts only if its own `starts_on` is on or before the date and its `ends_on` is
  empty or on or after it (both inclusive). Hits outside that window are excluded and counted
  as date-filter anomalies.
- Category, by title and part: export controls (15 CFR 730-774), ICT supply chain (15 CFR 7
  and 791), outbound investment (31 CFR 850), bulk sensitive data (28 CFR 202), medical
  devices (21 CFR 800-898), Medicare and Medicaid (42 CFR 400-699), federal procurement
  (title 48), otherwise "other". Agency = the CFR chapter heading.
- Rules of practice or procedure: the provision's subchapter, part or subpart heading matches
  "rule(s) of practice", "rule(s) of procedure", "practice and procedure", "practice before",
  "procedural rules", "adjudicat..." or "administrative hearing(s)".
- The job (run_job.py) does nothing until this PLAN.md and census.py are public in this
  repository and the census.py it runs is byte-identical (line endings aside) to the committed
  one. All outputs are public U.S. government data or derived from it, and are published in
  full: provisions.csv, timeline.csv, results.json, results.md, queries.json, anomalies.json.

## What was seen before this plan was frozen (disclosed)

While scoping on 2026-11-09 we ran a handful of live queries: undated "artificial
intelligence" (96 version hits; the provisions on the first page were mostly export-control
and investment-screening rules), undated "machine learning" (18 version hits, five of them
FDA medical-device classification rules from 2026), "large language model" (0),
"generative artificial intelligence" (0), unquoted "generative" (1 unrelated hit), and the
counts for "artificial intelligence" on 2020-01-01 (2 version hits) and for "machine learning"
on 2026-11-01 (9 version hits). Because of this the census is **descriptive, not a test of
predictions**: its value is a complete, dated, reproducible list, not a forecast. We state one
expectation only so that it can be checked in public: question 3 will find no provision.

## Checks and reporting

- Every query must return as many hits as its `total_count`; otherwise the result is marked
  incomplete and the gap is reported, not filled by hand.
- Date-filter anomalies are reported with their count and listed in anomalies.json.
- Every provision in force on the census date is read by hand in the write-up; a hit whose
  matching words are not about AI (for example a name) is reported as a false match beside the
  unchanged machine count.

## Limits

- Exact phrases only: a provision that says "AI" alone, "automated system" or
  "algorithm" without one of the terms is not counted.
- The eCFR is an editorial compilation, not the official legal edition; point-in-time
  versions start in 2017.
- Agency rules of practice are found by heading, so practice rules placed under a
  differently named part are missed; the write-up lists the headings it saw.
- Guidance documents, policy statements and Federal Register preambles are not in the CFR and
  are out of scope.

## Amendment 1 (2026-11-09, census 1.0.1), written after the 1.0.0 run failed

**What happened.** The 1.0.0 run (sealed job cfrai-v1, 2026-11-09 17:59 to 18:40 UTC) completed
every undated query and every query at 10 of the 12 dates. At the other two dates the eCFR search
API answered HTTP 400 for all nine terms, after three tries each:

- **2017-01-01**: earlier than the first point-in-time date the eCFR holds (its versions begin on
  3 January 2017; a query at 2017-01-03 works).
- **2026-11-06**: later than the date the eCFR was up to date as of. On 2026-11-09 the eCFR
  versioner API (`/api/versioner/v1/titles.json`) gave `up_to_date_as_of` 2026-11-05 for every
  title, and a query at 2026-11-05 works.

As this plan requires, run_job.py marked the result incomplete and nothing was filled in by hand.
Its status, query log and generated table are kept unchanged in `run-1.0.0/`.

**What changes in 1.0.1, and nothing else.** The first date becomes 2017-01-03 and the census date
becomes 2026-11-05, so the twelve dates are 3 January 2017, 1 January 2018 to 2026, 1 July 2026 and
5 November 2026. run_job.py now waits until the newest committed census.py is identical to its own
copy (so the re-run cannot start before this amendment is public), and records the eCFR's
`up_to_date_as_of` date beside the results. The terms, the method, the categories, the checks and the
one stated expectation (question 3 finds no provision) are unchanged. Questions 1 and 5 now read
"in force on 2026-11-05".

**What the agents saw before writing this amendment, disclosed.** Everything in `run-1.0.0/`: the
counts at the ten dates that worked (for example 29 provisions on 1 July 2026, 10 on 1 January
2020) and the list of the 35 provisions that ever used a term. Also three live checks on
2026-11-09: "neural network" at 2017-01-03 (6 version hits), "neural network" at 2026-11-05
(11 version hits) and "machine learning" at 2026-11-01 (9 version hits). The two new dates were
chosen only because they are the nearest dates the eCFR serves, not because of any count.
