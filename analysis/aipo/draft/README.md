# Draft coding, frozen before grading (1-2 November 2026)

This folder holds MV2's draft coding for the pre-registered count of AI clauses in court
protective orders ([pre-registration](../../ai-protective-orders-prereg.md),
[addendum](../../ai-protective-orders-prereg-addendum.md)). It is published **before any
count or prediction has been computed**, so that anyone can compare the final coding with
these snapshots and see every change made after them.

- `ai_protective_orders-0.9.0.json` (1 Nov): 51 cases from the 29 posts in the fixed frame.
  32 are coded from the order's own words, 3 are refusals, and 16 are listed as not codable
  because the posts describe those orders without quoting them. Nine further posts were
  screened out, each with a reason. Coding rules R1-R9 are in the file. R2-R9 were written
  while coding, after the frame was read; the pre-registration did not fix them, so the
  final write-up will report each prediction under the opposite reading of each rule as well.
- `patch-0.9.1.json` (2 Nov): the changes that turn 0.9.0 into 0.9.1. Whole cases are
  replaced by `case_id`, and nothing else changes:
  - seven orders the posts describe without quoting are coded from their own text, read
    free in the RECAP archive (Paula, Hawkins, Robinson, Stamp, Spatola and Morell, all
    S.D.N.Y. criminal cases, and James v. Cerebras, N.D. Cal.);
  - two anchors that pointed to the wrong post are corrected (Hintermaier and Brower are
    quoted in post 5724, not 5656), with their coding unchanged;
  - four RECAP copies (Jones, Sarris, DeJesus, Santos) have no usable text layer and are
    marked "pending OCR";
  - a new rule R10 says how orders read at the source are cited.
- `src/`: the order texts that the coding cites as `src:<case_id>`. `velez-oneplus.txt` holds
  passages copied by hand from the free PDF. The other files are pypdf 5.1.0 text of the
  free PDFs, with only CM/ECF page stamps and bare page numbers removed. Each file's first
  line names the PDF and its sha256. `recap_report-2026-11-01.json` lists per-page character
  counts and template-phrase probes for all 11 PDFs.
- The fetch script that made `src/` is `../recap_fetch.py`, with its tests and
  `../recap_manifest.json`.

Still to do before grading. The pre-registration counts an order as "not codable" only if
it also cannot be read free at the source, so first:
1. OCR the four image-only copies and code them;
2. finish checking four civil orders (Campbell, Fischman, Dunn, Elgin) for a free copy;
3. copy the Velez provisos.

Then the published grader (`../grade_aipo.py`) runs on the final file, and the result is
published whichever way the predictions go.

Seen while reading the courts' own copies (not a result): a post's "(same)" is not always
the same. The Robinson order the post calls the same as Lockhart lacks Lockhart's duties on
the government, and Stamp's certification rests on what the AI provider represents, which
Mora and Dygdon do not require.

Not graded, not a result. Information about public court documents, not legal advice.
The coding is CC BY 4.0, and court text is public record. The blog posts in the frame are
not reproduced. Made with AI agents working in the name of MV2 of Munim, Inc.
(mv2@munimtech.com).
