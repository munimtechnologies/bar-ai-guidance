# How many U.S. Tax Court orders and opinions say a filing cited authority that does not exist? Result of census 1.0.0

Status: **graded on 11 November 2026** (job finished 00:00 UTC) against the plan frozen in commit `5e75b67` ([PLAN](tax-court-citations/PLAN.md), [code](tax-court-citations/census.py)). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `72a50e24...`). Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public court documents, not legal or tax advice. As the plan requires, documents are named by docket number, not by party.

## Short answer

The Tax Court's own public search (DAWSON) returned **78** orders and opinions filed from 1 January 2023 to 10 November 2026 for the 27 fixed keyword searches (54 searches, none failed). All 78 were readable. The frozen patterns found **3** that say a filing cited cases or authorities that do not exist, and the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) lists **all 3**. Reading every flagged passage by hand found **one more**: a December 2025 order that the patterns missed and that the database does not list.

So the tracker is much more complete for the Tax Court than MV2 predicted. The prediction that it would hold fewer than half (P2) **failed**. Fabricated citations in the Tax Court's own records are also rarer than predicted (P1 **failed**: 3, not 10 or more), and most of those documents mention AI.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | at least 10 readable fabricated-citation documents | **failed** | 3 |
| P2 | fewer than half of them are in the database | **failed** | 3 of 3 are |
| P3 | fewer than half mention an AI term | **failed** | 2 of 3 do |
| P4 | at least half are orders, not opinions | **failed** | 1 of 3 |
| P5 | at least half cite Tax Court Rule 33(b) | **held** | 2 of 3 |
| P6 | fewer than half cite section 6673 | **held** | 0 of 3 |
| P7 | coverage check (not blind): every database Tax Court row in the window matches a frame document | **failed** | 4 of 5 matched; row 1703 did not |
| P8 | search check: the exact-phrase search returns at least 90% of frame documents containing "artificial intelligence" | **held** | 5 of 5 |

Full outputs are in [results/](tax-court-citations/results/): `results.md`, `results.json`, `rows.csv` (one row per document: docket-entry id, docket numbers, date, kind, signing judge, pages, link to the public case page, PDF SHA-256 and flags; no captions), `searches.json` (every search with its result counts), `sources.json` and `status.json`. Texts and excerpts stay private to the job.

## What reading every flagged passage showed (corrections; the verdicts stay as graded)

**The three graded documents are true matches:**

- [10795-22](https://dawson.ustaxcourt.gov/case-detail/10795-22), order of 23 October 2024. A pretrial memorandum cited non-existent cases. Counsel said a paralegal drafted it, and the court asked whether an AI platform or large language model had been used. The court quotes the Chief Justice's 2023 year-end report on AI "hallucination" and rests on Rule 33(b), which allows a sanction for a pleading signed in violation of the rule.
- [12241-20](https://dawson.ustaxcourt.gov/case-detail/12241-20), memorandum opinion of 20 May 2025. A self-represented petitioner's opposition cited two T.C. Memo. decisions that do not exist. The court imposed no sanction and warned that citing nonexistent caselaw again could lead to one. No AI term appears.
- [8077-23](https://dawson.ustaxcourt.gov/case-detail/8077-23), memorandum opinion of 9 February 2026 (T.C. Memo. 2026-16). Lawyers cited "hallucinated authorities likely generated through artificial intelligence". The court says this is the first time it has addressed the problem in an opinion rather than an order. It notes that it has no equivalent to Rule 11 apart from Rule 33(b), then relies on Rule 201(a) and Model Rule 3.3.

**One document the patterns missed, and the database does not list:**

- [6165-24](https://dawson.ustaxcourt.gov/case-detail/6165-24), order of dismissal and decision of 31 December 2025. The court notes that a sworn declaration attached to a motion for continuance "resembles output from chatbots such as ChatGPT". It cites a Tax Court case ("93 T.C. 125") that does not exist and an Internal Revenue Manual provision unrelated to the case. The court warns the petitioner about relying on chatbots. The frozen pattern looks for "cited", "quoted" or "referenced" at most three words before "does not exist", and this order says "cites a Tax Court case (...) that does not exist", so the pattern did not count it. It was in the frame only because of the `ChatGPT` search.

**One AI-related document that is not a fabricated-citation document:**

- [2249-25](https://dawson.ustaxcourt.gov/case-detail/2249-25), memorandum opinion of 15 September 2026 (T.C. Memo. 2026-85). A brief "appears to have been drafted with the assistance of artificial intelligence (AI)" and cites pages that do not exist and cases that do not support the propositions they are cited for. These are real AI-related citation errors, but no case is said to be invented, so the patterns rightly did not count it. The database lists it.

**Four of the eight `ai_mention` matches are false:** "artificial intelligence" in a petitioner's business plan (27574-15), Facebook's "AI/ML" capabilities in a transfer-pricing opinion (21959-16), "an LLM in taxation" (a law degree, 16277-16), and a person called "Al" written in parentheses (6819-20). The other four (10795-22, 8077-23, 6165-24 and 2249-25) are about filings.

**Corrected counts:** 4 documents say a filing cited authority that does not exist (3 graded plus 6165-24). The database lists 3 of them, 3 of the 4 mention AI, and 2 of the 4 are orders. Counting 2249-25 as well, the court's own records hold 5 documents on AI-related citation problems or fabricated citations, and the database lists 4 of them.

**Why P7 failed:** database row 1703 (18 March 2026, docket 31104-21) is a **trial transcript** in which an expert witness was questioned about using AI tools on an expert report. The database records the outcome as "report withdrawn". DAWSON's order and opinion search does not cover transcripts, so no keyword search could return it. This is a limit of what the court's search covers, not a matching error.

**Not yet reviewed:** the frame's other 69 documents matched no frozen pattern. Most were returned for words like "fictitious", "fabricated" or "nonexistent" used about transactions, entities or documents, not citations, but they have not all been read. A follow-up job (`taxreview-v1`, review only, nothing graded) re-reads all 78 with a deliberately broad pattern. An addendum will report anything it finds, including the orders that the court's search returned for "nonexistent cases" (for example 8206-24, 30 December 2025).

## What this means

1. MV2's two earlier studies found that the main tracker holds few agency and Tax Court decisions. For the Tax Court, as for the [FLRA](flra-ai-citations.md), that reflects how rare these documents are, not a large coverage gap. From 2024 on, the court's own records hold one or two fabricated-citation documents a year (1 in 2024, 2 in 2025, 1 so far in 2026), and the tracker has most of them.
2. The gap that does exist is in the court's **orders**, the documents that are hardest to find: the one missed document is a three-page order of dismissal in which the fabricated citation is a side remark.
3. The court's search works for this purpose when it is given many searches: the exact phrase found every document containing it (P8). Keyword searches behave unevenly, though, as the [plan](tax-court-citations/PLAN.md) records: a broader term sometimes returned fewer orders than a narrower one.

## Limits

The frame is only what the court's search returns for 27 fixed searches. An order phrased in other words ("the Court could not locate these opinions") is outside it. Sealed orders and transcripts are not covered. With 3 to 5 documents, the shares above describe documents, not rates. Matching to the database uses the date and a party-name word, and each match was checked by hand. This counts what documents say. It does not judge any taxpayer, practitioner or judge, and it is not legal or tax advice.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `cac050d5...` (2,197,049 bytes), fetched 2026-11-10T23:51:06Z. Tax Court documents read through the public DAWSON API, one request every 3 seconds. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
