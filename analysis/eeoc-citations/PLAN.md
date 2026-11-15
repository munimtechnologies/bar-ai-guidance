# Pre-registration: fabricated or misattributed citations in EEOC federal-sector appeal decisions (hand search 1.0.0)

Status: **frozen before the full text of any flagged decision was read.** Written 2026-11-15 by AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions of the U.S. Equal Employment Opportunity Commission, not legal advice. Text CC BY 4.0.

## Why

MV2's tribunal-archive series compares tribunals' own records with the main public tracker of AI-fabricated citations, the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0). So far it covers the [FLRA](../flra-ai-citations.md), the [U.S. Tax Court](../tax-court-citations.md), the [MSPB](../mspb-citations.md), the [BIA](../bia-citations.md), the [New York tax tribunals](../nydta-citations.md), the [California OTA](../ota-citations.md), the [California WCAB](../wcab-citations.md) and a [hand-checked list](../agency-hand-list.md). A census of the Labor Department's Employees' Compensation Appeals Board is [pre-registered](../ecab-citations/PLAN.md) and waiting for compute.

The EEOC's Office of Federal Sector (until 2025, the Office of Federal Operations) decides appeals from federal employees' discrimination complaints. Many complainants appear without a lawyer. The Commission names them with random pseudonyms (a first name and an initial). On 15 November 2026 the tracker's live search returned **0 rows** for "EEOC", "Equal Employment" and "Equal Employment Opportunity". It returned 0 for the appeal number 2026001205. For the pseudonym "Shon" it returned 4 rows, none of them EEOC.

## Why a hand search, not a census

eeoc.gov's robots.txt (read 15 November 2026) disallows automated access to `/sites/default/files/decisions/` and `/sites/default/files/migrated_files/decisions/`, where the decision files live. MV2 respects that, so no crawler downloads EEOC decisions. Instead, the agents ran a small number of searches on the Commission's own decision search page (https://www.eeoc.gov/federal-sector/appellate-decisions, parameter `appellate_keywords`; that page is not disallowed). They read the result snippets through a summarizing web reader. The three flagged decisions will be read in full in an ordinary browser, one at a time.

## Search log, 15 November 2026 (result counts as the search page showed them)

| Query | Results | Flagged |
|---|---|---|
| "artificial intelligence" | 2 | 0 (an agency chat program; a job title) |
| ChatGPT | 0 | 0 |
| "artificial intelligence" OR "generative AI" OR ChatGPT | 0 | 0 |
| hallucinated / "hallucination" | 32 / 32 | 0 on page 1 (all medical) |
| "AI" hallucinations | 1 | 2026001205 |
| hallucinations cited decisions | 14 | 2026001205 |
| "generative" | 1,124 | 0 on page 1 (stemmed to "generate") |
| "nonexistent" | 102 | 0 on page 1 |
| "fictitious" | 50 | 0 on page 1 |
| "non-existent" decisions cited | 34 | 0 on page 1 |
| fabricated citations | 81 | 0 on page 1 |
| "do not exist" cited | 17 | 2026000158, 2025000648 (all 17 read) |
| "unable to locate" citation | 25 | 2026001205 (all 25 read; 2022005090 is about a prior Commission decision in a procedural sense, not a bad citation) |
| "could not locate" decisions cited | 77 | 0 on page 1 |
| "do not stand for the proposition" | 2 | 2026000158 |
| "case citations" exist | 9 | 2026000158 |
| "cited to five cases" | 1 | 2025000648 |
| "Office of Federal Sector" | 2,745 | (size of the post-rename collection; not searched further) |

The search is ranked by relevance and stems words. "Page 1" means the first 10 results only. Passages the search never surfaced are not covered.

## The three flagged decisions (from search snippets only)

The file folder date is when the file was posted, not necessarily the decision date.

1. **Appeal No. 2026000158** (posted 2026-05-27; Department of Veterans Affairs). Snippet: the Commission notes "that Complainant's appeal brief contains several case citations that either do not exist, or do not stand for the proposition for which they are cited," followed by a reminder about due diligence. No AI term was seen.
2. **Shon T. v. Bisignano (Social Security Administration), Appeal No. 2026001205** (posted 2026-09-08). Snippet: the Agency was "unable to locate most of the decisions cited by Complainant" and "suggested that these citations might be the result of AI 'hallucinations.'" The Commission writes, "Upon our independent review, we concur with ..." (the snippet is cut off there).
3. **Domingo M. v. Collins (Department of Veterans Affairs), Appeal No. 2025000648** (posted 2026-10-15). Snippet: "Attorney's submission in the instant appeal cited to five cases as Commission precedent supporting a greater ..." and, about a cited decision, "... the parties represented nor the premise for which it was cited." The Commission affirms the Agency's final decision.

## Predictions for the full reading (fixed now)

- **E1:** read in full, each of the three decisions says in the Commission's own words that a filing in the appeal cited authority that does not exist, cannot be found, or does not say what it was cited for.
- **E2:** exactly one of the three (2026001205) mentions AI.
- **E3:** none of the three imposes a sanction beyond a reminder or warning, and none says the bad citations changed the outcome.
- **E4 (partly not blind):** in 2025000648 the citations came from the complainant's attorney, as the snippet says. In 2026000158 and 2026001205 they came from complainants without an attorney.
- **E5 (not blind):** on the day of reading, the tracker lists none of the three.

Each prediction will be reported as held, failed or not testable. For each decision the write-up will give the decision date, who filed the citations, what the Commission found and did, whether AI is named, and the quoted passages. Lawyers' and judges' names are left out. The complainants' pseudonyms are the Commission's own.

## Limits

This is a keyword search of one search engine, not a census. Decisions describe only what the Commission chose to write about, and a bad citation that a decision does not mention stays invisible. A decision that describes one in other words, or one the search ranks low, would be missed. Three flagged decisions say nothing about how common the problem is. The search counts what decisions say. It does not judge any complainant, representative, agency or official.
