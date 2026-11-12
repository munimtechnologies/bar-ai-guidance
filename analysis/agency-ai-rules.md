# AI filing rules of U.S. administrative tribunals: a first open list

*MV2, Munim, Inc. (mv2@munimtech.com), 12 November 2026. Made with AI agents working in MV2's name.
Data: [`data/agency_ai_rules.json`](../data/agency_ai_rules.json) (CC BY 4.0), tests:
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

This file starts that list with 13 instruments: 6 federal and 7 state. Eight of them are not in the court
tracker.

## What the 13 say

| Tribunal | Instrument | Date | Disclosure of AI use | In court tracker |
|---|---|---|---|---|
| DOL Administrative Review Board | "Super Intelligence" page, model note | undated | required if used | no |
| DOL Office of Administrative Law Judges | Order 2026-MIS-00004 | 2026-07-08 | not yet checked | no |
| DOJ EOIR (immigration courts, BIA) | Policy Memo 25-40 | 2025-08-08 | not required | yes |
| DOJ EOIR, OCAHO | *Wallcon*, 21 OCAHO no. 1630; Practice Manual 2.9(d) | 2025-01 | not required | partly |
| FTC Office of ALJs (Judge Himes) | certification in each certificate of service (case orders) | since 2024-09 | every filing | yes |
| USPTO (PTAB, TTAB) | 89 FR 25609 guidance | 2024-04-11 | not required | yes |
| Georgia Board of Workers' Compensation | Standing Order on AI and citations | 2026-08-26 | every filing | no |
| Idaho OAH | Policy 25-1 (binds its judges) | 2025-09-24 | on the judge's request | yes |
| Idaho OAH rules (IDAPA 62.01.01) | proposed Sections 011-012 | proposed 2025-10-01 | on request (**rejected**) | no |
| Massachusetts CERB | Statement Regarding the Use of AI | ~Sept 2026 | not yet checked | no |
| Minnesota PUC | AI Policy (reads Minn. R. 7829.0250) | undated | "should" disclose | no |
| Montana DOR Office of Dispute Resolution | MAR Notice 2026-169.2 (ODR rules) | in effect 2026-09-26 | required if used | no |
| Texas SOAH | Chief ALJ Advisory on AI | 2025-10-09 | not yet checked | no |

## Findings

1. **Agencies split the same way courts did, but the strict end is stricter.** Georgia's workers'-comp board
   requires every filing to carry either an AI-assistance statement or a no-AI certification. The board also
   says undisclosed AI-made *evidence* can bring civil penalties or a referral to its Criminal Investigation
   Division. The FTC judge's certificate is also required on every filing. At the other end, EOIR, OCAHO and the
   USPTO say outright that no disclosure is required and that existing duties apply. That is the same "verify,
   don't disclose" turn that several state supreme courts made for courts in 2026.
2. **A state's general administrative-procedure AI rule was rejected by its legislature.** Idaho's
   Office of Administrative Hearings, whose procedural rules govern contested cases across state agencies, proposed rules that would let a presiding officer ask parties for
   AI-use statements and would require agencies to label orders written with generative AI. The House committee
   excepted those sections, and the July 2026 Idaho Administrative Bulletin lists Sections 011, 012 and 515 as
   "rejected by SCR 128". The rest of the docket took effect on 1 July 2026. Montana went the other way for one
   agency: its Department of Revenue now has AI disclosure in its dispute-resolution rules, in effect
   26 September 2026, making it the only codified agency AI rule for parties in this list that is in force. The
   court tracker's Idaho entry does not mention the rejection.
3. **The federal "Super Intelligence" rename has reached the filing rules.** Executive Order 14434 (2 Oct
   2026) tells executive agencies to say "Super Intelligence (SI)". The Labor Department's Administrative Review
   Board's filing note now uses only that term. The Office of Administrative Law Judges' home page calls its
   8 July order the "July 8 Order on Super Intelligence", while its Notices page and the file name still say
   "Artificial Intelligence". Anyone searching federal agency pages for "AI" filing rules will now miss some.
   (MV2's pre-registered [Federal Register census](si-rename-census/PLAN.md) measures this for the Register; it
   does not cover agency web pages, so this observation is outside that study.)
4. **Most agency instruments are not rules.** Of the 13, two are codified rules (one rejected), and the others
   are orders, an advisory, policies, guidance documents, a precedent decision and a web page. Several cite no
   authority at all. Minnesota's PUC rests its policy on an existing representations rule, and Texas SOAH on its
   good-faith filing rule (1 TAC 155.303).

## How this was checked, and its limits

- Every entry links the issuer's own copy. `source_check` says how far each was checked.
  **issuer_page** (3): the fields were read on the issuer's own HTML page. **issuer_listing** (4): the issuer's
  own page lists the title and date, but the document's wording comes from secondary sources. **secondary** (6):
  so far only secondary sources and search-index text of the issuer's file. Fields we could not confirm say
  `unverified`.
- A sealed job (`agencyrules-v1`) fetches each issuer's file once, at one request every 10 s, and keeps short
  excerpts so a person can check every field before any entry is upgraded. Results will be added as a dated
  update.
- This is a **convenience list**, not a census. It comes from searches on 12 November 2026 and from tribunals
  met in MV2's earlier citation studies. There are thousands of state agency adjudicators, so absence from this
  list means nothing. Additions with an issuer link are welcome as GitHub issues.
- "Not in the court tracker" means we did not find it on legalaigovernance.com's court-order tracker on
  12 November 2026. That tracker covers courts; this is not a criticism of it.

Licence: data and text CC BY 4.0; code Apache-2.0.
