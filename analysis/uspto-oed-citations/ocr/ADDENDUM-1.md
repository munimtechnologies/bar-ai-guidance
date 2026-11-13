# Addendum 1 (pre-registered): OCR of the 27 OED decisions that census 1.0.0 could not read

Status: **frozen before any of the 27 decisions is OCR'd or read.** Written 2026-11-13 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `ocr_addendum.py` in this folder (Apache-2.0; it uses poppler-utils and Tesseract), tests in `test_ocr_addendum.py`. Before downloading anything, the job checks that this file and the code are public here and that its local code matches the newest committed copy. Information about public decisions of a federal agency, not legal advice.

## Why

[Census 1.0.0](../PLAN.md) read all 160 decisions dated 2023-01-01 to 2026-11-10 in the USPTO's OED reading room ([result](../../uspto-oed-citations.md)). 27 of them gave no text at all: their PDFs have no usable text layer, so the census counted them as unreadable, as the plan said it would. They are not spread evenly: **16 of the 35 decisions dated 2026 (46%)** against 11 of the 125 dated 2023-2025 (9%). One of the 16 is D2026-16, the July 2026 public reprimand over AI-generated citations that the press covered and the AI Hallucination Cases Database lists. So the census's prediction P1 could not be tested, and its counts may undercount. This addendum reads the 27 with OCR. **Census 1.0.0's verdicts stay as graded;** this addendum reports corrected counts beside them.

## What was seen before freezing, stated plainly

- From census 1.0.0's public `rows.csv`: each of the 27 rows' id, proceeding number, date, decision type and PDF SHA-256, and that each gave fewer than 300 characters with `pypdf`. None of their text has been read by anyone working on this study.
- From the database (CSV fetched by the census job on 2026-11-13) and the press: D2026-16 concerns AI-generated citations, quotations and parentheticals that pointed to nonexistent parts of a patent's specification, figures and prosecution history, ending in a public reprimand. So **A2 and A5 are pattern checks, not forecasts.** Nothing was seen about which rules D2026-16 cites beyond the press's "competence and misconduct", or whether it cites the USPTO's April 2024 AI guidance.

## Method

- The job re-reads the reading-room listing with census 1.0.0's own parser and row ids (its `census.py` is downloaded from commit `200007c`, SHA-256 checked) and picks the 27 rows by row id. It stops before fetching any decision if fewer than 25 are found.
- One request at a time, 3 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. Each PDF's SHA-256 is compared with the one census 1.0.0 recorded; a changed file is reported, not dropped.
- `pdftotext` (poppler) measures the text layer a second way. `pdftoppm` renders each page (first 60) at 300 dpi in grey, and Tesseract (English) reads it.
- The OCR text is classified with **census 1.0.0's frozen patterns unchanged** (`fake_cite`, `ai_mention`, `ai_citation`, `guidance`, the strict rule numbers). Census 1.0.0's hand check found that OCR'd text can render "11.101" as "I I.IOI", so the addendum adds **OCR-tolerant** rule-number and guidance patterns (`r11_18_tol`, `r11_101_tol`, `r11_804_tol`, `guidance_tol`), reported separately. **OCR-readable:** at least 300 characters after whitespace is collapsed.

## Predictions (fixed now)

- **A1 (check):** `pdftotext` also finds fewer than 300 characters in at least 25 of the 27 PDFs, so the census's "unreadable" reflects the files, not its PDF library.
- **A2 (pattern check, not blind):** the OCR text of D2026-16 has both a fabricated-citation phrase and an AI term by census 1.0.0's own patterns.
- **A3:** none of the other 26 OCR-readable decisions has a fabricated-citation phrase.
- **A4:** at most one of the other 26 mentions an AI term.
- **A5 (not blind):** D2026-16 cites 37 C.F.R. 11.101, the competence rule (strict or OCR-tolerant).
- **A6:** D2026-16 cites 37 C.F.R. 11.18, the signature and certification rule (strict or OCR-tolerant).
- **A7:** D2026-16 cites the USPTO's April 2024 AI guidance (89 FR 25609 or its title; strict or OCR-tolerant).
- **A8:** all 27 PDFs are fetched and OCR to at least 300 characters.

Each will be reported as held, failed or not testable. Afterwards the agents will read the full OCR text of every flagged decision and of D2026-16, report false matches and misses separately, and say which tribunal first caught D2026-16's citations and whether the database lists that first decision. They will also report, without names, what the 27 PDFs' own metadata says made them (e.g. a scanner or a print-to-PDF tool), since that may explain the 2026 jump.

## Outputs

`results.json`, `results.md`, `rows.csv` (row id, proceeding, date, fetch status, SHA match, pages, text-layer characters, OCR characters and flags) and `sources.json`. OCR texts, excerpts, PDF metadata and respondents' names stay private to the job.

## Limits

OCR makes errors, most of all on stamps, signatures and poor scans; a pattern can miss a garbled phrase. The addendum covers only the 27 rows census 1.0.0 could not read. It counts what decisions say, judges no practitioner or official, and is not legal advice.
