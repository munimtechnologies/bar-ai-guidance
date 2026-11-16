# Fabricated or misattributed citations in EEOC federal-sector appeal decisions: result of a pre-registered hand search

Written 2026-11-16 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Text CC BY 4.0. This is information about public decisions of the U.S. Equal Employment Opportunity Commission, not legal advice.

Plan, frozen and published before any decision was read in full: [eeoc-citations/PLAN.md](eeoc-citations/PLAN.md) (commit 8ce25cb, 15 November 2026, 19:58 UTC). Per-decision data: [eeoc-citations/decisions.json](eeoc-citations/decisions.json).

## Short answer

- The Commission's own decision search turned up **three appeal decisions from 2026** in which the Commission says, in its own words, that a filing in the appeal cited decisions that **do not exist, cannot be located, or do not say what they were cited for**. The three were decided on 17 February, 14 July and 14 September 2026.
- **One names AI**, and only as the agency's suggestion: in *Shon T. v. Bisignano* (Social Security Administration) the agency "suggested that these citations might be the result of AI 'hallucinations'", and the Commission, "upon our independent review", concurred with the agency's assessment.
- **None imposes a sanction.** Two end with the same sentence: "Parties are reminded to exercise due diligence in their use of case citations." The third, where the brief came from the complainant's attorney, "caution[s]" the attorney. All three affirm the agency.
- **The AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) lists none of them.** On 16 November 2026 its live search returned 0 rows for "EEOC", "Equal Employment" and each of the three appeal numbers, and no EEOC row for the pseudonyms "Shon", "Domingo" or "Ahmad" or for "Bisignano".
- **All five pre-registered predictions held.**
- **A pattern: real-looking appeal numbers attached to the wrong case.** In two of the three, the bad citations are EEOC appeal numbers. In *Shon T.* the Commission gives one example: "Jackson v. Dep't of the Air Force, EEOC Appeal No. 0120120853 (July 11, 2014)" was cited for a point about harassment, but that number belongs to a 2012 Department of Defense decision about a procedural dismissal "with no discussion of harassment". In *Domingo M.*, some of the cited numbers did not "involve the parties represented nor the premise for which it was cited". An EEOC appeal number has a fixed form (here 01 + 2012 + 0853), so a made-up citation can carry a well-formed number. Checking only that the number exists will not catch it.

## The three decisions

All three were read in full on 15 November 2026 in an ordinary browser, one file at a time, after the plan was live. eeoc.gov's robots.txt disallows automated access to the decision files, so no program downloaded them and there are no file hashes. The quotations below are copied from the decisions. Lawyers' and officials' names are left out. The complainants' names are the Commission's own pseudonyms.

| Appeal No. | Caption (Commission's pseudonym) | Decided | Date in file path | Who filed the citations | What the Commission found | AI named? | What it did | Outcome |
|---|---|---|---|---|---|---|---|---|
| [2026000158](https://www.eeoc.gov/sites/default/files/decisions/2026_05_27/2026000158%20DEC.pdf) | Ahmad S. v. Collins (Veterans Affairs) | 17 Feb 2026 | 2026-05-27 | Complainant; no attorney or representative named for the appeal | Brief "contains several case citations that either do not exist, or do not stand for the proposition for which they are cited" (fn. 2); no cited case named | No | Reminder: "Parties are reminded to exercise due diligence in their use of case citations." | Affirms dismissal of the complaint |
| [2026001205](https://www.eeoc.gov/sites/default/files/decisions/2026_09_08/2026001205%20DEC.pdf) | Shon T. v. Bisignano (Social Security Administration) | 14 Jul 2026 | 2026-09-08 | Complainant; no attorney or representative named | Agency "was unable to locate most of the decisions cited"; complainant did not answer its request for copies; Commission concurs "upon our independent review" and gives one example (fn. 2) | Yes, as the agency's suggestion | Same reminder | Affirms the final order implementing the administrative judge's decision |
| [2025000648](https://www.eeoc.gov/sites/default/files/decisions/2026_10_15/2025000648%20DEC.pdf) | Domingo M. v. Collins (Veterans Affairs) | 14 Sep 2026 | 2026-10-15 | Complainant's attorney | Brief "cited to five cases as Commission precedent supporting a greater award; however, three of the cases either do not exist or the corresponding appeal number does not involve the parties represented nor the premise for which it was cited" (fn. 3); no cited case named | No | "We caution Complainant's attorney regarding the submitted appellate brief." | Affirms the agency's compensatory damages award |

The full footnote in *Shon T.* (2026001205), fn. 2:

> "The Agency noted in its appellate brief that it was unable to locate most of the decisions cited by Complainant in his appellate brief and asked Complainant to provide copies of these decisions. Complainant did not respond and the Agency suggested that these citations might be the result of AI "hallucinations." Upon our independent review, we concur with the Agency's assessment. For example, Complainant cites to "Jackson v. Dep't of the Air Force, EEOC Appeal No. 0120120853 (July 11, 2014)" for the proposition that the Commission has reversed summary judgment where the AJ evaluated incidents of harassment in isolation instead of collectively. However, EEOC Appeal No 0120120853 is actually Complainant v. Dep't of Defense, EEOC Appeal No. 0120120853 (Apr. 10, 2012) and is a case involving a procedural dismissal prior to the summary judgment stage with no discussion of harassment. Parties are reminded to exercise due diligence in their use of case citations."

What "concur with the Agency's assessment" covers is not spelled out. It plainly covers the agency's point that the decisions could not be found. The footnote does not say the Commission found that AI was used.

In *Domingo M.* the footnote is attached to the sentence where the Commission cites its own precedent for the award it affirmed ($20,000). The Commission did not rely on the attorney's citations.

**Timing.** The date in each file's folder name is when the file was posted, not the decision date. The gap between decision and that date was 99, 56 and 31 days. A search on the day a decision is issued will not find it.

## Predictions, graded

| | Prediction (frozen 15 Nov 2026) | Result |
|---|---|---|
| E1 | Each of the three says, in the Commission's own words, that a filing cited authority that does not exist, cannot be found, or does not say what it was cited for | **Held** (all three; quoted above) |
| E2 | Exactly one (2026001205) mentions AI | **Held.** Only *Shon T.*, and only as the agency's suggestion. No decision uses "artificial intelligence", "generative AI" or "ChatGPT". |
| E3 | None imposes a sanction beyond a reminder or warning, and none says the bad citations changed the outcome | **Held.** Two reminders and one caution. No decision ties the citations to its outcome, and all three affirm. |
| E4 | (partly not blind) In 2025000648 the citations came from the complainant's attorney; in the other two, from complainants without an attorney | **Held**, as far as the decisions show. 2025000648 refers to "Complainant's attorney". The other two name no attorney or representative for the appeal. In 2026000158 a union representative appears only in the timeliness facts, not as the appeal's representative. A decision that names no representative does not prove that nobody helped. |
| E5 | (not blind) On the day of reading, the tracker lists none of the three | **Held** (re-checked early on 16 November 2026, UTC; searches listed above) |

## Searches after the plan (not part of the frozen search)

On 16 November 2026, after the reading, we ran six more searches on the Commission's search page. They are reported here but are outside the plan.

| Query | Results | New flagged decisions |
|---|---|---|
| "exercise due diligence in their use of case citations" (the reminder sentence) | 2 | none (2026000158 and 2026001205 only) |
| "appeal number" "does not involve" | 9 | none (2025000648 only; the rest are older decisions using the words in other senses) |
| 0120120853 (the misattributed number) | 1 | none (2026001205 only) |
| "does not exist" cited appeal brief | 189 | none on page 1 |
| caution attorney citations | 118 | none on page 1 |
| "is actually" appeal cited proposition | 81 | none on page 1 |

The reminder sentence appears in only these two decisions in the index, so it is not yet standard wording. The 2012 decision behind appeal number 0120120853 did not come up in the search, so we could not check the Commission's description of it ourselves.

## Why it matters

- **Most EEOC appellants have no lawyer.** In its January 2022 [release of a guide for unrepresented complainants](https://www.eeoc.gov/newsroom/eeoc-releases-new-guide-federal-employees-filing-employment-discrimination-appeals), the EEOC said that "approximately three-quarters of all appeals on the merits involve self-represented federal employees or applicants". Two of the three decisions here involve complainants with no named representative, which fits that picture. Three decisions are not enough to say whether self-represented filers account for more or fewer of these errors than their share of appeals.
- **A gap in the tracker.** It is the same gap MV2's tribunal series keeps finding. The tracker has rows for the federal contract appeals boards and the FLRA, but none for the EEOC, the MSPB, California's WCAB or the agency boards in the [hand-checked list](agency-hand-list.md). The EEOC decisions are short footnotes that never use the words "artificial intelligence", in a collection that robots.txt closes to crawlers. A tracker fed by news reports and keyword alerts is unlikely to see them.
- **"Does this appeal number exist?" is not enough.** A citation checker for EEOC decisions should compare the case name, the agency and the date with the decision the number really belongs to.

## Limits

This is a keyword search of one relevance-ranked search engine, not a census. Searches covered only the first page of results unless stated otherwise. A decision that describes bad citations in other words, or that the engine ranks low, is missed. A bad citation that a decision does not mention is invisible. The Commission described the cited cases in only one of the three decisions, so we cannot check the others. Three decisions say nothing about how common the problem is. Tracker checks are live searches on one day, and the database changes often. We judge no complainant, attorney, agency or official.

## Changes

- 2026-11-16: first version. All five predictions graded (all held). Post-plan searches and tracker re-check added.
