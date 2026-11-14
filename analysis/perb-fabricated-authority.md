# California PERB: four Board decisions on fabricated authority in eleven months; the main tracker lists one

*MV2, Munim, Inc. (mv2@munimtech.com), 12 November 2026, updated 14 November 2026. Made with AI agents working in
MV2's name. A hand check of public records, not a census. Information about public documents, not legal advice.
Text CC BY 4.0.*

## What we checked

California's Public Employment Relations Board (PERB) decides unfair-practice and representation cases for
public employers, unions and employees. It posts a summary of every month's Board decisions and orders on its
own site. We read PERB's monthly summaries from December 2025 to October 2026 (11 months, 88 decisions and
administrative orders) on perb.ca.gov on 12 November 2026, then read the decision page of each decision whose
summary says a filer cited fabricated, fictitious or nonexistent authority.

We compared the result with the AI Hallucination Cases Database (damiencharlotin.com), the largest public
tracker of rulings on fabricated citations, using a copy downloaded on 11 November 2026.

## Result

| PERB Decision No. | Issued | Precedential | What PERB's own page says | In the tracker |
|---|---|---|---|---|
| [2995-E](https://perb.ca.gov/decision/2995e/) (*Atwater Elementary Teachers Association, CTA/NEA*) | 2025-12-15 | yes | all legal citations in the appeal were fabricated, created by generative AI tools; no sanction, warning for future cases | **yes** |
| [3037-H](https://perb.ca.gov/decision/3037h/) (*Teamsters Local 2010*) | 2026-07-06 | no | the charging party's "abuse of PERB's processes by citing to fabricated authority" was a further independent reason for the decision | no |
| [3040-M](https://perb.ca.gov/decision/3040m/) (*AFSCME Local 2076*) | 2026-07-15 | no | the Office of the General Counsel had admonished the charging party for "citations to six nonexistent PERB decisions" | no |
| [3041-H](https://perb.ca.gov/decision/3041h/) (*Regents of the University of California and UC-AFT*) | 2026-07-16 | yes | abuse of process, including documents "containing fictious [sic] legal authority"; the Board imposed non-monetary litigation sanctions | no |

- **4** of the 88 decisions and orders in eleven months address fabricated or nonexistent authority, all in
  cases brought by individual charging parties. Three of the four came in a single month (July 2026).
- **The tracker lists 1 of the 4** (*Atwater*). It has no row for the three July 2026 decisions, including
  3041-H, a precedential decision that imposed sanctions.
- **Only *Atwater* says AI produced the citations.** The pages for 3037-H, 3040-M and 3041-H do not say how the
  fabricated authority arose. The tracker also lists rulings where AI use is implied or unidentified, so this
  is a coverage gap worth a look rather than a clear error.
- PERB set its AI rule through *Atwater* rather than by regulation; it is entry `us-ca-perb-atwater-2995e` in
  [`data/agency_ai_rules.json`](../data/agency_ai_rules.json).

## Beyond the four Board decisions

*Added 14 November 2026.* Below the Board, one of PERB's administrative law judges struck a pre-hearing brief
filed by the Trustees of the California State University in Case No. LA-CE-1433-H (17 November 2025) because it
quoted passages and cited pages that do not exist in the one federal appellate decision it relied on. The order
says the brief bears the hallmarks of AI-generated text; the University later told the press that a staff
member's AI use caused the errors. Unlike the four Board decisions, the filer here was an employer. The order
does not appear on perb.ca.gov, and the tracker had no row for it on 14 November 2026. Details and sources:
[agency-hand-list.md](agency-hand-list.md#california-perb-a-public-universitys-brief-struck-by-an-administrative-law-judge).

## Limits

- We read PERB's **summaries and decision pages**, not the full decision texts. A decision whose summary does
  not mention fabricated authority could still discuss it, so 4 is a floor for this period. The other three
  decisions' full texts may say more about AI.
- The period starts with *Atwater*, which PERB called a matter of first impression; we did not read earlier
  summaries. November 2026 decisions were not yet summarised.
- ALJ orders and proposed decisions are outside this note's count; the one above was found by a web search, not
  by a search of PERB's records.
- Case names are given as PERB cites them, without the individual charging parties' names.
- "Not in the tracker" means not found in our 11 November 2026 copy by decision number, union, employer or
  party name. The tracker grows daily and may add them.

## What comes next

A full-text census of PERB Board decisions, pre-registered before any decision text is read, would settle how
often fabricated authority appears and whether the full texts tie it to AI. It joins MV2's series comparing
tribunals' own records with the tracker (FLRA, U.S. Tax Court, MSPB, and pre-registered studies of BIA,
California's Office of Tax Appeals and New York's tax tribunals).
