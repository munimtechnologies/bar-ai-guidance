# Pre-registration: are US courts "ratcheting up" sanctions for AI-hallucinated filings?

*By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
Information only, not legal advice. Text CC BY 4.0; code Apache-2.0.*

Version 1.0.0, written 2026-11-06 before any data row was read. The analysis code
(`analyze.py`, Apache-2.0) is committed in the same commit and is the grader. The job wrapper
(`run_job.py`) refuses to download the data until this file is public on GitHub and the
committed `analyze.py` matches the one it runs.

## Question

Commentary often says that courts are escalating sanctions for filings with AI-fabricated
citations. Examples: the article "Two Years of Fake Cases and the Courts are Ratcheting up
the Sanctions" on the Massachusetts Board of Bar Overseers' site, vendor trackers that compare the
$5,000 *Mata v. Avianca* sanction (2023) with the $110,204 *Couvrette v. Wisnovsky* award
(2026), and EDRM's "$145K in Q1 penalties". These compare landmark cases or add up totals,
and totals grow with the number of decisions. **We found no published per-decision count of
whether a US decision involving a lawyer is now more likely to carry a monetary penalty, or a
larger one, than a year earlier.** This study measures that.

## Data

AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0), CSV export
`/hallucinations/hallucinations/download.csv`, downloaded once by the job after this file is
public. The job records the download time and SHA-256 and publishes the derived US rows.

The database is a collection of decisions that came to its author's attention, not a census
of filings. Its coverage has grown fast (a mid-2025 blog post cited over 120 cases; the page listed 2,266 on 5 Nov 2026), so
a change over time can come from what gets collected as well as from what courts do. The result
will be read as a description of the database, and this limit will be stated next to it.

## What we knew before writing this

- The page summary: 2,266 cases (1,535 USA), party counts across all countries (Pro Se
  Litigant 1,305, Lawyer 898), monetary penalties stored as "amount CUR", and "1 USD" entries
  that look like placeholders.
- Vaquill's pooled analysis of the 12 Oct 2026 CSV: 587 US lawyer entries, 158 with an amount
  above $1, median $3,000, 116 with a professional-sanction flag, and lawyer entries per year
  4 / 14 / 207 / 361 (2023-2026). It gives no amounts or shares by period.
- To write the parser we read the CSV's 19 column names and a description of the value
  *formats* (dates YYYY-MM-DD; parties joined by "; "; penalties like "750 USD", sometimes
  with no currency; Yes/No flags). We asked for formats only, and the summary we read was
  drawn from the first ~100 rows. We saw no per-period figure of any kind.

## Definitions (as coded in analyze.py 1.0.0)

- **US decision:** `State(s)`, split on `;` or `,`, has a token `USA` (or `USA (...)` or
  `United States`, should those appear). The results list the 15 most common `State(s)` and party
  values so this rule can be checked.
- **Lawyer decision:** `Party(ies)`, split on `;`, contains exactly `Lawyer`. **Pro se decision:** contains
  exactly `Pro Se Litigant`. A decision can be both.
- **Period:** half-year of `Date` (H1 = Jan-Jun). Primary comparison: **A = 2025H1 vs
  B = 2026H1** (same season, a year apart; 2026H2 is still being collected).
- **Monetary penalty (primary):** `Monetary Penalty` holds an amount of at least 1 in any currency,
  or a non-empty value that does not parse as an amount. **Amount statistics** use only amounts
  above 1 in USD (or with no currency code); "1" placeholders and other currencies are left out.
  Amounts are as recorded and may include fee awards as well as penalties.
- **Professional sanction:** `Professional Sanction` = `Yes`.
- **Minimums:** a share prediction needs at least 30 decisions in each period compared; a median
  prediction needs at least 10 USD amounts in each. Below that it is graded "not testable".
- Tests are one-sided permutation tests (10,000 permutations, seed 20261106), reported next to each
  prediction. **The verdicts follow the pre-stated direction or threshold, not the p-values.**

## Predictions

- **P1 (no ratchet in frequency).** The share of US lawyer decisions that carry a monetary penalty
  is not more than 5 percentage points higher in 2026H1 than in 2025H1. *Why:* as collection
  widens, more routine show-cause and warning decisions enter, which should hold the share flat or
  lower.
- **P2 (ratchet in size).** Among US lawyer decisions with a USD amount, the median amount is higher
  in 2026H1 than in 2025H1. *Why:* published orders increasingly cite earlier sanctions as not having
  deterred, and fee-shifting awards are getting larger.
- **P3 (ratchet in discipline).** The share of US lawyer decisions with a professional sanction
  (referral, suspension and the like) is higher in 2026H1 than in 2025H1.
- **P4 (pro se is fined less).** In each of 2025H1, 2025H2 and 2026H1, US decisions involving a pro se
  litigant carry a monetary penalty less often than US decisions involving a lawyer.
- **P5 (most decisions end without money or discipline).** In 2026H1, fewer than half of US lawyer
  decisions carry a monetary penalty or a professional sanction.

## Sensitivity analyses (reported, not graded)

S1 drops rows flagged `Alleged` = Yes (AI use alleged but not confirmed). S2 counts any party
label containing "lawyer" (for example "Government Lawyer"). S3 counts a penalty only if its
amount is above 1. S4 compares calendar 2025 with 2026 to date. We will also publish half-year
tables (2023H1-2026H2) for lawyer and pro se decisions: n, share with a monetary penalty,
median, 75th percentile and maximum USD amount, share of amounts of $10,000 or more, and share
with a professional sanction.

## Rules

Any change to the code or the definitions after this commit is an amendment. It will be
committed with a reason *before* the data is read, or, if it comes later, reported next to the
result with both versions' answers. All predictions are reported whichever way they come out.
The database is Damien Charlotin's work. This study only re-counts it, and any coding questions
belong to the database, not to the courts.
