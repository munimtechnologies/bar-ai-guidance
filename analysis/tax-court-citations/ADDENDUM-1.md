# Addendum 1 to the U.S. Tax Court census 1.0.0: what the broad re-read found

Status: **review only, nothing graded.** The verdicts in [the result](../tax-court-citations.md) do not change. Written 12 November 2026. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public court documents, not legal or tax advice. As the plan requires, documents are named by docket number, not by party.

## What was done

The census plan promises to report documents that its frozen patterns missed. A follow-up job (`taxreview-v1`, code in [review/](review/review.py), run 12 November 2026, 11:27-11:34 UTC) downloaded the census's published `rows.csv` (SHA-256 `8bbc7697...`) and re-read **all 78** frame documents from the court's public DAWSON API, one request every 3 seconds. It also searched DAWSON's opinions for "Tellock" (T.C. Memo. 2026-59, which a 2026 frame opinion cites next to its AI passage) and added the one 2026 hit. It used a deliberately broad pattern: "does/did not exist", "nonexistent", "fictitious", "fabricat-", "bogus", "fake", "hallucinat-", ChatGPT, chatbot, Gemini, Claude, Copilot, "artificial intelligence", "AI", "large language model", "unable to / could not locate or find", "no such case", "misquot-" and "misrepresent the holding".

- 79 documents read, **79 readable**; **77** had at least one match (about 385 passages). The per-document counts are in [review/review_summary.csv](review/review_summary.csv) (docket, date, kind, characters, matched words and this addendum's reading; no text). There, "not about citations" means either that no passage had a citation word within six words of a match word (see below) or that the passage was read and was about something else.
- Every passage was searched in both directions for a citation word (cite, case, authority, opinion, page, quote, precedent, reporter) within six words of a match word. Every passage that search returned was read by hand, as was every passage from the 2026 documents and every order the court's search had returned for "nonexistent cases", "non-existent" or "fabricated cases" (8206-24, 1959-21, 6501-20, 6323-22, 19354-24, 2980-25 and 10951-24).

## Result

**No new document says a filing cited a case or authority that does not exist.** The count stays at 4 (the 3 graded plus [6165-24](https://dawson.ustaxcourt.gov/case-detail/6165-24), found by hand earlier). The broad pattern also found all 4 and [2249-25](https://dawson.ustaxcourt.gov/case-detail/2249-25), which shows that it could find such documents.

**One borderline document, not in the AI Hallucination Cases Database:**

- [19354-24](https://dawson.ustaxcourt.gov/case-detail/19354-24), order of 8 April 2026. The court says the petitioner "cites to non-existent pages" of a real Tax Court opinion (Beland v. Commissioner, 156 T.C. 80 (2021)). It then reads the argument as pointing to the pages that do exist and decides it on the merits. No AI term appears and no sanction or warning is given. Like 2249-25, this is a citation to pages that do not exist, not an invented case. Unlike 2249-25, the court does not link it to AI. A wrong page number can be an ordinary typing error, so this addendum does not count it as a fabricated-citation document. It is listed so that readers can judge it.

**Why the other orders were in the frame:** the words were about other things. The 2025 order in 8206-24 calls a document request "irrelevant or nonexistent". 6323-22 concerns "a nonexistent notice of determination". 1959-21 and 6501-20 quote a Justice Department press release about "nonexistent exclusions". 2980-25 is about "allegedly non-existent balances". In 10951-24 the petitioners alleged that the IRS "fabricated" the mailing of notices.

**Most of the other matches are about facts, not filings:** fictitious income or business expenses, fabricated documents offered as evidence, "bogus" deductions or insurance arrangements, nonexistent businesses or buildings in appraisals, a ZIP code or a town that "does not exist", and the Appraisal Institute's "AI-GRS" designation. One "Claude" match is a person's first name.

**Tellock (T.C. Memo. 2026-59, docket 10402-23, 20 July 2026):** readable, with no match at all. The 2026 opinion that cites it (2249-25) cites it on the section 6404(h) point, not on AI.

## What this changes

Nothing in the graded verdicts. It makes the corrected reading of the census firmer: from 2023 to 10 November 2026 the Tax Court's search-returned orders and opinions hold 4 fabricated-citation documents, 1 AI-related document about pages that do not exist (2249-25) and 1 non-AI one (19354-24). The database lists 4 of the first 5 and not 19354-24. The one real gap stays the same: [6165-24](https://dawson.ustaxcourt.gov/case-detail/6165-24), a short order in which the fabricated citation is a side remark.

## Limits

This re-read covers only the 78 documents that the 27 fixed searches returned, plus one. An order that uses none of the broad words is outside it, and so are sealed documents and transcripts. The passages were sorted with the two-way search described above; passages from 2023-2025 that the search did not return were not all read one by one. Texts and excerpts stay private to the job. Database: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, checked against MV2's private copy fetched 12 November 2026.

Text of this addendum: CC BY 4.0. Code: Apache-2.0.
