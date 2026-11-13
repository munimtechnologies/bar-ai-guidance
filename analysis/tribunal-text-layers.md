# Which tribunal archives post decisions a text search cannot see? Five archives, one test

Status: **descriptive note, 13 November 2026.** Not pre-registered; it re-reads the public `rows.csv` outputs of five censuses MV2 has already published. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public records, not legal advice.

## Short answer

MV2's tribunal censuses downloaded **5,009 decision PDFs** from five official archives and measured each one the same way: `pypdf` 5.1.0 text extraction, with "readable" meaning at least 300 characters of text. Four archives were fully readable. One was not.

| archive (census) | PDFs fetched | readable | no usable text layer |
|---|---:|---:|---:|
| U.S. Tax Court orders and opinions found by its search, 2023-2026 ([result](tax-court-citations.md)) | 78 | 78 | 0 |
| MSPB Board decisions, Jan 2024 - Nov 2026 ([result](mspb-citations.md)) | 3,567 | 3,567 | 0 |
| BIA and Attorney General precedent decisions, 2020-2026 ([result](bia-citations.md)) | 288 | 288 | 0 |
| New York Division of Tax Appeals and Tax Appeals Tribunal ([result](nydta-citations.md)) | 916 (1 more returned 404) | 916 | 0 |
| **USPTO Office of Enrollment and Discipline (OED) reading room, Jan 2023 - Nov 2026** ([result](uspto-oed-citations.md)) | 160 | 133 | **27** |

So **all 27 text-less PDFs in 5,009 come from one archive**, the USPTO's practitioner-discipline reading room at [foiadocuments.uspto.gov/oed](https://foiadocuments.uspto.gov/oed/). Each of the 27 yielded 1 character.

## Inside the OED archive: which decisions, and when

Read from the census's public [`rows.csv`](uspto-oed-citations/results/rows.csv) (decision type, date and character count for each of the 160 rows):

- **By kind of decision.** 26 of the 27 are plain **"Final Order"** files (26 of 117 such files, 22%); the 27th is a technical-standard notice (Tech_18). **None of the other 42 files** is image-only: 12 Final Decisions, 2 Initial Decisions, 18 decisions on reinstatement petitions, 9 other orders (amended final orders, disability-inactive orders, orders on reconsideration or on motions) and a moral-character decision. In OED's practice, a "Final Order" usually closes a settled or reciprocal matter; Final and Initial Decisions are contested rulings.
- **By time.** 2023: 6 of 44; 2024: 2 of 37; 2025: 3 of 44; **January to July 2026: 16 of 29** (16 of the 27 Final Orders in those months, 59%); **August to 10 November 2026: 0 of 6** (all 4 Final Orders in those months have text).
- **Scanned is not the same as text-less.** At least some readable Final Orders are scans too: the text layer of D2025-13, the 2025 reprimand over nonexistent cases, is OCR output that renders the rule number "11.101" as "I I.IOI". So the 27 look like scans that were posted **without the OCR step**, not a different way of making the documents. That is an inference from the files, not something OED has said.
- **What it hides.** One of the 16 is **D2026-16**, the July 2026 public reprimand over AI-generated citations that the press covered and the AI Hallucination Cases Database lists. A full-text search of the reading room, or any tool or model that reads its text, cannot find it.

## Why it matters

1. **Research and trackers.** Every census in this series counts what a tribunal's own records say. A file with no text layer is invisible to that kind of count, so OED's 2026 numbers were undercounted until a pre-registered OCR addendum ([Addendum 1](uspto-oed-citations/ocr/ADDENDUM-1.md), waiting for compute) reads the 27 a second way.
2. **Accessibility.** Federal agencies' public-facing electronic content falls under the Section 508 standards, which incorporate WCAG 2.0 Level A and AA (36 CFR part 1194, Appendix A, E205.2 and E205.4). A page image with no text is the case WCAG's criteria on non-text content (1.1.1) and images of text (1.4.5) are written for: a screen reader has nothing to read. Whether these files meet the standard is for the USPTO's Section 508 program to judge; the USPTO's [accessibility page](https://www.uspto.gov/using-usptogov/accessibility-uspto-website) invites reports of inaccessible content. MV2 plans to send the list of 27 proceeding numbers there once Addendum 1 has confirmed, with a second PDF tool, that they have no text layer.
3. **It may already be fixed going forward.** The newest six files (August to October 2026) all have text. Whether that is a change of practice or chance is not known from six files.

## Prior art

A search on 13 November 2026 found no published count of text-less PDFs in the OED reading room or a comparison across tribunal archives. The practitioner blog IPethics & INsights runs [its own search engine](https://ipethicslaw.com/new-uspto-discipline-search-engine-added-to-ipethics-insights/) over OED decisions with written summaries, and notes that the reading room's PDFs are not catalogued in any searchable way; it does not count text-less files.

## Limits

The FLRA census (310 decisions, all readable) is left out because it read the FLRA's decision web pages, not PDFs. One PDF library and one threshold (300 characters). A file can pass the threshold with poor OCR text and still defeat a search, so "readable" here is a floor, not a guarantee of accessibility. The four comparison archives cover different years and different kinds of decisions, and the Tax Court frame is only the documents its search returned. The OED counts cover only files dated 1 January 2023 to 10 November 2026. Counts can change if OED replaces files. No names are given here; the reading room publishes them.

Data: [`tribunal-text-layers/counts.csv`](tribunal-text-layers/counts.csv), derived by hand from the five censuses' published `rows.csv`/`results.json` files (OED rows fetched 2026-11-13 09:45-09:55 UTC). Text: CC BY 4.0. Code in the linked censuses: Apache-2.0.
