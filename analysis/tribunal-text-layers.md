# Which tribunal archives post decisions a text search cannot see? Six archives, one test

Status: **descriptive note, 13 November 2026, updated 14 November 2026.** Not pre-registered; it re-reads the outputs of censuses MV2 has already published. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public records, not legal advice.

## Short answer

MV2's tribunal censuses downloaded **6,858 decision PDFs** from six official archives and measured each one the same way: `pypdf` 5.1.0 text extraction, with "readable" meaning at least 300 characters of text. Four archives were fully readable. Two were not, and they differ.

| archive (census) | PDFs fetched | readable | no usable text layer |
|---|---:|---:|---:|
| U.S. Tax Court orders and opinions found by its search, 2023-2026 ([result](tax-court-citations.md)) | 78 | 78 | 0 |
| MSPB Board decisions, Jan 2024 - Nov 2026 ([result](mspb-citations.md)) | 3,567 | 3,567 | 0 |
| BIA and Attorney General precedent decisions, 2020-2026 ([result](bia-citations.md)) | 288 | 288 | 0 |
| New York Division of Tax Appeals and Tax Appeals Tribunal ([result](nydta-citations.md)) | 916 (1 more returned 404) | 916 | 0 |
| California Office of Tax Appeals opinions, 2024 - Nov 2026 ([result](ota-citations.md); added 14 Nov 2026) | 1,849 (27 more not reached) | 1,832 | **17** (0.9%) |
| **USPTO Office of Enrollment and Discipline (OED) reading room, Jan 2023 - Nov 2026** ([result](uspto-oed-citations.md)) | 160 | 133 | **27** (17%) |

The first version of this note (13 November, five archives) said that all 27 text-less PDFs came from the USPTO's reading room. With the sixth archive that is no longer true: **44 of 6,858 are text-less, 27 at the USPTO OED and 17 at California's OTA.** The two patterns are different:

- **OED: many, recent, all-or-nothing.** Each of its 27 yielded 1 character; 16 of them are from January to July 2026 (details below).
- **OTA: few, older, near-empty.** Its 17 yielded 58 to 261 characters each, all are 2024 opinions (17 of 656 fetched from 2024; 15 from the franchise-and-income-tax page, 2 from business tax), and **none of the 1,193 opinions from 2025 and 2026** fell below the threshold. A few dozen to a few hundred characters is what a page stamp or footer leaves when the body is an image, but we have not opened the 17 to confirm that they are scans.

## Inside the OED archive: which decisions, and when

Read from the census's public [`rows.csv`](uspto-oed-citations/results/rows.csv) (decision type, date and character count for each of the 160 rows):

- **By kind of decision.** 26 of the 27 are plain **"Final Order"** files (26 of 117 such files, 22%); the 27th is a technical-standard notice (Tech_18). **None of the other 42 files** is image-only: 12 Final Decisions, 2 Initial Decisions, 18 decisions on reinstatement petitions, 9 other orders (amended final orders, disability-inactive orders, orders on reconsideration or on motions) and a moral-character decision. In OED's practice, a "Final Order" usually closes a settled or reciprocal matter; Final and Initial Decisions are contested rulings.
- **By time.** 2023: 6 of 44; 2024: 2 of 37; 2025: 3 of 44; **January to July 2026: 16 of 29** (16 of the 27 Final Orders in those months, 59%); **August to 10 November 2026: 0 of 6** (all 4 Final Orders in those months have text).
- **Scanned is not the same as text-less.** At least some readable Final Orders are scans too: the text layer of D2025-13, the 2025 reprimand over nonexistent cases, is OCR output that renders the rule number "11.101" as "I I.IOI". So the 27 look like scans that were posted **without the OCR step**, not a different way of making the documents. That is an inference from the files, not something OED has said.
- **What it hides.** One of the 16 is **D2026-16**, the July 2026 public reprimand over AI-generated citations that the press covered and the AI Hallucination Cases Database lists. A full-text search of the reading room, or any tool or model that reads its text, cannot find it.

## Why it matters

1. **Research and trackers.** Every census in this series counts what a tribunal's own records say. A file with no text layer is invisible to that kind of count, so OED's 2026 numbers were undercounted until a pre-registered OCR addendum ([Addendum 1](uspto-oed-citations/ocr/ADDENDUM-1.md), waiting for compute) reads the 27 a second way. At the OTA the effect is small and confined to 2024, the year in which the census found no fabricated-citation opinion among the readable ones.
2. **Accessibility.** Federal agencies' public-facing electronic content falls under the Section 508 standards, which incorporate WCAG 2.0 Level A and AA (36 CFR part 1194, Appendix A, E205.2 and E205.4). A page image with no text is the case WCAG's criteria on non-text content (1.1.1) and images of text (1.4.5) are written for: a screen reader has nothing to read. Whether these files meet the standard is for the USPTO's Section 508 program to judge; the USPTO's [accessibility page](https://www.uspto.gov/using-usptogov/accessibility-uspto-website) invites reports of inaccessible content. MV2 plans to send the list of 27 proceeding numbers there once Addendum 1 has confirmed, with a second PDF tool, that they have no text layer. (California's state agencies have their own accessibility rules; we make no claim about the 17 OTA files until they have been opened.)
3. **It may already be fixed going forward.** The newest six OED files (August to October 2026) all have text, and every OTA opinion from 2025 and 2026 has text. Whether OED's change is a change of practice or chance is not known from six files.

## Prior art

A search on 13 November 2026 found no published count of text-less PDFs in the OED reading room or a comparison across tribunal archives. The practitioner blog IPethics & INsights runs [its own search engine](https://ipethicslaw.com/new-uspto-discipline-search-engine-added-to-ipethics-insights/) over OED decisions with written summaries, and notes that the reading room's PDFs are not catalogued in any searchable way; it does not count text-less files.

## Limits

The FLRA census (310 decisions, all readable) is left out because it read the FLRA's decision web pages, not PDFs. One PDF library and one threshold (300 characters). A file can pass the threshold with poor OCR text and still defeat a search, so "readable" here is a floor, not a guarantee of accessibility. The archives cover different years and different kinds of decisions, and the Tax Court frame is only the documents its search returned. The OED counts cover only files dated 1 January 2023 to 10 November 2026. The OTA census stopped at its time limit 27 opinions short of its frame (all 2024 business-tax opinions), so its counts are for the 1,849 it fetched. Counts can change if an archive replaces files. No names are given here; the archives publish them.

Data: [`tribunal-text-layers/counts.csv`](tribunal-text-layers/counts.csv), derived by hand from the censuses' published outputs (OED rows fetched 2026-11-13 09:45-09:55 UTC; OTA from the job's per-row log, [`ota-citations/results/progress.jsonl`](ota-citations/results/progress.jsonl), fetched 2026-11-14 02:42-12:43 UTC). Text: CC BY 4.0. Code in the linked censuses: Apache-2.0.

## Changes

- 2026-11-14: sixth archive added (California Office of Tax Appeals, 1,849 opinions, 17 under the threshold, all from 2024). The first version's statement that all text-less PDFs in the series were OED's is withdrawn.
- 2026-11-13: first version (five archives).
