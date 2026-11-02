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
- `ai_protective_orders-0.9.1.json` (2 Nov): 0.9.0 with patch 0.9.1 applied, as built and
  checked by job aipo-build-v1. All 11 PDFs matched their pinned sha256, all 29 posts were
  unchanged, the grader's 13 tests passed, and its per-case check found 0 problems
  (39 codable, 3 refusals, 9 not codable).
- `patch-0.9.2.json` (2 Nov, later): the changes that turn 0.9.1 into 0.9.2:
  - the four image-only orders are coded from OCR text (new rule R11). Jones, DeJesus and
    Santos use the S.D.N.Y. template wording. **Sarris does not**: its definition of an
    "AI tool" leaves out "software that operates entirely on systems controlled by the
    defense, such that no Disclosure Materials are transmitted to any third party", it bars
    "consumer (i.e., non-commercial)" versions rather than "publicly accessible" ones, and
    it lets the defense use a tool once counsel has taken reasonable steps to confirm four
    safeguards (new rule R12 for the exclusion);
  - Campbell (D. Md.) and Elgin (N.D. Cal.) are final as not codable: a read-only check of
    the RECAP archive on 2 Nov found no free copy of either protective order;
  - Fischman (N.D. Tex.) and Dunn (D. Colo.) are marked "pending": a free copy of Fischman's
    protective order (ECF 58) was found, and Dunn's order granting the motion (ECF 32) is
    free, though its protective order (ECF 33) is not. Both are being read at the source.
- `src/`: the order texts that the coding cites as `src:<case_id>`. `velez-oneplus.txt` holds
  passages copied by hand from the free PDF. `us-v-jones-sdny.txt`, `us-v-sarris.txt`,
  `us-v-dejesus.txt` and `us-v-santos.txt` are tesseract 5.5.0 OCR text (300 dpi, not
  corrected by hand). The other files are pypdf 5.1.0 text of the free PDFs. In all of them
  only CM/ECF page stamps and bare page numbers are removed, and the first line names the
  PDF and its sha256. `recap_report-2026-11-01.json` lists per-page character counts and
  template-phrase probes for the first 11 PDFs.
- The build script is `../build_aipo.py`, with its tests and `../build_manifest.json`. It
  applies the patches, re-downloads and checks every PDF, rebuilds `src/`, re-reads the
  posts and runs the grader's check. With `--grade` it also grades P1-P6 on the coding and
  on each alternative reading, but it refuses while any case is still pending.

Still to do before grading:
1. code Fischman from its own text, and Dunn if ECF 32 sets out the provision's words;
2. copy the Velez provisos in full and code Velez under rule R9.

Then the published grader (`../grade_aipo.py`) runs on the final file, and the result is
published whichever way the predictions go.

Seen while reading the courts' own copies (not a result): a post's "same" is not always
the same. The Robinson order the post calls the same as Lockhart lacks Lockhart's duties on
the government. Stamp's certification rests on what the AI provider represents, which
Mora and Dygdon do not require. Sarris, grouped by the posts with the template orders, is
the only S.D.N.Y. criminal order read so far that names software running on the defense's
own systems.

Not graded, not a result. Information about public court documents, not legal advice.
The coding is CC BY 4.0, and court text is public record. The blog posts in the frame are
not reproduced. Made with AI agents working in the name of MV2 of Munim, Inc.
(mv2@munimtech.com).
