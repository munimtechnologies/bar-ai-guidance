# Fabricated citations in California Workers' Compensation Appeals Board panel decisions, 2024-2026: result of census 1.0.0

Status: **graded 15 November 2026** against the [pre-registration](wcab-citations/PLAN.md) frozen on 12 November 2026 (commit e504710). Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Text CC BY 4.0; code Apache-2.0. This is information about public decisions of a state workers' compensation tribunal, not legal advice.

## Short answer

The WCAB's panel-decision page listed **3,123 decisions** in its 2024, 2025 and 2026 folders when the census job read it on 15 November 2026. 3,121 were readable. The patterns flagged 12. The agents then read all 12 in full: **10 are true cases, in 7 workers' compensation cases**, and 2 are false matches. None of the 7 cases is in the AI Hallucination Cases Database, which has no row for the WCAB at all.

Three of the seven cases are new to MV2's [hand-checked list](agency-hand-list.md), which had four cases (six decisions) read before the plan was frozen. The census found the other three:

| ADJ case | Decision (filed) | Who filed the bad citations | What the Board said | Outcome | AI named? | PDF SHA-256 (first 12) |
|---|---|---|---|---|---|---|
| ADJ10983565 | Opinion denying reconsideration, 18 Aug 2025 | Defense counsel (for one of the employers and its insurer) | footnote 3: a cited Cal.Comp.Cases case does not exist ("There is no case with this cite"); the trial judge had flagged it too | Both defense firms admonished, mainly for petitions with no references to the record; no sanction | No | 3c40f112c711 |
| ADJ17817958 | Opinion granting removal and notice of intent to sanction, 13 Oct 2025 | Defense counsel | Quotations attributed to a panel decision "do not appear to exist"; "It appears that the above citations are fabricated"; the cited panel decision says the opposite | Notice of intent, up to $2,500 | No | 4d0c2abc9d4f |
| ADJ17817958 | Decision after removal and order imposing sanctions, 24 Sep 2026 | same | Counsel answered that the quotations "appear to have been fabricated using AI" by **office support staff** and stayed in the petition while the supervising attorney had a family emergency. The Board surveys California Court of Appeal and Ninth Circuit AI-citation sanctions (from *Noland* to *Quinteros*) and rests the decision on the lawyer's duty to supervise non-lawyer staff (the WCAB's en banc *Ledezma*, Rule 5.3) | **$1,000** against the firm and the attorney (reduced from up to $2,500 for candid responses) | Yes | 51d34f50e93b |
| ADJ10934327 | Opinion granting removal, 4 Dec 2025 | Defense counsel, in a petition filed at the trial level | A cited panel decision cannot be found ("This case citation appears to have been fabricated") and a quotation from a Court of Appeal case is in no published decision; the Board says it "has recently seen a significant increase in the amount of what appears to be fabricated citations and fabricated quotations being filed in verified pleadings" and that "It does not matter how such fabrications are generated" | Returned to the trial judge to decide what happened; firm admonished | No | 582446aaeb3f |

The four hand-checked cases (ADJ17550375 *Sedano*, ADJ17889413 *ChatSOC*, ADJ12865802 and ADJ16902178) were all flagged again, so the recall check held. ADJ12865802 still has only its notice of intent (22 September 2025) in the listing; no final decision had been posted by 15 November 2026.

## What stands out

- **Every case began between June and December 2025, and no new one has appeared since.** The first decision in each of the seven cases is dated 29 July to 23 December 2025 (*Sedano*'s notice of intent, issued 30 June 2025, is not itself in the listing). The three 2026 decisions on fabricated citations are all follow-ups that impose sanctions in cases begun in 2025. No 2024 decision has one. That is the reverse of the census's guess (P4) that 2026 would have more. It is also at odds with the Board's own remark in December 2025 about a "significant increase". Possible reasons, none tested: the Board's sanctions and *Sedano* deterred filers, new cases are now handled by trial judges (whose orders are not on this page; one October 2026 panel decision in the listing reviews a trial judge's sanctions order that cites *Sedano*), or such cases simply have not reached a written panel decision yet.
- **The filers were mostly lawyers for employers and insurers.** In five of the seven cases the bad citations came from defense counsel; one came from an applicant's attorneys and one from a lien claimant's non-attorney representative. No case involves a worker without a lawyer. In the courts the tracker covers, many such filings come from people representing themselves. In this tribunal, by these decisions, they come from professionals.
- **AI is named in only two of the seven cases, and both times by the filer.** In ADJ17889413 the defense said the citations came from ChatSOC, a workers'-compensation treatise's own research chatbot. In ADJ17817958 the defense said office staff produced them with AI. In ADJ12865802 the Board raised AI only as a question. The other four never mention it. The Board's stated position (*Sedano*, repeated in 2026) is that a false citation in a verified petition is the problem however it was made. A tracker built around the word "AI" would miss most of these.
- **Sanctions are small and aimed at supervision.** The four sanctions so far are $750, $1,000, $1,000 and $150, under a statute that caps them at $2,500. The September 2026 decision is the first in this set to rest on a lawyer's duty to supervise staff who use AI, rather than on the signer's own checking.

## Predictions

| | prediction | verdict (as graded) | corrected (after reading all 12) |
|---|---|---|---|
| P1 (recall check, not blind) | all six hand-checked decisions are in the frame and flagged | **held** (6 of 6) | held |
| P2 | 10 to 40 decisions have a fabricated-citation phrase | **held** (12) | 10, held |
| P3 | at most one 2024 decision has one | **held** (0) | held |
| P4 | more 2026 decisions than 2025 decisions have one | **failed** (5 vs 7) | 3 vs 7, failed |
| P5 | fewer than half mention an AI term | **held** (4 of 12) | 4 of 10, held |
| P6 | at least three quarters cite Labor Code section 5813 | **held** (9 of 12) | 9 of 10, held |
| P7 (not blind) | no WCAB row in the database, and at least three cases missing from it | **held** (0 rows; 9 flagged cases, all missing) | 7 cases, all missing, held |
| P8 | at least two fabricated-citation decisions other than the six hand-checked ones mention *Sedano* | **failed** (0) | failed |
| P9 (method check) | at least 98% of the frame readable | **held** (3,121 of 3,123, 99.9%) | held |

Seven held, two failed. P8's failure is informative in its own way: the three newly found cases rely on the Court of Appeal's *Noland*, the en banc *Ledezma* and the Board's own reasoning, not on *Sedano*, even though *Sedano* is the WCAB's reported sanctions decision.

## The two false matches, and what else was read

- **ADJ8963138 (28 Jul 2026)**: a trial judge's finding rested on "a medical opinion that does not exist" (a doctor never gave one). Not a citation.
- **ADJ14015513 (13 Apr 2026)**: the trial judge's report says a claims administrator's letter rejecting a treatment request cited "a non-existent regulation" (section 9792.9.1(t)(2); the rule the defendant later relied on is 9792.6.1(t)(2)). That is a wrong section number in a claims letter, not authority invented in a filing with the Board, so it is not counted. A stricter reader could count it; it would not change any verdict.
- **The other six decisions flagged only for an AI term, "hallucinat...", *Noland* or *Sedano* were read too.** Three use "hallucination" in its medical sense. One is a case whose injured worker happens to be named Noland. One reviews a trial judge's sanctions order for misstating the law, citing *Sedano*; it does not describe fabricated authority. One records that an unrepresented applicant said at a hearing that he had "consulted artificial intelligence" about how his disability rate should be calculated: the first decision in this series in which a worker, rather than a lawyer, says he relied on AI, though not for any filing with fake citations. No missed true case turned up among them.

## Tracker check

The job downloaded the AI Hallucination Cases Database CSV at 00:12 UTC on 15 November 2026 (2,199,394 bytes, SHA-256 74aa53af...). No row's court is the WCAB, and no row quotes any of the seven ADJ numbers. The tracker's live search at about 08:00 UTC the same day agreed: "WCAB" returns no rows; "Workers" returns six rows, none from the WCAB (the nearest is British Columbia's Workers' Compensation Appeal Tribunal); the names of the new cases' employers return nothing; and the one "Tovar" row is a different case in a California superior court.

## Data

[`wcab-citations/results/`](wcab-citations/results/): `results.md` and `results.json` (the job's own grading), `rows.csv` (one row per decision: row id, folder year, listed date, ADJ numbers for flagged decisions only, fetch status, text length, the PDF's SHA-256, and the flags), `listing.json` (the listing page's size, SHA-256 and parser checks) and `sources.json`. **Injured workers' names and file names are not published**, though the WCAB publishes them; the WCAB's page finds each decision by ADJ number. Texts and excerpts stayed private to the job. One PDF (2025) could not be parsed (broken file) and one returned 404.

## Limits

Panel decisions are what the Board chose to write about. Trial judges' orders, including sanctions orders, are not on this page, so a fake citation caught and dealt with at trial is invisible here unless a panel later reviews it. The patterns can miss other wording; the review looked for misses only among flagged texts. The census counts what decisions say. It judges no worker, lawyer, representative, company or official, and it is not legal advice. Prior art: practitioner blogs, podcasts and trade press discuss *Sedano* and the ChatSOC case. A search on 12 November 2026 found no count across WCAB decisions and no published mention of the other cases.

## Changes

- 2026-11-15: first version.
