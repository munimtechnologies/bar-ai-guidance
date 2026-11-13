# Fabricated citations in the USPTO's practitioner-discipline archive, 2023-2026: result of census 1.0.0, and a blind spot nobody had counted

Status: **graded on 13 November 2026** against the plan frozen in commit `200007c` ([PLAN](uspto-oed-citations/PLAN.md)). Before downloading anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `dfdf5dc3...`). No amendment was needed. A pre-registered follow-up reads the decisions the census could not ([Addendum 1](uspto-oed-citations/ocr/ADDENDUM-1.md)). Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions of a federal agency, not legal advice.

## Short answer

The census fetched all **160 decisions** that the USPTO's Office of Enrollment and Discipline (OED) lists in its [FOIA reading room](https://foiadocuments.uspto.gov/oed/) with dates from 1 January 2023 to 10 November 2026 (140 discipline, 18 reinstatement, 1 moral character, 1 technical). Every download worked.

- **One readable decision deals with fabricated citations: D2025-13**, a public reprimand of 6 March 2025. It is also the only readable decision that mentions AI.
- **27 of the 160 PDFs have no text layer** (scanned images), so nothing in them can be searched. They cluster in 2026: **16 of the 35 decisions dated 2026 (46%)**, against 11 of 125 (9%) from 2023 to 2025. One of the 16 is **D2026-16**, the July 2026 reprimand over AI-generated citations that the press covered. So the census could not test it, and its counts may be low. Addendum 1 OCRs the 27.
- The AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) has **one row whose court is the USPTO**: D2026-16. It has **no row for D2025-13**, and none for the Trademark Trial and Appeal Board (TTAB) ruling that first caught those citations in February 2024. It does have the **New York reciprocal censure** of the same lawyer for the same brief (13 November 2025). Once again the tracker caught a later follow-on but not the tribunal that first found the problem.

Readable decisions by year: 2023: 38 of 44; 2024: 35 of 37; 2025: 41 of 44; 2026: 19 of 35.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | D2026-16 is readable and has a fabricated-citation phrase and an AI term (pattern check, not blind) | **not testable** | its PDF has no text layer |
| P2 | D2025-13 is readable and has a fabricated-citation phrase (pattern check, not blind) | **held** | found |
| P3 | 2 to 4 proceedings have a readable decision with a fabricated-citation phrase | **failed** | 1 |
| P4 | fewer than 5 proceedings have a readable decision that mentions an AI term | **held** | 1 |
| P5 | at least one fabricated-citation decision cites the USPTO's April 2024 AI guidance (89 FR 25609) | **failed** | 0 of 1 |
| P6 | every fabricated-citation decision cites 37 C.F.R. 11.101 (competence) | **failed** | 0 of 1, but see the hand check |
| P7 | at least half cite 37 C.F.R. 11.18 (signature and certification) | **held** | 1 of 1 |
| P8 | the database has exactly one USPTO row, and it matches a readable decision (not blind) | **failed** | one row (D2026-16); it matches, but that decision is not readable |
| P9 | at least one fabricated-citation proceeding is not in the database (not blind for D2025-13) | **held** | D2025-13 |

Four held, four failed, one not testable. P3 and P8 failed mainly because D2026-16 could not be read, not because the world differed from the plan.

## Hand check (as promised in the plan; the verdicts stay as graded)

The agents read the full text of the one flagged decision.

- **D2025-13 is a true match.** It is a settlement final order. In a TTAB cancellation proceeding (No. 92077944), a lawyer new to trademark practice filed a trial brief on 17 September 2023. The other side's rebuttal brief, and then the TTAB's non-precedential opinion of 7 February 2024, found quotations that do not appear in the cited decisions, cases cited for points they do not discuss, and cases that **do not exist** (for example "E.J. Brach Corp. v. Gilbert/Robinson, Inc., 185 USPQ 597 (TTAB 1975)"). The TTAB was "at a loss for words that adequately express the gravity" of citing fictitious decisions. The respondent said he found the citations through internet searches of "blog posts and articles" and never read the decisions. He also said that he used a generative AI tool only to learn how TTAB proceedings work, not to draft the brief. The order publicly reprimands him and requires **two hours of CLE "on the topic of the use of generative AI in legal practice"**.
- **So the AI term is the respondent's denial, not a finding.** The census's `ai_mention` and `ai_citation` flags are correct as defined, but no one has found that AI produced these citations. We count it as a fabricated-citation decision that *mentions* AI.
- **P6 is a pattern miss.** The decision does cite the competence rule. Its text layer is itself an OCR of a scan and renders "11.101" as "I I.IOI", so the frozen pattern `\b11\.101\b` missed it. The agreed violations are 37 C.F.R. 11.101, 11.103, 11.301, 11.804(c) and 11.804(d), with the inquiry duty of 11.18 as the basis. **Corrected P6: 1 of 1.** Addendum 1 adds OCR-tolerant rule patterns for this reason.
- **P5 has a timing explanation.** The brief was filed in September 2023, seven months before the USPTO's April 2024 AI guidance existed. The order does not cite the guidance.
- **Who caught it first, and does the tracker list that ruling?** The TTAB, on 7 February 2024 (prompted by the opposing party). Neither the TTAB opinion nor the USPTO's own reprimand is in the database CSV the job downloaded (no row mentions the proceeding number, the cancellation number or the fake "E.J. Brach" case). The database does list the lawyer's reciprocal **public censure in New York** (row 764, court "SC New York", 13 November 2025), and that row's description refers to the TTAB brief.

## What this means

1. **A text search cannot see half of the 2026 archive.** Nearly half the decisions OED posted in 2026 are image-only PDFs. Anyone who searches the reading room's text (a researcher, a journalist, a tracker, or a model) cannot see them, and screen readers cannot read them either. A practitioner blog, IPethics & INsights, runs [its own search engine](https://ipethicslaw.com/new-uspto-discipline-search-engine-added-to-ipethics-insights/) over OED decisions with written synopses. A search on 13 November 2026 found no published count of how many reading-room PDFs have no text layer. We do not know why it changed. Addendum 1 will report what each PDF's metadata says made it.
2. **Same pattern as the rest of the series.** As with the [MSPB](mspb-citations.md), the [BIA](bia-citations.md) and the [NLRB and WCAB hand list](agency-hand-list.md), the database is strongest on court rulings. Here it holds the state-court follow-on, while the agency tribunal that first found the fake cases (the TTAB) and the federal regulator's discipline are missing.
3. **The regulator acts under its general conduct rules.** D2025-13 relies on competence, diligence, meritorious contentions and misconduct, not on any AI rule. That fits MV2's [agency AI-authority census](agency-ai-authority.md). The CLE order is the one place AI shows up in the sanction.

## Limits

The reading room holds what OED chose to publish, and settled matters are described in the parties' agreed words. Until Addendum 1 is graded, nearly half of 2026 is unread. Regular expressions miss unusual wording and OCR errors (P6 shows one). The job kept full texts only for flagged decisions. The census counts what decisions say. It does not judge any practitioner or official, and it is not legal advice. As the plan promised, `rows.csv` has proceeding numbers and PDF hashes but no names. The USPTO's reading room publishes the names.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `f828f95f...` (2,200,099 bytes), fetched 2026-11-13T09:45:55Z. Decisions read from foiadocuments.uspto.gov, one request every 3 seconds, 2026-11-13 09:45-09:55 UTC. Full outputs: [results/](uspto-oed-citations/results/) (`results.md`, `results.json`, `rows.csv`, `listing.json`, `sources.json`, `status.json`). Text of this write-up: CC BY 4.0. Code: Apache-2.0.
