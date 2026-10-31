# Addendum to the pre-registration: how the AI protective-order count is graded, and two questions about copied clauses

Written 31 October 2026, after `ai-protective-orders-prereg.md` was published and **before any post in its frame was read**. The sandboxed job that collects the frame had not yet run when this was written. By MV2 of Munim, Inc. (mv2@munimtech.com); this note and the grader were made with AI agents working in his name. Text CC BY 4.0, code Apache-2.0. It is about public court documents, not legal advice.

Nothing here changes the frame, the unit, the coding or predictions P1-P4 of the pre-registration. It fixes *how* they are checked, and adds two secondary predictions (P5, P6).

## The grader, published first

`analysis/aipo/grade_aipo.py` (standard library only, with unit tests in `analysis/aipo/test_grade_aipo.py`) reads the coded data file and the order texts and refuses to grade if any check fails:

- **Spans, not retyped text.** Each case points to the order's own words by a start anchor and an end anchor in a frame post (`post:<id>`) or in a text read at the source (`src:<name>`). The start anchor must occur exactly once. Spans cover only the court's words, normally a block quote, never the blog author's commentary.
- **Every call is checked.** Each test code (BAN, PUBLIC, OPENNESS, DATA, CONTRACT, NOTICE, OTHER), each "named" call and each setup-A code carries a quotation that must appear word for word in that case's span text ("..." may skip words, in order). An "unclear" setup-A code must give a reason; a "not codable" case must say why.
- **Thresholds are exact.** With n codable orders: P1 holds if 5 x (self-hosting named) <= n; P2 if 2 x (DATA) >= n; P3 if 4 x (OPENNESS) <= n and no OPENNESS order codes setup A as permitted; P4 if 2 x (permitted) >= n and 5 x (forbidden) <= n. Under 10 codable orders, every prediction is reported as "too small to grade", with the counts.

The order text of every case (the extracted spans) is published with the result. The blog posts themselves are not republished; `frame.json` keeps each post's link and content hash so anyone can fetch the same version and re-run the grader.

## Two more questions: are AI clauses copied from templates?

*RMME LLC v. Majestic Steel USA, Inc.* (D. Nev., ECF 20, 24 June 2026) defines "open" and "closed" AI systems in the same words as a sample clause an e-discovery vendor published in September 2026, which suggests that some AI clauses travel as templates. No count of how often this happens was found. The grader measures it mechanically: for every pair of codable cases, the longest run of words (lower-cased letters and digits) that their AI texts share.

- **P5.** At least one pair of codable cases **from different courts** shares a run of 25 or more words.
- **P6.** At most one third of codable cases share a run of 25 or more words with any other codable case: copied clauses exist, but most AI clauses are drafted case by case.

Limits fixed now: blog posts often quote only part of an order, so shared runs are a lower bound; a shared run shows common wording, not who copied whom; two cases with the same lawyers in the same court may share wording for that reason alone, which is why P5 requires different courts. Every pair at or above 25 words is listed with its length, and every case's longest run is published, whichever way P5 and P6 go.
