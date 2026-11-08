# AI-fabricated authority at US federal procurement tribunals: graded result

*Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Information about
public decisions, not legal advice and not advice on any protest or claim. Code: Apache-2.0. Text
and derived rows: CC BY 4.0.*

**Plan:** [`procurement-ai/PLAN.md`](procurement-ai/PLAN.md), committed 2026-11-08 03:57 UTC
(commit `909f9a8`) before any data row was read. **Code:** [`analyze.py`](procurement-ai/analyze.py)
(analysis 1.0.0). The job checked that its copy matched the committed file (SHA-256
`08d1bed4...7e04`) before it downloaded anything.
**Data:** [AI Hallucination Cases Database](https://www.damiencharlotin.com/hallucinations/),
Damien Charlotin (CC BY 4.0). CSV fetched 2026-11-08 14:59 UTC, 2,175,509 bytes, SHA-256
`9201eecd5ea30ac3eda884062a6421f84882abf2f58415aa4391e283ef297c87`, 2,267 rows, none malformed.
**Outputs:** [`results.md`](procurement-ai/results.md), [`results.json`](procurement-ai/results.json),
[`procurement_rows.csv`](procurement-ai/procurement_rows.csv) (case_id, forum, date, party type and
penalty flags for each of the 32 rows; no case names, so look a row up by its `case_id` at the source).

## Short answer

The database holds **32 procurement decisions** at GAO, the Court of Federal Claims (COFC), the ASBCA
and the CBCA from 2025 to October 2026: GAO 24, ASBCA 4, CBCA 2, COFC 2. None comes before 2025.
**Lawyers' share rose from 2 of 15 rows in 2025 (13%) to 7 of 17 in January-October 2026 (41%).**
At GAO, 17 of 24 rows (71%) are protesters acting for themselves. **No row records a money penalty.**
The database holds fewer decisions than David Timm's hand count, and **the serial protester he
describes shows up as only 2 database rows**, so one of the six predictions failed for reasons
that tell us something useful about the data (below).

## The six pre-registered predictions

| # | Prediction (fixed in advance) | Result | Verdict |
|---|---|---|---|
| A1 | at least 15 core rows dated Jan-Jul 2026 (Timm counts 19 at these four forums) | 14 | **failed** (one short) |
| A2 | at least 17 core rows dated 2025 (Timm: 23 at all procurement tribunals) | 15 | **failed** |
| A3 | lawyer share higher in Jan-Oct 2026 than in 2025 (each period n >= 8) | 13.3% (2/15) to 41.2% (7/17) | **held** |
| A4 | at least 60% of GAO rows (2025 to Oct 2026) list a pro se party (n >= 10) | 70.8% (17/24) | **held** |
| A5 | at most 1 core row records a monetary penalty (n >= 10) | 0 of 32 | **held** |
| A6 | the most frequent protester is at least 25% of GAO rows (n >= 10) | 2 of 24 (8.3%, Oready, LLC) | **failed** |

Three held and three failed. Every prediction is reported, either way.

### Sensitivity analyses (reported, not graded)

| analysis | A1 | A2 | A3 | A4 | A5 | A6 |
|---|---|---|---|---|---|---|
| S1: every COFC row counts, not only procurement cases | held (15) | held (17) | held | held | held (1 money row) | failed |
| S2: forum also taken from case name or source | failed | failed | held | held | held | failed |
| S3: rows marked "Alleged" dropped | failed | failed | held | held | held | failed |

## What the failures show

**1. The coverage gap is mostly about scope.** Under S1, when every COFC row counts and not only the
procurement ones, A1 and A2 both hold. That matches how Timm counts. His September post calls the
COFC's opinion of 31 March 2025 in *Sanders v. United States* (176 Fed. Cl. 163) the first
procurement decision to discuss GenAI misuse. The plaintiff in *Sanders* brought an unjust-enrichment
claim for restitution for slavery, which is not a procurement case. The database does hold *Sanders*,
but its `Court` value is "Fed. claims court", which our pre-registered forum filter did not
recognise (it is the only such near-miss in the published near-miss table). So Timm's numbers count
AI-misuse decisions **at** procurement tribunals, while our core rule counts **procurement cases**
at them. Both are reasonable. Anyone comparing counts needs to know which one is meant.

**2. A serial filer's protests collapse into a few decisions.** Timm describes one protester, Oready,
LLC, with at least 23 GAO protests between April 2025 and July 2026. The database has 2 rows for
it (13 Aug 2025 and 25 Sep 2025), and the second row's outcome is "Protests dismissed for abuse",
plural. GAO decides consolidated protests in a single decision, and the database records decisions.
So "≥ 23 protests" and "2 database rows" are both true. A6 assumed the database's unit would follow
the protests, and it doesn't. Measured in decisions, GAO's AI-citation problem is spread across 23
different protester names in 24 rows, not concentrated in one.

**3. Lawyers are a growing share, but the numbers are small.** The jump from 2 lawyer rows to 7 is the
direction Timm describes ("lawyers are now a substantial part of the problem"). At GAO, all 8 rows
from July-December 2025 are pro se, while 5 of 9 from January-June 2026 list a lawyer. With these
counts, one or two decisions either way would change the percentages a lot. Nobody should read
this as a precise rate.

**4. No money.** None of the 32 rows records a monetary penalty, and none records a professional
sanction. These tribunals answer with dismissal, warnings and struck filings. Timm counts 3
"sanctions" in 2026 (ASBCA 2, CBCA 1). He uses the word more broadly than the database's
`Monetary Penalty` and `Professional Sanction` columns do.

## Rows by forum and half-year (core rows)

| forum | 2025 H1 | 2025 H2 | 2026 H1 | 2026 H2 (to Oct) | of which lawyer |
|---|---|---|---|---|---|
| GAO | 3 | 8 | 9 | 4 | 7 |
| ASBCA | 0 | 1 | 2 | 1 | 2 |
| CBCA | 0 | 1 | 1 | 0 | 0 |
| COFC (procurement text only) | 0 | 2 | 0 | 0 | 0 |

Against Timm's January-July 2026 split: GAO 10 (Timm 12), ASBCA 3 (4), CBCA 1 (1), COFC 0 (2),
Federal Circuit 0 (1).

## Checking our own filter (after grading, changes no verdict)

We read the matched rows after grading. These are corrections we owe readers, not a regrade.

- **The two COFC "procurement" rows are doubtful.** Both are pro se. The analysis counted them as
  procurement because a `Legal Field` label or the details contain "contract". One row's labels are
  "contract, employment", which looks like a federal-employment case, not a protest. If both are
  dropped, the 2025 count falls to 13 and A2 still fails. A3 still holds (2 of 13 vs 7 of 17), and
  no other verdict changes.
- **Three COFC rows were left out as non-procurement**, and that looks right. One of them is a
  rails-to-trails takings case from July 2026 with a lawyer party. It is the one money row that S1
  picks up: the database records a 5,000 USD fine and an adverse costs order. That is the only
  monetary penalty at any of these four tribunals in the database, and it is not a procurement
  case.
- **The Federal Circuit pattern also matched the Federal Circuit and Family Court of Australia** (11
  rows). Federal Circuit rows were reported only, none of them passed the procurement text test, and
  none is in A1-A6, so nothing changes. A future version should match the full U.S. name.
- **GAO's own page agrees on a lawyer row.** A design pilot fetched GAO's page for *Bramstedt
  Surgical Inc.*, B-424064 (28 Jan 2026), within GAO's robots.txt crawl delay. It lists "Neil C.
  Saucier, Esq., Saucier Law Office, for the protester", and the database marks that row "Lawyer".

## Limits

- The database is a growing, volunteer-fed collection, not a census, and none of these counts has
  a denominator. One sample `Pointer` value is "David Timm", so his finds feed the database. The
  coverage predictions are therefore not an independent check of his count.
- GAO does not publish every decision, and the tribunals do not all publish in the same way.
- The forum filter is code run on free text. The near-miss table in `results.json` lists every
  `Court` string with "Board", "Claims" or similar that we did not match, so anyone can audit it.
- Lawyer and pro se come from the database's `Party(ies)` labels, not from our own reading of each
  decision.

## Next

A prospective count from GAO's own legal-decisions feed (one request per 420 seconds, as GAO's
robots.txt asks), pre-registered before its first census fetch, will give the missing denominator:
the share of all published GAO protest decisions that discuss AI-fabricated authority. It will
also show how quickly such decisions reach the database.

## Prior art

- David P. J. Timm, Burr & Forman, ["How GenAI Misuse is Changing in Procurement
  Litigation"](https://www.burr.com/government-contracting/how-genai-misuse-is-changing-in-procurement-litigation)
  (11 Sep 2026), and his January 2026 report. These are hand counts, with no per-decision list
  and no lawyer/pro se numbers.
- As far as we found, nobody has published a per-decision open dataset or a numeric lawyer/pro se
  split for these forums. This write-up and `procurement_rows.csv` are a first, small one, built
  entirely on Charlotin's CC BY 4.0 data.
