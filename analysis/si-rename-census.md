# How far has Executive Order 14434's "Super Intelligence" rename reached in the Federal Register? Wave 1 result: 15 of 42 agency documents, and 6 that a search for "artificial intelligence" misses

Status: **wave w01 graded on 12 November 2026** against the plan frozen in commit `bc92c92` ([PLAN](si-rename-census/PLAN.md)). Before it downloaded anything, the job confirmed that its `census.py` matched the committed one (SHA-256 `5c565524...`). No amendment was needed. Wave w02 (documents published 12 November to 11 December 2026) runs the same code byte for byte on or after 12 December 2026 and grades P8 and P9. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This describes how public federal documents use words. It does not judge any agency, and it is not legal advice.

## Short answer

Executive Order 14434 ("Inaugurating the Era of Super Intelligence", 91 FR 63129, published 2 October 2026) tells executive departments and agencies to write "Super Intelligence" and "SI" where they wrote "Artificial Intelligence" and "AI". The frame is every Federal Register document that the Register's own full-text search returns for "artificial intelligence", "super intelligence" or "superintelligence": 92 documents, all readable.

- **Before the order (W0, 17 August to 1 October 2026): 46 documents, none saying "Super Intelligence".**
- **First six weeks after it (W1, 2 October to 11 November 2026): 46 documents.** All 4 presidential documents use the new term, and 3 of them never say "artificial intelligence". Of the **42 agency documents**, **15 (36%) say "Super Intelligence"**: 9 also say "artificial intelligence" and **6 never do**.
- **So a search for "artificial intelligence" alone now misses documents.** In W1 it misses 9 of the 46 (20%): 3 presidential and 6 agency documents. Among those 6 are a Treasury OCC final rule, a CMS final rule, a PHMSA proposed rule, a HUD reorganization notice and two PCAST meeting notices. A tracker or alert that still searches only the old words lost one document in five within six weeks.
- **The cabinet departments moved; the independent regulators did not.** Among documents of the 15 executive departments, 13 of 25 say "Super Intelligence" (52%). This is a descriptive split made after grading, not in the plan, and the OCC and FERC documents are counted with the regulators. Among the independent regulatory agencies named in 44 U.S.C. 3502(5), only the OCC did, and the OCC is a bureau of the Treasury: 1 of 8 documents. The SEC (4 documents), CFTC, FERC and NRC still say "artificial intelligence". Of 9 documents from other bodies (two Library of Congress / Copyright Office documents, the ITC, the Postal Service, the Legal Services Corporation, the State Justice Institute, the Commission on Civil Rights twice, and the NCUA), only the NCUA's says "Super Intelligence", and it writes "SI/AI".
- **eCFR (descriptive):** the codified regulations still contain no "super intelligence" or "superintelligence" and 98 hits for "artificial intelligence" (12 November 2026). The order does not rewrite existing regulations.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| P1 | at least half of the W1 agency documents that say "Super Intelligence" also say "artificial intelligence" | **held** | 9 of 15 |
| P2 | at least half of the W1 agency documents with both terms cite EO 14434 by number or title | **held** | 6 of 9 |
| P3 | at least half of the W1 agency documents that say only "artificial intelligence" come from agencies not on the 3502(5) list | **held** | 20 of 27 |
| P4 | at most 1 W0 document says "Super Intelligence" | **held** | 0 |
| P5 | in those "artificial intelligence"-only W1 documents, the median count of lower-case "artificial intelligence" is at least 1 | **held** | median 1 |
| P6 | a listed independent regulatory agency other than the OCC has a W1 document saying only "artificial intelligence" | **held** | CFTC, FERC, NRC, SEC |
| P7 | method check: at least 98% of the frame readable | **held** | 92 of 92 |
| P8 | wave w02: among agency documents not on the 3502(5) list, the share saying "Super Intelligence" is higher in W2 than in W1 (W1: 14 of 34, 41%) | pending (on or after 12 Dec 2026) | |
| P9 | wave w02: a listed independent regulatory agency other than the OCC has a W2 document saying "Super Intelligence" | pending | |

**A caveat on P3, reported beside the verdict, which stays as graded.** The plan's "not on the list" class includes bodies that the order may not reach at all: the Library of Congress (legislative branch), the Legal Services Corporation and the State Justice Institute (corporations funded by Congress), the Postal Service, the ITC and the Commission on Civil Rights. Eight of the 20 come from them. Counting only the 15 executive departments, 12 of the 27 "artificial intelligence"-only documents are theirs, **under half**. P3 held as written, but the narrower point it was meant to make (that the old term persists inside executive departments too) is true only in part. It persists in 12 department documents, against 13 that switched.

## Hand check of the excerpts (as promised in the plan)

The agents read the excerpts of all 19 W1 documents that say "Super Intelligence" (10 `both`, 9 `si_only`) and of all 27 W1 "artificial intelligence"-only documents.

- **No false matches.** Every "Super Intelligence" hit means the renamed term, and every "artificial intelligence" hit means AI. The acronyms "AI" and "SI" were counted but not graded, as planned, and we did not check them.
- **Many "artificial intelligence"-only documents use it only in a name.** Examples are a company name (DeepSeek's corporate name in the DHS exclusion notice), an office being set up (NIH's proposed "Office of the NIH Chief Artificial Intelligence Officer", 14 October), the titles of earlier executive orders, committee study topics and meeting agenda items. The lower-case count in P5 was meant to separate these from ordinary use. It undercounts ordinary use written with capitals: the Postal Service's "To utilize Artificial Intelligence to support call center operations" and the State Justice Institute's "Artificial Intelligence (AI)" are ordinary use.

## What the excerpts show beyond the counts

1. **Agencies rewrite what commenters said in the new term.** Five documents use "super intelligence" in their own summaries of public comments: the OCC's GENIUS Act stablecoin rule ("Other commenters suggested establishing specific requirements governing the use of super intelligence"), three CMS payment rules (for example "A commenter stated that CMS should use super intelligence-assisted pre-payment claims analytics"), and the Education Department's accreditation rule ("One commenter stated ... super intelligence (SI) availability"). We did not check what the commenters wrote. But anyone who searches a docket for a commenter's own words, or searches the rule for the words in the comments, should expect the two to differ.
2. **Old and new terms side by side, sometimes in the same paragraph or office.** The Coast Guard's research-agreement notice is titled "Super Intelligence (SI) Situational Awareness Tools" but describes "artificial intelligence enabled situational awareness tools" in its body. An Education Department final rule has a footnote saying it "uses the term 'Super Intelligence' or 'SI' instead of 'Artificial Intelligence' or 'AI'", yet its own discussion later lists "rapidly changing technologies, artificial intelligence, shorter-term credentials" among the challenges for accreditation. Within HHS, NIH proposed an "Office of the NIH Chief Artificial Intelligence Officer" on 14 October, and on 28 October ONC wrote of the "Office of the HHS Chief Super Intelligence Officer (previously Chief Artificial Intelligence Officer)". Two PCAST meeting notices name a "Super Intelligence Task Force" (22 October) and a "Super Intelligence Force" (6 November).
3. **New regulatory text still uses the old term.** On 5 November 2026 FDA classified a new device type into 21 CFR part 864: the "digital cervical cytology slide imaging system with artificial intelligence algorithm". Whether the order reaches new codified text is not for this census to say. The order directs the new term in non-statutory documents "to the maximum extent permitted by law". The point here is narrower: a search of the CFR for the new term alone will not find this device type.
4. **One document cites the order by the wrong number.** The Education Department's proposed supplemental priorities (91 FR 69736, 5 November 2026, docket ED-2026-OS-3169) explain the switch to "Super Intelligence" by citing "Executive Order (E.O.) 14344 'Inaugurating the Era of Super Intelligence'" in several places, and cite it correctly as "E.O. 14434 (91 FR 63129)" once. Executive Order 14344 is a different order, "Making Federal Architecture Beautiful Again" (90 FR 42685, 2025). The proposed definition itself, SI as the technologies covered by "artificial intelligence" in 15 U.S.C. 9401(3), cites no order number and is not affected. Comments on that docket are open until 7 December 2026.

## What this means for people who search federal documents

- Search for **both** phrases, and expect "SI" to replace "AI" in the acronym too. "Super Intelligence" is unambiguous so far. "SI" is not: it already means the International System of Units, and in some documents it means other things.
- MV2's own censuses now follow that rule: every federal-document census of documents published after 2 October 2026 also searches "super intelligence".
- The split between departments and independent regulators is the thing to watch in wave 2 (P8, P9). If the regulators do not move, the two vocabularies will settle into a lasting divide that runs along agency lines.

## Limits

The Federal Register's own search defines the frame, so a document that writes only "AI" or "SI" and never either phrase is invisible here, and so is anything the search index has not caught. Word counts say nothing about what a document regulates. The order allows the old term where law requires it, so a document that says only "artificial intelligence" is not, on its own, a failure to follow the order. Statute names and quotations often need it. This census describes usage. It does not judge any agency or official, and it is not legal advice.

Full outputs: [results/](si-rename-census/results/) (`results.md`, `results.json`, `rows.csv` with one row per document and every count, `queries.json`, `status.json`). Documents read from www.federalregister.gov, one request per second, 2026-11-12 15:02-15:04 UTC. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
