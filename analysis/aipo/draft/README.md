# Draft coding, frozen before grading (1 November 2026)

This folder holds MV2's draft coding for the pre-registered count of AI clauses in court
protective orders ([pre-registration](../../ai-protective-orders-prereg.md),
[addendum](../../ai-protective-orders-prereg-addendum.md)). It is published **before any
count or prediction has been computed**, so that anyone can later compare the final coding
with this snapshot and see every change made after it.

- `ai_protective_orders-0.9.0.json`: 51 cases from the 29 posts in the fixed frame. 32 are
  coded from the order's own words, 3 are refusals, and 16 are listed as not codable because
  the posts describe those orders without quoting them. Nine further posts were screened out,
  each with a reason. Coding rules R1-R9 are in the file. R2-R9 were written while coding,
  after the frame was read; the pre-registration did not fix them, so the final write-up will
  report each prediction under the opposite reading of each rule as well.
- `src/velez-oneplus.txt`: passages of one order (Velez v. OnePlus, S.D.N.Y., ECF 28) copied
  from its free copy in the RECAP archive, because the post that cites it does not quote it.

What happens next: the pre-registration counts an order as "not codable" only if it also
cannot be read free at the source. A read-only check of CourtListener's RECAP archive found
free copies of 11 of the 16 described orders. Their text is being extracted in a sandboxed
job (the script and its list of PDFs will be published next to the grader), coded with the
same rules, and only then is the published grader (`../grade_aipo.py`) run. The result is published whichever way
the predictions go.

Not graded, not a result. Information about public court documents, not legal advice.
Coding CC BY 4.0; court text is public record; the blog posts in the frame are not reproduced.
Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
