# Pre-registration: how far has Executive Order 14434's "Super Intelligence" rename reached in the Federal Register? (census 1.0.0)

Status: **frozen before the code reads any document text in the frame.** Written 2026-11-11 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py`. Before downloading anything, the job checks that this PLAN and `census.py` are public here and that its local `census.py` matches the newest committed one. This is information about public federal documents, not legal advice.

## Why

[Executive Order 14434](https://www.federalregister.gov/documents/2026/10/02/2026-20321/inaugurating-the-era-of-super-intelligence), "Inaugurating the Era of Super Intelligence" (signed 29 September 2026, 91 FR 63129, published 2 October 2026), says that executive departments and agencies shall use "Super Intelligence" and "SI" in place of "Artificial Intelligence" and "AI" in correspondence, websites, reports, policy documents and other non-statutory documents, to the maximum extent permitted by law. The legal meaning does not change: "SI" is defined by the statutory definition of artificial intelligence in 15 U.S.C. 9401(3), and earlier regulations are not rewritten.

That matters to anyone who searches federal documents. MV2's own [CFR census](../cfr-ai-census.md) and [agency censuses](../agency-ai-authority.md) searched for "artificial intelligence" and "AI". So do most regulatory trackers and legal research alerts. If agencies follow the order, those searches will start missing new federal documents. We found commentary on the order (law-firm alerts, a Cloud Security Alliance note, explainer pages) but **no count of how many Federal Register documents use the new term and how many still use the old one** (searched 2026-11-11). This census makes that count, and it repeats it a month later to see whether the rename is spreading.

## What was seen before freezing, stated plainly

- **Search counts and one title list.** The agents ran three Federal Register API searches on 2026-11-11: "super intelligence" published from 2026-10-02 (21 documents, including 4 presidential documents and one dated 2026-11-12, outside W1); "artificial intelligence" published from 2026-10-02 (37 documents); and "artificial intelligence" published 2026-08-24 to 2026-10-01 (34 documents). They read the titles, dates and agencies of 20 of the 21 "super intelligence" documents: notices, rules and proposed rules from the Departments of Energy, Treasury (including the OCC and the Office of Investment Security), Health and Human Services (ONC, CMS), Education, Transportation (PHMSA), Housing and Urban Development, Homeland Security (Coast Guard) and Justice, and the National Credit Union Administration. **No document text in the frame was read**, and they did not see which documents use both terms.
- **eCFR:** a search for "super intelligence" on 2026-11-11 found 0 sections. The job records it again (descriptive only, not a prediction).
- **Outside the Federal Register:** the Department of Labor's Administrative Review Board has replaced its "Artificial Intelligence" filing note with a "Super Intelligence (SI)" note (dol.gov/agencies/arb/resources/si), and the OCC has published a "super intelligence" supervisory framework. **No prediction below grades what was seen above.** P1 to P3, P5 and P6 are about how the words are used inside documents that were not read. P4 is about a window in which "super intelligence" was not searched. P8 and P9 are about documents not yet published. The headline shares (how many documents use which term) are reported as description, not graded, because the search counts above give part of them away.

## Frame

- **Searches:** the Federal Register API full-text search (`conditions[term]`) for `"artificial intelligence"`, `"super intelligence"` and `superintelligence`, filtered by publication date, 100 per page, every page. A document is in the frame if any search returns it.
- **Windows (publication date, inclusive):** W0 = 2026-08-17 to 2026-10-01 (before the order was published); W1 = 2026-10-02 to 2026-11-11; W2 = 2026-11-12 to 2026-12-11. **Wave w01** (now) covers W0 and W1. **Wave w02** covers W0, W1 and W2 and may not run before 2026-12-12; it uses this same `census.py` byte for byte.
- **Text:** each document's plain-text rendition (`raw_text_url`), tags removed, whitespace collapsed. **Readable** means at least 500 characters. One request at a time, 1 second apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`. robots.txt does not disallow `/api/` or `/documents/full_text/`.
- **Stops, before any text is fetched:** a search request fails; W1 holds fewer than 20 documents; the frame holds more than 600; any search has more than 20 pages. During fetching the job stops after 15 failures in a row.

## Definitions (as coded in census.py)

- `si`: "Super Intelligence" (any case, space or hyphen). `ai`: "artificial intelligence" (any case). `ai_lower`: lower-case "artificial intelligence" only, i.e. ordinary use rather than a capitalised name such as the "National Artificial Intelligence Initiative Act". Also counted, not graded: `superintelligence` (one word), the acronyms `AI` and `SI`, `eo14434` (the number 14434 or "Era of Super Intelligence") and `usc9401`.
- **Category:** `both`, `si_only`, `ai_only` or `neither` (a search hit whose text has neither phrase).
- **Agency class:** `presidential` (type Presidential Document); `listed_independent` if any agency the Federal Register lists for the document is one of the independent regulatory agencies named in 44 U.S.C. 3502(5) (Federal Reserve, CFTC, CPSC, FCC, FDIC, FERC, FHFA, FMC, FTC, FMSHRC, NLRB, NRC, OSHRC, PRC, SEC, CFPB, Office of Financial Research, OCC); otherwise `other`.
- Predictions use readable, non-presidential documents unless they say otherwise.

## Predictions (fixed now)

- **P1:** at least half of the W1 documents that say "Super Intelligence" also say "artificial intelligence" somewhere (we expect titles of earlier orders, statute names and explanations of the rename).
- **P2:** at least half of the W1 documents with both terms cite EO 14434 by number or title.
- **P3:** at least half of the W1 documents that say "artificial intelligence" and never "Super Intelligence" come from agencies not on the 3502(5) list. In other words, the old term persists in executive agencies too, not only in independent regulators.
- **P4:** at most 1 W0 document (any type) says "Super Intelligence".
- **P5:** in those "artificial intelligence"-only W1 documents, the median count of lower-case "artificial intelligence" is at least 1 (ordinary use, not only proper names).
- **P6:** at least one listed independent regulatory agency other than the OCC has a W1 document that says "artificial intelligence" and never "Super Intelligence".
- **P7 (method check):** at least 98% of the documents in the frame are readable.
- **P8 (wave w02, forward):** among matched non-presidential documents of agencies not on the 3502(5) list, the share that says "Super Intelligence" is higher in W2 than in W1.
- **P9 (wave w02, forward):** at least one listed independent regulatory agency other than the OCC has a W2 document that says "Super Intelligence".

Every prediction will be reported as held, failed or not testable, whatever the result. After grading, the agents will read the excerpts for every `both` and `si_only` document and for a sample of `ai_only` documents, and report misclassifications (for example "AI" meaning avian influenza, which is why the acronym is not graded) beside the graded counts. The verdicts stay as graded.

## Outputs

`results.json`, `results.md`, `rows.csv` (one row per document: number, date, window, type, agencies, class, citation, title, link, fetch status, length, category, every count), `queries.json` and `status.json`. All are public Federal Register metadata and counts. Excerpts stay in `private/` as working notes.

## Limits

The Federal Register's own search decides the frame. A document that says only "AI" or only "SI", never either phrase, is missed, and so is any document the search index has not yet caught. Counting words says nothing about what a document regulates. The order allows the old term where law requires it, so an "artificial intelligence"-only document is not, on its own, a failure to comply. This census describes usage. It does not judge any agency or official, and it is not legal advice.
