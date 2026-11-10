# Amendment 1 to the FLRA archive AI-citation census (census 1.0.0 -> 1.0.1): listing parser only

Written 2026-11-10 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com), **before any decision text in the frame was read by code**. [PLAN.md](PLAN.md) stays as committed. The frame, definitions, predictions, thresholds and grading are unchanged. Information about public decisions, not legal advice.

## What happened

The first job (`flraai-v1`, 2026-11-10 13:35-13:38 UTC) passed its unit tests and confirmed that its `census.py` matched the committed copy. It downloaded the AI Hallucination Cases Database CSV, which held 1 FLRA row. It then **stopped as the plan requires**: the frame held 0 decisions, so no decision page was fetched. Its log: `7 listing pages, 0 in frame, 58 undated listing rows`, and `listing page 6: no rows parsed`. The status and sources files are published in `runs/flraai-v1/`.

## Why: two parser faults, found from listing pages only

The agents looked at the saved first listing page and at two more listing pages (pages 7 and 36, read on flra.gov). These pages show only citation numbers, dates, case numbers and parties. No decision text was read.

1. **Each decision fills two table rows.** The first row holds the citation, issuance number and issuance date. The second holds the PDF, HTML and digest links and the parties. Version 1.0.0 read each row on its own, so a row with a link never had a date. That gave 58 undated rows and none in the frame.
2. **Older decisions link to `.html` pages.** Recent ones use `https://www.flra.gov/decisions/v74/74-89`. Earlier ones, from page 7 on, use `.../v74/74-29.html`, and the link pattern did not allow a dot. Page 7 (`page=6`) therefore parsed no rows, and the listing stopped there.

## Changes in census.py 1.0.1 and run_job.py

- `parse_flra_listing`: a row with no decision link is carried forward and read together with the next row that has one, so the date and the link come from the same decision. The link pattern accepts a `.html` ending. A decision listed with a PDF but no HTML link is no longer dropped. It stays in the frame with no link and counts as not readable (`doc_status` `no_html_link`), as an unreadable page would under the plan.
- `run_job.py`:
  - An empty listing page is fetched once more after 60 seconds, and only two empty pages in a row end the listing.
  - **New stop:** if the listing never reaches decisions issued before 2022-01-01, the frame is incomplete. The job then stops before any decision text is fetched (exit 7), in the same way as the existing under-20 stop.
  - Duplicates are counted by citation.
  - The job waits until this amendment is public and the newest committed `census.py` is identical to its own.
- New tests use the live two-row layout, `.html` links, a PDF-only row and a header-only page (`test_census.py`). An offline test of the listing loop covers an empty page in the middle and an incomplete listing (`test_run_job.py`).

The classification patterns, the 1,500-character readability threshold, the database match and all seven predictions are byte-for-byte as in 1.0.0. Only the `VERSION` string, the module notes, `FLRA_HREF`, the new `FLRA_PDF` and `parse_flra_listing` differ.

## What this lets the agents know in advance

From the three listing pages: the list holds 10,462 Authority decisions across all years, 10 per page. 2026 decisions run up to 74 FLRA No. 89 (30 October 2026). Page 36 is already at June-July 2021. So the frame from 2022-01-01 to 2026-11-10 should hold roughly 300 decisions, read at 3 seconds apart. This was not known when the predictions were fixed. Nothing about it bears on any prediction except P7, whose 50-decisions-per-year test may leave it not testable if the FLRA issued fewer than 50 decisions in 2023 or 2026.
