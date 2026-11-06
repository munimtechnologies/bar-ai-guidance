# Date audit of the hallucination-sanctions study: plan (audit 1.0.0)

*By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name. Information only, not legal advice. Text CC BY 4.0, code Apache-2.0.*

Committed on 2026-11-06, **before any decision document is fetched or read.** The job (`run_job.py`) checks that this plan and `audit.py` are public, and that its local `audit.py` matches the committed one, before it downloads anything.

## Why

The graded study ([write-up](../../hallucination-sanctions.md), pre-registration 65bd693, grading 32fdea8) put each US decision in a half-year using the `Date` column of Damien Charlotin's AI Hallucination Cases Database (CC BY 4.0). Its results hang on that column: P2 (median fine) rests on 16 amounts in 2025H1, and P3 (professional sanctions) failed by under one percentage point. If decision dates are wrong, some decisions sit in the wrong half-year.

## What we already know (read from the CSV columns, not from any decision document)

To be plain about what was seen before this plan:

- The graded snapshot (SHA-256 9201eecd..., fetched 2026-11-06 14:58Z) has 2,267 rows. 119 of their hosted file names end in a `DD-MM-YYYY` date.
- In the newest ~160 rows, about 25 file-name dates differ from the `Date` column, a few by months or years (for example a 2022 file-name date on a row dated September 2026).
- One US lawyer row has no `Date`. At least four US lawyer rows dated 2026H2 have file names dated in 2026H1. None of these five carries a fine or a professional sanction in the database, so moving them alone cannot flip P1-P5.
- A file name can carry the date of an earlier order or of the upload, so a different file-name date is **not** by itself an error. That is why this audit reads the documents.

## Frame

Every US row involving a lawyer (`Lawyer` among the parties) in the published `results/us_rows.csv` (602 rows), using that file exactly as graded. The document path comes from the current CSV export (`Source`, joined on `case_id`). Only documents the database hosts itself (`/documents/...pdf`) are fetched, one request a second. Text comes from pypdf, with no OCR. A document with under 200 characters of text counts as `no_text`. Pro se rows keep their recorded dates.

## Rules (frozen in `audit.py`)

- **Recorded date found:** the row's `Date` appears in the document text in a common US form (October 27, 2026; Oct. 27th, 2026; 27th day of October, 2026; 27 October 2026; 10/27/2026; 10/27/26; 10-27-2026; 2026-10-27), with digit boundaries.
- **ECF date:** the most frequent CM/ECF header date (`Filed MM/DD/YY`, `Entered on ... Docket MM/DD/YYYY`).
- **Same event:** two dates no more than 7 days apart.
- **C1 (document date first):** an ECF date more than 7 days from the recorded date replaces it. Otherwise, if the recorded date is not in the text, a file-name date that is in the text and more than 7 days away replaces it. Otherwise the recorded date stays.
- **C2 (conservative):** only rows whose recorded date is *not* in the text are corrected (ECF date first, then a file-name date found in the text, each only if more than 7 days away).
- **Sanity gate:** before any document is fetched, a regrade of the published rows with their recorded dates must reproduce the published P1-P5 numbers and verdicts exactly, or the job stops.

## Predictions (graded whichever way they go)

- **D1:** Among audited rows with a text layer and a recorded date, the recorded date appears in the document in **at least 85%**.
- **D2:** Among those with an ECF date, the recorded date is within 7 days of it in **at least 90%**.
- **D3:** C1 moves **fewer than 5%** of audited rows with a text layer into a different half-year.
- **D4:** Regraded under C1 and under C2, all five verdicts stay as published: P1, P2, P4 and P5 held, P3 failed. D4 holds only if both rules leave all five unchanged.

## What gets published

`date_audit.json` (counts, D1-D4, the three regrades), `date_audit_rows.csv` (one row per audited decision: dates, rule applied, no document text) and a write-up. Rows still in doubt are then read by hand and reported separately from the mechanical grade, which stays as computed. Decision documents are not republished. If the maintainer has already changed a date by the time of the fetch, `date_now` shows it.

## Limits

Mechanical date matching can miss unusual formats (false "not found") and can match a date that only appears in the body (false "found"). No OCR means scanned orders are not checked. ECF headers exist only for federal filings. The hand reading afterwards is meant to measure these errors, and the write-up will report them.
