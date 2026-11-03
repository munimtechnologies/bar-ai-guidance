# AI protective-order study: coding versions (draft folder)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Coding and texts written here: CC BY 4.0. Code: Apache-2.0. Court documents are public record.
Information about public court documents, not legal advice.

This folder holds every version of the coding for the pre-registered count of AI clauses in
US court protective orders (`../../ai-protective-orders-prereg.md` and its addendum).
**The graded results are in [`../../ai-protective-orders.md`](../../ai-protective-orders.md)**; the final
data file is `../../../data/ai_protective_orders.json` (version 1.0.0).

## Versions

| Version | Date (2026) | What changed |
|---|---|---|
| `ai_protective_orders-0.9.0.json` | 1 Nov | 51 cases from the 29 frame posts: 32 coded from quoted text, 3 refusals, 16 not codable; 9 posts screened out. Rules R2-R9 were written while coding, so each prediction is also reported under the opposite reading of each rule. |
| `patch-0.9.1.json` | 2 Nov | Seven orders the posts only describe are coded from their free RECAP copies (R10); two anchors fixed; four image-only PDFs marked for OCR. Built file: `ai_protective_orders-0.9.1.json`, check `check-0.9.1.json` (0 problems). |
| `patch-0.9.2.json` | 2 Nov | The four image-only S.D.N.Y. orders coded from OCR text (R11). Sarris leaves software that runs entirely on the defense's own systems out of its AI-tool definition (R12). Campbell and Elgin final as not codable. Built file: `ai_protective_orders-0.9.2.json`, check `check-0.9.2.json` (0 problems, 2 cases pending). |
| `patch-1.0.0.json` | 2 Nov | **Final coding.** Fischman coded from the protective order itself (ECF 58). Dunn final as not codable. Velez recoded from its five provisos, now copied in full (R13). No case is pending. Built file: `../../../data/ai_protective_orders.json`, check `../check-1.0.0.json` (0 problems, 0 integrity failures). |

Versions 0.9.0 to 0.9.2 were on GitHub before any count was computed. Patch 1.0.0 was written and handed
to the grading job before any count was computed, but its first commit did not land, so it was first
published together with the results (3 Nov 2026). The results page shows that no coding of its three
cases could change any of the six outcomes.

The frame itself (each post's id, date, link, title and content hash, as fixed on 1 Nov 2026) is
`../frame.json`; blog post texts are not reproduced.

## The three cases settled in 1.0.0

- **Fischman v. Epic Systems Corp.** (N.D. Tex., No. 3:26-cv-00770-D, ECF 58, 23 Oct 2026), paras. 26-31,
  read from the free copy in the RECAP archive (`src/fischman-v-epic.txt`). Protected material may go into
  an AI platform only if "the provider of the AI Platform is contractually prohibited from" storing or
  training on inputs and from disclosing them beyond what the service needs, and must let the user require
  deletion. A self-hosted model has no outside provider, so the words do not settle it: coded **unclear**
  (rule R5, provider_contract), and also reported as forbidden.
- **Dunn v. LexisNexis Risk Solutions** (D. Colo.). The free order granting the motion (ECF 32,
  `src/dunn-v-lexisnexis.txt`) describes the agreed AI provision but does not set out its words, and the
  protective order (ECF 33) is available only from PACER. Final: **not codable**.
- **Velez v. OnePlus** (S.D.N.Y., No. 1:25-cv-02432, ECF 28). The order lists "self-hosted language models"
  among permitted systems, but only if five provisos hold (`src/velez-oneplus-provisos.txt`, pasted from
  the PDF's text layer and found once, word for word, in pypdf's extraction of the same PDF). A
  self-hosted model meets the first three; the fourth asks for a good-faith basis to believe "the platform
  contractually prohibits use of the information for generalized model training", and there is no outside
  provider to promise that. Coded **unclear** under rule R13 (self_hosted_contract_proviso), and also
  reported as permitted.

## How it is built and graded

`../build_aipo.py` (with `../test_build_aipo.py`, `../build_manifest.json`, `../patch-1.0.0.json` and
`../srcextra/`) downloads the frozen 0.9.0 file and the published patches, applies 1.0.0, re-downloads
every cited RECAP PDF and checks its pinned sha256, rebuilds each cited text (pypdf, or tesseract OCR for
image-only PDFs) and checks its pinned text hash, re-reads the 29 frame posts against their content hashes,
runs the published grader's tests and its word-for-word check of every quotation, and only then, with
`--grade`, grades P1-P6 on the coding and on every pre-declared alternative reading. It refuses to grade if
anything above fails.

Not legal advice.
