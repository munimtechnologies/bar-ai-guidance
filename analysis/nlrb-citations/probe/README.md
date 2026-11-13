# NLRB sizing probe (13 November 2026)

Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code Apache-2.0, text and counts CC BY 4.0. Information about public decisions, not legal advice.

Before pre-registering the [NLRB census](../PLAN.md), a small job (`handcheck-nlrb-v1`, run 13 November 2026, 08:30-08:33 UTC) ran `probe.py`. It is not a census and grades nothing. It did three things:

1. Fetched *Rivas Painting, Inc.*, 374 NLRB No. 30, so the agents could read the decision itself rather than the Board's weekly summary. Result: see the [hand-checked list](../../agency-hand-list.md).
2. Read the first 19 pages of the NLRB's public Board-decisions listing, newest first, until a page held only decisions from before 2024: 380 rows, volumes 372 (26), 373 (147), 374 (141) and 375 (66); by listed date 34 in 2023, 155 in 2024, **8 in 2025** and 183 in 2026. Every row had an NLRB document id and a case number. See `listing.json`.
3. Fetched the three newest listed decisions (375 NLRB Nos. 68, 67 and 65) through nlrbresearch.com's mirror of the NLRB's documents, to check that the mirror serves them; all four fetches (with *Rivas*) succeeded. One of the three, 375 NLRB No. 65 (*Pepperjacks*), turned out to describe citations that do not exist. See `docs_public.json` (counts of a few search phrases per document, no text).

The listing pages, texts and excerpts were kept private to the job. The probe asked nlrb.gov for one page every 3 seconds and never requested `apps.nlrb.gov/link/`, which that site's robots.txt disallows.
