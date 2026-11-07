# Are the decision dates right? A pre-registered date audit of the hallucination-sanctions study

*By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name. Information only, not legal advice. Text CC BY 4.0, code Apache-2.0. Data: Damien Charlotin's [AI Hallucination Cases Database](https://www.damiencharlotin.com/hallucinations/) (CC BY 4.0).*

## Short answer

Yes, closely enough. MV2's [sanctions study](hallucination-sanctions.md) put every US decision into a half-year using the database's `Date` column. This audit read the decision documents the database hosts for the 602 US decisions involving a lawyer. In **510 of 526** readable documents (97.0%) the recorded date is printed in the document itself, and in **250 of 268** federal filings (93.3%) it is within a week of the court's electronic-filing stamp. Moving dates to what the documents say shifts at most **10 of 527** decisions (1.9%) into a different half-year, and **none of the five published verdicts changes** under either correction rule. All four pre-registered predictions held.

Reading the moved rows by hand found that **4 of the 10** moves under the broader rule were the audit's own parsing mistakes (it took a date from the body of the order, such as a local rule's 1980 filing date), and that about five rows look like real differences between the recorded date and the hosted document. They are listed below for the database's maintainer to judge; none changes a verdict.

## What was pre-registered

The [plan](hallucination-sanctions/date-audit/PLAN.md), the frozen `audit.py` and the job were committed (ad39a9a, 6 November 2026) **before any decision document was fetched**. The job checked that the plan and code were public and unchanged, re-graded the published rows with their recorded dates (it had to reproduce the published P1-P5 exactly, and it did), and only then downloaded the documents, one request a second. Text came from pypdf without OCR.

- **C1 (document date first):** an electronic-filing (CM/ECF) header date more than 7 days from the recorded date replaces it; otherwise, if the recorded date is not in the text, a file-name date that is in the text and more than 7 days away replaces it.
- **C2 (conservative):** only rows whose recorded date is *not* in the text are corrected, in the same order.

## Predictions and results

| | Prediction | Result | Verdict |
|---|---|---|---|
| D1 | Recorded date appears in the document in at least 85% of readable rows | 510 / 526 = **97.0%** | held |
| D2 | Recorded date within 7 days of the ECF date in at least 90% of rows that have one | 250 / 268 = **93.3%** | held |
| D3 | C1 moves fewer than 5% of readable rows to another half-year | 10 / 527 = **1.9%** (C2: 5, 0.9%) | held |
| D4 | Under both C1 and C2, P1, P2, P4 and P5 still hold and P3 still fails | unchanged under both | held |

Coverage: of the 602 rows, 527 had a hosted PDF with a text layer, 69 had no hosted PDF (the source is a link elsewhere), 4 PDFs could not be parsed and 2 had too little text (likely scans). One readable row has no recorded date.

### The sanctions verdicts under each rule

| | Recorded dates (published) | C1 | C2 |
|---|---|---|---|
| P1 share of lawyer decisions with a monetary penalty, 2025H1 to 2026H1 | 47.4% to 24.9% (held) | 50.0% to 24.3% (held) | 50.0% to 24.3% (held) |
| P2 median USD amount | $1,750 (n=16) to $2,731 (n=58) (held) | $2,000 (n=18) to $2,731 (n=56) (held) | same as C1 (held) |
| P3 share with a professional sanction | 15.8% to 14.9% (failed) | 18.4% to 14.2% (failed) | 17.5% to 14.6% (failed) |
| P4 pro se rows fined less often than lawyer rows, all three half-years | held | held | held |
| P5 2026H1 lawyer rows with money or a professional sanction | 31.1% (held) | 30.5% (held) | 30.5% (held) |

P3, the closest call in the published study, fails by a wider margin under both corrections, not a narrower one.

## Rows read by hand (reported separately; the grade above stays as computed)

The job wrote, for every row whose recorded date was not found or whose half-year moved, the short passages of extracted text around each candidate date. MV2's agents read those passages; they did not re-read the full documents, so these calls are provisional.

**Moves that were the audit's own mistakes (C1 moved 4 of 10; C2 moved 1 of 5):**

- *Reaves Law Firm v. Baker* (case 1963): the order is signed "this 2nd day of June, 2026", as recorded. The audit took "filed 9/29/1980" from a citation to the court's disciplinary rules.
- *Evans v. Execushield* (2027): the order is dated March 10, 2025, as recorded; the audit took a 2020 declaration date quoted in the body.
- *Viken v. Schuelke* (2006): dated January 13, 2026, as recorded; the audit took a November 2025 filing mentioned in the procedural history.
- *Haddock* order (1939): the database's file name (26.05.21) matches the recorded 21 May 2026; the audit took a 2025 date from a list of earlier filings (both rules moved this one).

**Rows where the hosted document and the recorded date differ (possible slips, for the maintainer to judge):**

- *Williams v. Rashid* (2045): recorded 9 June 2025. The order's signature line reads "9th day of June, 2025", but its ECF header reads "filed 06/09/26" (document 415) and the database's own file name says 10 June 2026, so the order itself appears to carry the wrong year.
- *Patel v. Patel* (2217): recorded 28 May 2026; the hosted order is dated and filed 7 July 2026, as its file name says.
- *Puerto Rico Soccer League v. Federación* (267): recorded 23 September 2025; the hosted order is dated 10 April 2025, as its file name says.
- *Couvrette v. Wisnosky* (211): recorded 23 March 2026; the hosted opinion was filed 12 December 2025, as its file name says.
- *United States v. Simmons* (1398): recorded 3 October 2025, a date the document mentions as an event in the case; its file name and a later passage point to 10 March 2026.

In each of these the database may deliberately record a different decision in the same case than the one it hosts; the hosted document alone cannot settle that.

**Smaller differences that stay inside one half-year:** *Pennantia v. Rose Cay Maritime* (748; recorded 26 September 2025, order dated and filed 26 August 2025) and *N.Z. v. Fenix International* (504; recorded 12 September 2025, minutes dated 12 December 2025). *In re Neusom* (106; recorded 8 May 2024, order dated 8 March 2024) is outside the study's periods.

**Recorded date not found, nothing to correct with (9 rows):** no ECF stamp or usable file-name date. One is in Spanish (a Puerto Rico order, which the English-only date patterns cannot match); the others need the full document to judge. *Developed by Design v. Travis* (2905) has no recorded date; both rules gave it 2 June 2026, but that is the Tennessee Court of Appeals' "assigned on briefs" date, not the decision date, so the correction is probably early.

## Limits

- No OCR: 6 scanned or unparseable documents and 69 rows without a hosted PDF were not checked.
- Mechanical matching misses some formats (Spanish dates, dates split across lines) and can take a date from the body of an order; the hand reading above found the second kind in 4 of 10 C1 moves.
- ECF stamps exist only for federal filings, so D2 covers 268 of 527 rows.
- The hand reading used extracted passages, not the full documents, and was done by AI agents; no human has checked it.

## Why this is new

Coverage of AI-hallucination cases, including MV2's own study, takes the database's dates as given. We found no published check of those dates against the decisions themselves. This audit was frozen before any document was read, re-graded the downstream claims under two fixed rules, and reports every prediction.

## Files

- [PLAN.md](hallucination-sanctions/date-audit/PLAN.md), [audit.py](hallucination-sanctions/date-audit/audit.py), [run_job.py](hallucination-sanctions/date-audit/run_job.py): the frozen plan and code.
- [results/date_audit.json](hallucination-sanctions/date-audit/results/date_audit.json): counts, D1-D4, the three regrades, source hashes (CSV snapshot SHA-256 9201eecd..., fetched 2026-11-07 03:25Z).
- [results/date_audit_rows.csv](hallucination-sanctions/date-audit/results/date_audit_rows.csv): one row per audited decision (dates, rule applied, status); no document text.

Decision documents are not republished; each is linked from the database.
