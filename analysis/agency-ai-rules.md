# AI filing rules of U.S. administrative tribunals: a first open list

*MV2, Munim, Inc. (mv2@munimtech.com), 12 November 2026 (version 0.3.0). Made with AI agents working in MV2's
name. Data: [`data/agency_ai_rules.json`](../data/agency_ai_rules.json) (CC BY 4.0), tests:
[`test_agency_ai_rules.py`](../test_agency_ai_rules.py) (Apache-2.0). Information about public documents, not
legal advice.*

## Why this list

Several public trackers follow the AI rules courts set for filers. The largest one we know of,
legalaigovernance.com's court-order tracker, listed 251 instruments when we read it on 12 November 2026. Ropes &
Gray, RAILS and others cover courts too. **Administrative tribunals** are different: agency judges and boards that
hear workers' compensation, tax, utility, labor, immigration and benefits cases. Many people come before them
without a lawyer. We found no list that collects their AI rules. The court tracker includes four of them (EOIR,
USPTO, the Idaho OAH's judge policy and an FTC ALJ order), filed under court categories, and mentions a fifth
(OCAHO) inside another entry.

This file starts that list with 16 instruments: 7 federal and 9 state. Eleven of them are not in the court
tracker. Two of the entries (USPTO and the IRS) regulate practice before an agency rather than a single
tribunal; they are included because their rules reach the same filings.

## What the 16 say

| Tribunal | Instrument | Date | Disclosure of AI use | In court tracker |
|---|---|---|---|---|
| DOL Administrative Review Board | "Super Intelligence" page, model note | undated | required if used | no |
| DOL Office of Administrative Law Judges | Order 2026-MIS-00004 | 2026-07-08 | not yet checked | no |
| DOJ EOIR (immigration courts, BIA) | Policy Memo 25-40 | 2025-08-08 | not required | yes |
| DOJ EOIR, OCAHO | *Wallcon*, 21 OCAHO no. 1630; Practice Manual 2.9(d) | 2025-01 | not required | partly |
| FTC Office of ALJs (Judge Himes) | certification in each certificate of service (case orders) | since 2024-09 | every filing | yes |
| IRS Office of Professional Responsibility | Alert 2026-19, responsible AI use in federal tax practice | 2026-06-24 | not required (to the IRS) | no |
| USPTO (PTAB, TTAB) | 89 FR 25609 guidance | 2024-04-11 | not required | yes |
| California Public Employment Relations Board | *Atwater*, PERB Decision No. 2995-E (precedential), notice and FAQ | 2025-12-15 | not required | no |
| Georgia Board of Workers' Compensation | Standing Order on AI and citations | 2026-08-26 | every filing | no |
| Idaho OAH | Policy 25-1 (binds its judges) | 2025-09-24 | on the judge's request (disputed, see notes) | yes |
| Idaho OAH rules (IDAPA 62.01.01) | proposed Sections 011-012 | proposed 2025-10-01 | on request (**rejected**) | no |
| Massachusetts CERB | Statement Regarding the Use of AI | ~Sept 2026 | not yet checked | no |
| Minnesota PUC | AI Policy (reads Minn. R. 7829.0250) | undated | "should" disclose | no |
| Montana DOR Office of Dispute Resolution | MAR Notice 2026-169.2 (ODR rules) | in effect 2026-09-26 | required if used | no |
| South Carolina Workers' Compensation Commission | bench order, interim generative-AI policy | 2026-06-17 | signed statement on memoranda a Commissioner asks for | no |
| Texas SOAH | Chief ALJ Advisory on AI | 2025-10-09 | not yet checked | no |

## Findings

1. **Agencies split the same way courts did, but the strict end is stricter.** Georgia's workers'-comp board
   requires every filing to carry either an AI-assistance statement or a no-AI certification. The board also
   says undisclosed AI-made *evidence* can bring civil penalties or a referral to its Criminal Investigation
   Division. The FTC judge's certificate is also required on every filing. At the other end, EOIR, OCAHO, the
   USPTO, the IRS and California's PERB ask for no disclosure and say existing duties apply. That is the same
   "verify, don't disclose" turn that several state supreme courts made for courts in 2026.
2. **Two clusters: workers' compensation and public-sector labor boards.** Two of the nine state instruments
   come from workers' compensation agencies in neighbouring states, both from summer 2026: South Carolina's
   Commission (17 June 2026) and Georgia's Board (26 August 2026). Two more come from public-sector labor boards:
   California's PERB, which set its rule by a precedential decision in December 2025, and Massachusetts's CERB,
   which issued a statement in about September 2026. None of the four is in the court tracker. California's
   Workers' Compensation Appeals Board has no rule we found, but it has sanctioned AI-fabricated quotations in a
   2026 panel decision.
3. **Some agencies make their AI rule by deciding a case.** California's PERB and the federal OCAHO did not
   issue an order or a rule. Each decided a case and made it the reference: PERB's *Atwater* decision (15
   December 2025) holds that failing to verify AI-generated citations is bad-faith conduct and that extensive
   reliance on nonexistent PERB decisions violates PERB Regulation 32635(a). PERB now prints a banner pointing to
   that decision on its decision pages. A court-rule tracker that looks only for orders and rules will miss
   this kind of instrument. PERB's own decision summaries also show the rule in use: see
   [`perb-fabricated-authority.md`](perb-fabricated-authority.md).
4. **A state's general administrative-procedure AI rule was rejected by its legislature.** Idaho's
   Office of Administrative Hearings, whose procedural rules govern contested cases across state agencies,
   proposed rules that would let a presiding officer ask parties for AI-use statements and would require agencies
   to label orders written with generative AI. The House committee excepted those sections, and the July 2026
   Idaho Administrative Bulletin lists Sections 011, 012 and 515 as "rejected by SCR 128". The rest of the docket
   took effect on 1 July 2026. Montana went the other way for one agency: its Department of Revenue now has AI
   disclosure in its dispute-resolution rules, in effect 26 September 2026, making it the only codified agency AI
   rule for parties in this list that is in force. The court tracker's Idaho entry does not mention the rejection.
5. **The federal "Super Intelligence" rename has reached the filing rules.** Executive Order 14434 (2 Oct
   2026) tells executive agencies to say "Super Intelligence (SI)". The Labor Department's Administrative Review
   Board's filing note now uses only that term. The Office of Administrative Law Judges' home page calls its
   8 July order the "July 8 Order on Super Intelligence", while its Notices page and the file name still say
   "Artificial Intelligence". Anyone searching federal agency pages for "AI" filing rules will now miss some.
   (MV2's pre-registered [Federal Register census](si-rename-census/PLAN.md) measures this for the Register; it
   does not cover agency web pages, so this observation is outside that study.) The IRS alert predates the order
   and still says "artificial intelligence". State agencies are not covered by the order.
6. **Most agency instruments are not rules.** Of the 16, two are codified rules (one rejected), and the others
   are orders, an advisory, policies, guidance documents, two precedent decisions and a web page. Several cite no
   authority at all. Minnesota's PUC rests its policy on an existing representations rule, Texas SOAH on its
   good-faith filing rule (1 TAC 155.303), PERB on its appeal-content regulation (32635(a)), and the IRS on
   Circular 230's due-diligence, competence, fee and supervision sections (31 CFR 10.22, 10.27, 10.35, 10.36).

## How this was checked, and its limits

- Every entry links the issuer's own copy. `source_check` says how far each was checked.
  **issuer_page** (5): the fields were read on the issuer's own HTML page. **issuer_listing** (4): the issuer's
  own page lists the title and date, but the document's wording comes from secondary sources. **secondary** (7):
  so far only secondary sources and search-index text of the issuer's file. Fields we could not confirm say
  `unverified`.
- Sources disagree on one field. Secondary sources say the Idaho OAH's Policy 25-1 lets judges ask parties for
  an AI disclosure; the court tracker's entry says it imposes no duty on parties or counsel. The entry keeps
  `on_request` until the text check below.
- A sealed job (`agencyrules-v1`) fetches the issuer files for the first 13 entries once, at one request every
  10 s, and keeps short excerpts so a person can check every field before any entry is upgraded. It was still
  waiting for compute when 0.3.0 was published. The South Carolina file is partly a scanned image and needs a
  text (OCR) check. Results will be added as a dated update.
- This is a **convenience list**, not a census. It comes from searches on 12 November 2026 and from tribunals
  met in MV2's earlier citation studies. There are thousands of state agency adjudicators, so absence from this
  list means nothing. Searches on 12 November 2026 found no AI filing rule at: state offices of administrative
  hearings other than Idaho and Texas (including New Jersey, Maryland, Michigan, Colorado and Washington),
  unemployment appeal boards, state tax tribunals, the North Carolina Industrial Commission, Florida's Judges
  of Compensation Claims, the Tennessee Court of Workers' Compensation Claims (which has run AI training for
  lawyers), the Virginia and New York workers' compensation agencies, Washington's Board of Industrial
  Insurance Appeals, Colorado's Industrial Claim Appeals Office, public employment boards other than
  California's and Massachusetts's, the Copyright Claims Board, and utility commissions other than
  Minnesota's. California's Office of Tax Appeals was reported in July 2026 to be considering guidance.
  Additions with an issuer link are welcome as GitHub issues.
- "Not in the court tracker" means we did not find it on legalaigovernance.com's court-order tracker on
  12 November 2026. That tracker covers courts; this is not a criticism of it.

## Changes

- **0.3.0 (12 November 2026):** added California's Public Employment Relations Board (*Atwater*, PERB Decision
  No. 2995-E, 15 December 2025, with PERB's notice and FAQ), read on PERB's own pages; recorded the
  public-sector labor-board cluster, rules made by precedent decision, and the wider set of tribunals searched
  without a find.
- **0.2.0 (12 November 2026):** added the South Carolina Workers' Compensation Commission's bench order
  (17 June 2026) and the IRS Office of Professional Responsibility's Alert 2026-19 (24 June 2026); noted the
  sources' disagreement on the Idaho OAH policy and the secondary report that the DOL OALJ order rests on
  29 CFR 18.35(b)-(c).
- **0.1.0 (12 November 2026):** first list, 13 instruments.

Licence: data and text CC BY 4.0; code Apache-2.0.
