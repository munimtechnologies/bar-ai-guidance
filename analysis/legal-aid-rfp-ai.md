# How 2026 legal-aid RFPs treat a vendor's own use of AI: graded result

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Text and data: CC BY 4.0. Code: Apache-2.0. This is information about public procurement documents, not legal
advice.

**Result in one paragraph.** We read 17 requests for proposals (RFPs) and requests for information (RFIs) that US
legal-aid and access-to-justice organisations posted between 1 January and 4 November 2026. All were listed on, or
hosted by, LSNTAP's jobs-and-RFPs board. We graded four predictions that we had committed in advance. On the full frame of 17
postings, **P1 held**: 3 of 17 (17.6%) say anything about what the vendor itself may do with AI. **P2 failed**: that
share was 2 of 9 in the first half of the year and 1 of 8 in the second, so it did not rise. **P3 held**: no posting
bans a vendor's use of AI. **P4 held**: 5 of 8 technology-build postings (62.5%) include AI in the work itself. In the
sensitivity frame, which leaves out the 5 postings found only through web search, P1, P3 and P4 hold the same way.
P2 there is **not testable**, because only 4 postings fall in the second half and the pre-registration needs at least
5. **P2 rests on one call either way.** The difference between the halves is a single posting. If our borderline call on
R01 (Cleveland) is read the other way, or the one on R13 (Legal Aid Chicago's RFI) is, P2 would have held. Read P2
as "no sign of a rise", not as evidence of a fall.

- Pre-registration: [`legal-aid-rfp-ai-prereg.md`](legal-aid-rfp-ai-prereg.md) (commit 17f6f85, 4 Nov 2026)
- Amendment 1 (collection only, no prediction changed): [`legal-aid-rfp-ai-prereg-amendment-1.md`](legal-aid-rfp-ai-prereg-amendment-1.md) (commit 8d9d733)
- Coding 1.0.0, frozen and published before grading: [`rfpai/coding.json`](rfpai/coding.json),
  [`rfpai/CODING.md`](rfpai/CODING.md), [`rfpai/frame_decisions.json`](rfpai/frame_decisions.json) (commit 791fc27)
- Grader and its tests: [`rfpai/grade_rfpai.py`](rfpai/grade_rfpai.py), [`rfpai/test_grade_rfpai.py`](rfpai/test_grade_rfpai.py)
- Grader output: [`rfpai/results/results.json`](rfpai/results/results.json), [`rfpai/results/results.md`](rfpai/results/results.md)

## How it was checked

The grader ran on 5 November 2026 at 21:13 UTC in a sealed container, after its 16 offline tests passed. It downloaded
all 18 source files again from lsntap.org, and all 18 matched the SHA-256 recorded in the frozen coding. It extracted
their text with pypdf 5.1.0 and found all 34 quotations word for word. The only normalisation was Unicode NFKC and
whitespace. It found no structural problems. The coding file it graded has SHA-256
`d9f8456e502ffacc039c7784dc5385ca17fc4046a5547a4a485c6ab878af5335`.

## The four predictions

| | Prediction (pre-registered) | Full frame (17) | Sensitivity frame (12) |
|---|---|---|---|
| P1 | At most 30% of codable postings have a VENDOR_AI clause | **held**: 3/17 = 17.6% | **held**: 3/12 = 25.0% |
| P2 | VENDOR_AI share higher in 1 Jul to 4 Nov than in 1 Jan to 30 Jun (each half at least 5) | **failed**: 2/9 = 22.2% vs 1/8 = 12.5% | **not testable**: 2/8 vs 1/4 |
| P3 | No codable posting has a `ban` sub-code | **held** | **held** |
| P4 | At least 25% of codable TECH postings have AI_IN_SCOPE (at least 5 TECH) | **held**: 5/8 = 62.5% | **held**: 3/6 = 50.0% |

VENDOR_AI means a sentence about what the bidder or contractor itself does with AI, or with the organisation's data
in AI, while preparing the proposal or doing the work. A requirement on the AI system being delivered is not
VENDOR_AI. AI_IN_SCOPE means the requested work itself includes AI. TECH means the vendor builds, configures,
integrates or operates software or systems. The full rules are in [`rfpai/CODING.md`](rfpai/CODING.md).

## Exploratory: what one changed call would do

Each borderline call was flipped on its own (full frame). This is exploratory and was not pre-registered as a test.

| Record | Call -> other reading | Predictions that change |
|---|---|---|
| R01 | VENDOR_AI yes -> no | P2: failed -> held |
| R13 | VENDOR_AI no -> yes | P2: failed -> held |
| R05, R06 | VENDOR_AI no -> yes | none |
| R07, R08, R09, R12, R13 | NON_TECH -> TECH | none |
| R14 | TECH -> NON_TECH | none |

P1, P3 and P4 do not depend on any single call. P2 depends on two.

## Every posting

| id | Organisation | Posted | TECH | VENDOR_AI | AI_IN_SCOPE | Found only by web search |
|---|---|---|---|---|---|---|
| R01 | Legal Aid Society of Cleveland | 2026-02-17 | TECH | yes (data, restrict; borderline) | yes | |
| R02 | Anishinabe Legal Services | 2026-05-01 | NON_TECH | no | yes | |
| R03 | Legal Services State Support (Minnesota) | 2026-05-13 | TECH | no | no | |
| R04 | Georgia Legal Services Program | 2026-05-14 | NON_TECH | yes (disclose, human_review) | no | |
| R05 | Legal Aid Society of Mid-New York | 2026-05-14 | TECH | no (borderline) | yes | |
| R06 | Southern Minnesota Regional Legal Services | 2026-05-15 | TECH | no (borderline) | yes | |
| R07 | IOLA Fund of the State of New York | 2026-06-03 | NON_TECH | no | no | |
| R08 | Michigan Statewide Advocacy Services | 2026-06-24 | NON_TECH | no | yes | |
| R09 | Atlanta Legal Aid Society | 2026-04-20 | NON_TECH | no | yes | text only from a seeded file |
| R10 | Community Legal Services (Arizona) | 2026-07-20 | NON_TECH | no | no | yes |
| R11 | North Mississippi Rural Legal Services | 2026-07-24 | TECH | no | yes | yes |
| R12 | Montana Legal Services Association | 2026-08-05 | NON_TECH | no | no | |
| R13 | Legal Aid Chicago (RFI) | 2026-08 (upload folder) | NON_TECH | no (borderline) | yes | yes |
| R14 | Legal Aid Chicago | 2026-08-18 | TECH | no | yes | yes |
| R15 | Navajo Nation Judicial Branch | 2026-09-03 | TECH | no | no | |
| R16 | Colorado Legal Services | 2026-10-16 | TECH | no | no | |
| R17 | Georgia Legal Services Program | 2026-11-03 | NON_TECH | yes (disclose, human_review) | no | |

Descriptive note, not a graded result: the three VENDOR_AI postings come from only two organisations. R04 and R17
are from the same programme and carry the same clause word for word.

## What the clauses say (verbatim from the posted files)

**R04 and R17**, the same standard clause in both:

> "Any use of AI in processing data under this contract must be disclosed, and any deliverables assisted by AI must
> be reviewed by a human being before finalization."

Both also ask proposers for "an explanation of the policies which will govern your use of AI" if AI will be used.

**R01** (borderline), on the developer of an AI research assistant:

> "The developer will be required to ensure that no data used to develop or train the AI Assistant is reused,
> repurposed, or shared with any third party (including LLM providers) without Clevelan d Legal Aid's explicit
> approval."

(The split "Clevelan d" is in the PDF's own text layer.)

**Limits written on the delivered product, coded NOT VENDOR_AI and listed as borderline:**

- R05: the assistant "must exclude client personally identifiable information from training data".
- R06: "all proposed solutions must meet strict data security and governance requirements. These include
  prohibitions on using customer data to train AI models".
- R13 states the organisation's own internal policy as background: "public AI tools must not be used with PII,
  confidential information, sensitive information, highly sensitive information, or client information".

## What this does and does not show

- In this set, an RFP is more likely to ask for AI as part of the work (9 of 17 postings, and 5 of 8 build postings)
  than to set rules for how the vendor uses AI (3 of 17). Where data rules for AI appear, they mostly describe the
  delivered system: no training on client or customer data. Disclosure and human review of AI-assisted
  deliverables appear only in one programme's standard clause.
- Nobody banned vendor AI use. That is P3, and it held in both frames.
- It does not show a trend. P2 failed by one posting and turns on a single borderline call. The second-half sample
  is 8 postings, or 4 in the sensitivity frame.

## Limits

- **Small and partial frame.** Of the 26 postings known to fall in the window, only 17 could be coded. Nine survive
  only as one-line listing teasers, and three of those titles name AI. Two seeded postings have no text and no date.
  LSNTAP takes posting pages down when a posting closes, so the frame depends on archive captures and on files that
  stay hosted. Legal-aid RFPs posted elsewhere (on an organisation's own site, for example) are not in it.
- **One coder.** AI agents working in MV2's name made the calls. No second coder checked them. Every call is
  published with its quotation and its borderline readings, so any reader can check them and disagree.
- **Text layer only.** Quotations were checked against pypdf's text. Nothing that appears only in images was read.
- **Interest.** Munim, Inc. may respond to one of the open postings in this set. The coding was frozen and published
  before grading, and the result is reported whichever way it came out.

## Reproduce

```
pip install pypdf==5.1.0
cd analysis/rfpai
python -I -B -m unittest discover -v
python -I -B grade_rfpai.py --coding coding.json --out results
```

The grader prints one JSON line. On 5 November 2026 it was:
`{"verified": true, "files_ok": "18/18", "quotes_ok": "34/34", "full": {"P1": "held", "P2": "failed", "P3": "held", "P4": "held"}, "sensitivity": {"P1": "held", "P2": "not testable", "P3": "held", "P4": "held"}, "differs": {"P2": ["failed", "not testable"]}}`
