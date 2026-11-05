# Legal-aid RFP vendor-AI study: coding 1.0.0 (frozen before grading)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Text and data: CC BY 4.0. Code: Apache-2.0. Information about public procurement documents, not legal advice.

Frozen on 5 November 2026, before the grader was run. Pre-registration: `../legal-aid-rfp-ai-prereg.md`
(commit 17f6f85). Amendment 1: `../legal-aid-rfp-ai-prereg-amendment-1.md` (commit 8d9d733). Frame:
collector v2 (`collect_rfps.py`, job `rfp-ai-collect-v2`, run on 5 November 2026 at 11:23 UTC).

## Files

- `frame_decisions.json`: every one of the 46 records the collector found (38 posting pages on the LSNTAP
  board and 8 files uploaded in 2026 that no collected page links to), with the decision taken and the reason:
  codable, merged into another record, in the study but not codable, or out.
- `coding.json`: the 17 codable postings. For each one: organisation, posted date and where the date came from,
  source files with SHA-256, the codes (VENDOR_AI and sub-codes, AI_IN_SCOPE, TECH or NON_TECH), a
  verbatim quotation for every code, and the calls a reader could reasonably make the other way
  ("borderline").
- `grade_rfpai.py` and `test_grade_rfpai.py`: the grader. It re-downloads every source file, checks its
  SHA-256, extracts the text with pypdf, checks every quotation against that text (only Unicode NFKC and
  whitespace are normalised), and grades P1 to P4 on the full frame and on the sensitivity frame. As a
  separate exploratory check, it then flips each borderline call one at a time and reports which
  predictions would change.

## How the calls were made

The calls were made by reading the collected text. AI agents working in MV2's name did the reading. There
is no second coder, so every call is published with its quotation for any reader to check. Rules applied
on top of the pre-registration, fixed before any count was computed:

- **VENDOR_AI** covers what the bidder or contractor itself does with AI, or with the organisation's data in
  AI, while preparing the proposal or doing the work. A requirement on the AI system being delivered (for
  example "the solution must not use customer data to train AI models") describes the product, so it is not
  VENDOR_AI. Such sentences are kept as `NOT_VENDOR_AI` quotations and listed as borderline calls.
- **TECH**: the vendor builds, configures, integrates or operates software, websites or systems, delivers
  IT services, or trains staff to build software. Work that only assesses, plans, evaluates, designs at
  concept level, sets governance or writes content is NON_TECH, even when its subject is technology.
- **Sensitivity frame**: records found only through a web-search seed are left out (amendment 1). So is
  text that only a seeded file supplied. That second rule removes one posting (Atlanta Legal Aid Society's
  LACI shared-governance RFP): a listing capture found the posting, but it can be coded only from a
  seeded file.

## Limits known before grading

- Only 17 of the 26 postings known to fall in the study window can be coded. The other nine survive only as
  one-line listing teasers (three of their titles name AI). Two more seeded postings have no text and no
  date, so whether they fall in the window is unknown.
- Four codable postings (Legal Aid Chicago's AI-architecture RFI and Copilot training RFP, North Mississippi
  Rural Legal Services' intake RFP, and Community Legal Services' strategic-plan RFP) are in the frame only
  because a web search found their files. That is why the sensitivity frame exists.
- Since 15 April 2026, LSNTAP also accepts RFPs through A2J Jobs. On 5 November 2026 its RFP list was empty,
  so it added nothing here.

The graded result and the write-up will be published next to these files, whichever way the predictions come out.
