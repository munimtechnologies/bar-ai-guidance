# Pre-registration: AI-fabricated authority at US federal procurement tribunals (analysis 1.0.0)

Status: **frozen before any data row is read.** Written 2026-11-08 by AI agents working in MV2's
name (MV2, Munim, Inc., mv2@munimtech.com). Code: `analyze.py` in this folder (standard
library only, Apache-2.0), tests in `test_analyze.py`, job wrapper `run_job.py`. The job checks
that this PLAN and `analyze.py` are public in this repository and that its local `analyze.py` is
identical to the committed one before it downloads anything. Information only, not legal advice.

## Question

How often do GAO bid protests, the U.S. Court of Federal Claims (procurement cases), the Armed
Services Board of Contract Appeals (ASBCA) and the Civilian Board of Contract Appeals (CBCA) issue
decisions about AI-fabricated or AI-garbled authority? Who files them, lawyers or companies acting
for themselves? Are they ever sanctioned with money?

## Prior art (read 2026-11-07/08)

- David P. J. Timm, Burr & Forman, "How GenAI Misuse is Changing in Procurement Litigation"
  (11 Sep 2026). He counted the decisions by hand: 23 in 2025 with 3 sanctions, and 20 in 2026
  "current through the end of July, 2026" (GAO 12, COFC 2, Fed. Cir. 1, ASBCA 4, CBCA 1, with 3
  sanctions: ASBCA 2, CBCA 1). He describes one serial protester with at least 23 GAO protests
  between April 2025 and July 2026, and says lawyers "are now a substantial part of the problem".
  He publishes no per-decision list, no lawyer/pro se numbers and no dataset.
- Washington Technology (Oct 2025) reported 9 GAO decisions with non-existent citations since May
  2025. Law-firm posts cover single decisions.
- We found no open per-decision dataset and no numeric lawyer/pro se split for these forums.

## Data

AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0), the full CSV export, downloaded by
the job after this PLAN is public. The SHA-256, size and time are recorded.

**What has been seen before freezing, stated plainly.** MV2's earlier pre-registered sanctions
study (`analysis/hallucination-sanctions/`) processed the whole CSV by code. Its published rows
carry no forum column, and nobody tallied or read its procurement-tribunal rows. A scouting job on
2026-11-07 (snapshot SHA-256 `9201eecd...`, 2,175,509 bytes) recorded only the column names and
sample values of the short label columns. It found that the forum is not a label column: it sits
in the free-text `Court` column, which the scout did not print. One sample value of the `Pointer`
(contributor) column is "David Timm", so Timm's own finds probably feed the database, and the
coverage predictions below are not independent of his count. No count of procurement rows, no
`Court` value and no case name from these forums had been seen when this plan was written.

## Definitions (as coded in analyze.py)

- **Forum** comes from the `Court` text, first match in this order: Federal Circuit ("Court of
  Appeals for the Federal Circuit", "Federal Circuit", CAFC, "Fed. Cir."), COFC ("Court of Federal
  Claims", COFC, "Fed. Cl."), ASBCA, CBCA (full names or abbreviations), GAO ("Government
  Accountability Office", "General Accounting Office", "Comptroller General", GAO). Abbreviations
  are matched case-sensitively as whole words.
- **Procurement row (core):** every GAO, ASBCA and CBCA row. A COFC row counts only if its legal-field
  labels, case name or details mention protest, procure, solicitation, contract, bid, bidder,
  offeror or award, because the court also hears vaccine, tax, takings and pay cases. Federal
  Circuit rows that pass the same text test are reported but are not part of A1-A6.
- **Lawyer / pro se:** `Party(ies)` contains the token `Lawyer` / `Pro Se Litigant`.
- **Money:** `Monetary Penalty` holds an amount above 1 (the database uses 1 as a placeholder) or text
  that is not a plain amount.
- **Date windows** use the `Date` column (ISO dates; others count as undated): 2025 = 2025-01-01 to
  2025-12-31; Jan-Jul 2026 = 2026-01-01 to 2026-07-31; Jan-Oct 2026 = 2026-01-01 to 2026-10-31.
- **Protester key:** the case name before the first comma, "--", dash, bracket, "d/b/a" or "v.",
  with "Matter of:", B-numbers and company suffixes (LLC, Inc., Corp., JV and similar) removed,
  lower-cased. A key is printed only if the name carries a company suffix. Otherwise it is
  withheld.

## Predictions (fixed now)

- **A1 (coverage, 2026):** at least 15 core rows dated Jan-Jul 2026 (Timm counts 19 at these four
  forums).
- **A2 (coverage, 2025):** at least 17 core rows dated in 2025 (Timm: 23 in all, forum split not given).
- **A3 (lawyers rising):** the share of core rows with a lawyer party is higher in Jan-Oct 2026 than
  in 2025. Not testable if either period has fewer than 8 rows.
- **A4 (GAO is mostly pro se):** at least 60% of GAO rows dated 2025-01-01 to 2026-10-31 list a pro se
  litigant. Not testable below 10 rows.
- **A5 (no money):** at most 1 core row dated 2025-01-01 to 2026-10-31 records a monetary penalty.
  These forums mostly answer with dismissals, warnings or struck filings. Not testable below 10 rows.
- **A6 (one serial filer):** the most frequent protester key accounts for at least 25% of GAO rows
  dated 2025-01-01 to 2026-10-31. Not testable below 10 rows.

Each prediction is reported as held, failed or not testable, every one of them, either way.

## Sensitivity (reported, not graded)

S1 counts every COFC row. S2 also takes the forum from the case name or source when `Court` gives
none (a GAO B-number, ASBCA or CBCA). S3 drops rows marked `Alleged` = Yes.

## Outputs

`results.json`, `results.md` and `procurement_rows.csv` (case_id, forum, date, parties, penalty,
flags; no case names). There is also a table of every matched `Court` string, and of near-miss
strings that were not matched, so anyone can audit the filter. The raw CSV is not republished.
Read it at the source.

## Limits

The database is a growing collection, not a census. Its coverage of these forums may depend on a
few contributors. GAO publishes only some of its decisions, and none of these counts has a
denominator. A forum filter run on free text can miss rows or catch the wrong ones. The
near-miss table is there so readers can check. A planned prospective study will count new GAO
decisions from GAO's own feed at the pace its robots.txt asks for (one request per 420 seconds),
which gives a denominator. This is not legal advice and not advice on any protest.
