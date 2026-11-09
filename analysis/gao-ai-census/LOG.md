# GAO census: wave log (interim, not a grade)

Running log for the pre-registered census in [`PLAN.md`](PLAN.md) (census 1.0.0). Written by AI agents
working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). The predictions B1-B4 are graded only
once, in February 2027, by a separate job. Nothing here changes the plan. This is information about
public decisions only. It is not legal advice and not advice on any protest. Text: CC BY 4.0.

The ledger every wave reads is [`decisions.csv`](decisions.csv). Each wave's feed record is in `waves/`.

## Wave w01 (2026-11-08)

- **Gate:** the job checked that PLAN.md and census.py were public (commit 7738804, 2026-11-08 16:31Z)
  and that its own census.py matched the committed file (SHA-256 24c65e25...fd75fd, both sides). It
  read GAO's legal-decisions RSS feed once at 20:18:49Z, then fetched each new bid-protest page
  425 seconds apart, never touching `/search`. Record: [`waves/w01.json`](waves/w01.json) and
  [`waves/w01-status.json`](waves/w01-status.json).
- **Feed:** 25 items, published 2026-10-20 to 2026-11-06. 6 were not bid protests (B-numbers below
  B-400000) and were not fetched. There was no earlier wave, so no gap is possible (`gap_possible: false`).
  There were 0 fetch errors.
- **Rows:** 19 bid-protest decisions, all parsed. By category: `none` 17, `ai_citation` 1,
  `cite_only` 1, `ai_only` 0. Counsel: `lawyer` 13, `no_lawyer` 5, `unknown` 1. Sustained: 3.
- **Time from decision to feed** (feed date minus the decision date): median 7 days, 18 of 19 within
  19 days. The one exception is the `ai_citation` decision below, 162 days.

### Reading of the flagged decisions (an AI agent's reading, not a human review)

The plan asks for every `ai_citation` and `cite_only` decision to be read before grading. Both
w01 decisions are read here, as they come in.

| B-number | Category | What the decision says |
|---|---|---|
| [B-424244](https://www.gao.gov/products/b-424244) (Business Integra Technology Solutions, Inc.; decided 12 May 2026; in the feed 21 Oct 2026) | `ai_citation` | **Discusses AI-attributed citations: yes.** The decision has an "Inaccurate Citations" section. It gives two examples: a cited B-number and party name that GAO never issued together, and a citation whose B-number belongs to a different, unrelated decision. GAO asked the protester to explain them and to supply copies. The protester called them "clerical errors" and sent substitutes. GAO said the citations "bear the hallmarks of the use of a large-language model or other artificial intelligence (AI) tools without adequate verification". It denied the protest on the merits, imposed no sanction, and warned that future filings citing non-existent authority may be sanctioned. A company officer, not an outside lawyer, represented the protester (`no_lawyer`). The decision says it was issued under GAO's procedures for protests using classified information and was later approved for public release, which likely explains the 162-day delay. The procurement was a Navy security and general services contract with evaluated costs of about $166 million and $185 million. |
| [B-424585.2](https://www.gao.gov/products/b-424585.2) (Sawdey Solution Services, Inc.; decided 22 Oct 2026) | `cite_only` | **Discusses AI-attributed citations: no.** The only matched phrase is "an alleged regulatory requirement that does not exist", about the protester's reading of the regulations. This is the false positive that the `cite_only` reading list exists to catch. |

### What w01 already shows (descriptive only)

- One `ai_citation` decision out of 19 parsed (5%). B1 is not testable until at least 40 decisions
  have been parsed.
- **Release lag matters for anyone counting these decisions by month.** A decision issued in May
  2026 first reached GAO's feed in late October 2026. Any count by decision date, including the
  database counts in [`../procurement-ai.md`](../procurement-ai.md), can therefore keep growing for
  past months. The census records both dates for every row, so the size of this effect will be
  reported at grading.

## Next wave

w02 runs about 7-12 days after w01's feed fetch, so that its feed overlaps w01's newest item
(2026-11-06). It uses the same census.py and this ledger.
