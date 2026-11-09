# Do state-court decisions on AI-fabricated citations cite the new 2026 state AI rules? (census 1.0.0, graded)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; graded by a
sealed job on 9 November 2026 against the plan frozen in commit 61ffda7 before any decision text
was read. Text CC BY 4.0, code Apache-2.0. Information about public court decisions, not legal
advice. No human has checked these counts yet.

Plan, code and tests: [`state-ai-rule-citations/`](state-ai-rule-citations/) (PLAN.md,
census.py, run_job.py, test_census.py). Results: `results.md`, `results.json`, `rows.csv`
(case ids, court, date, party type and match flags; no case names, no text), `source.json` and
`court_values.json` in [`state-ai-rule-citations/results/`](state-ai-rule-citations/results/).

## The question

In 2026 four states put a duty to check citations, with AI named as the reason, into binding
court rules: New York's 22 NYCRR Part 161 (in force 1 June 2026), Florida's amended Rule 2.515
(15 June), Connecticut's Practice Book Section 4-9 (23 June) and Indiana's amended Trial Rule 11
with new Rules 11.1 and 11.2 (1 August). When a state court in one of these states now rules on
fabricated or garbled authority, does the decision cite the new rule?

## Data

Rows: Damien Charlotin's AI Hallucination Cases Database (CC BY 4.0), full CSV fetched by the job
on 2026-11-09 at 15:25 UTC (SHA-256 `bcd49cf6...`, in `source.json`). In scope: state-court rows
in the four states dated 1 November 2025 to 8 November 2026, 87 rows. The job fetched the
decision document each row links, 5 seconds apart: 85 had a document, 84 were readable
(at least 1,500 characters of text). 32 readable decisions fall after their state's effective
date (post period) and 52 before it (pre period, from 1 November 2025).

## Result

| state | new rule | in force | post: cite / readable | pre: cite / readable |
|---|---|---|---|---|
| New York | 22 NYCRR Part 161 | 2026-06-01 | **0 / 15** | 0 / 25 |
| Florida | Rule 2.515 | 2026-06-15 | **8 / 11** | 2 / 13 |
| Connecticut | Practice Book § 4-9 | 2026-06-23 | **2 / 2** | 0 / 2 |
| Indiana | Trial Rule 11 (11.1, 11.2) | 2026-08-01 | **1 / 4** | 1 / 12 |
| all four | | | **11 / 32 (34%)** | 3 / 52 |

New York's 15 post-period decisions cite Part 130 (the older rule on frivolous conduct and
signatures) 9 times and Part 161 not once. Florida's appellate courts cite Rule 2.515 in most
decisions since the amendment. Connecticut's two decisions both cite Section 4-9, and the first
of them, on 31 July 2026, also cites the appellate rules amended on 14 July (Section 85-2 or 62-6).

## Pre-registered predictions

| | prediction | verdict | numbers |
|---|---|---|---|
| H1 | fewer than half of post-period decisions, pooled, cite the new rule | **held** | 11 of 32 (34%) |
| H2 | in New York, more post-period decisions cite Part 130 than Part 161 | **held** | 9 vs 0 of 15 |
| H3 | Florida: the share citing 2.515 is higher after the amendment | **held** | 8/11 (73%) vs 2/13 (15%) |
| H4 | Indiana: the same for Trial Rule 11 | **held** | 1/4 (25%) vs 1/12 (8%) |
| H5 | post period: lawyer cases cite the rule more often than self-represented cases | **failed** | lawyer 5/16 (31%), self-represented 6/16 (38%) |
| H6 | method check: at most 1 New York or Connecticut decision before 25 March 2026 matches | **held** | 0 of 15 |

Five of six held. H5 failed: courts cited the new rules slightly more often when the filer was
self-represented, though with 16 decisions in each group the difference is one or two decisions.

## Reading every match (false-match check)

As the plan requires, the agents read the text around all 14 matches of the new-rule patterns
(11 post period, 3 pre period). All 14 are real citations of the rule in question; there is no
false match, so the corrected counts equal the graded ones. Points worth knowing from that
reading:

- The two Florida pre-period matches are real too: one decision (March 2026) cites 2.515 through
  the appellate rule that requires filings to be signed under it, and one (May 2026) cites
  2.515(d)(2) a month before the amendment took effect.
- One Florida decision (October 2026) records a party's argument that the amended rule cannot be
  applied to a brief filed before it took effect; another cites the Florida Supreme Court's
  amending opinion for the notice-and-hearing step it added before sanctions.
- The Indiana post-period match is a decision whose text says that a filer's apparent use of
  ChatGPT or another AI tool to prepare motions violated Trial Rule 11(A).

## How to read the New York zero

Part 161 is not a stand-alone sanctions rule. The New York State Bar Association's notice of the
rule (the source in this repository's index, entry `ny-ucs-part-161`) says it rests on
22 NYCRR 130-1.1 and Rule 3.3, and its model signature rule sits in an appendix that each court
may choose to adopt. A New York court that sanctions under Part 130 is therefore using the older
tool that Part 161 itself points to. The finding is narrower than "New York courts ignore the AI
rule": in the 15 readable decisions of this database since 1 June 2026, none names Part 161,
and the sanction route visible in the text is Part 130.

## Limits

- The database is a growing collection that contributors add to, not a census of court
  decisions, and some courts are covered better than others. Connecticut (2) and Indiana (4)
  have very few post-period decisions.
- A decision dated after a rule took effect may concern filings made before it, and a court may
  apply a rule without citing it by number.
- Citations are found by regular expressions frozen before any text was read; an unusual
  citation form would be missed (H6 and the reading above found no false match).
- One linked document was unreadable and two rows had no document; they are counted, not graded.
- This counts citations. It does not judge whether any court applied any rule correctly.

## Reproduce

Run `run_job.py` from `state-ai-rule-citations/` with Python 3.12 and pypdf 5.1.0. The database is
updated continuously, so a later download gives different rows; `source.json` records the exact
file used, and `rows.csv` keeps each decision's case id and document hash.

Data credit: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0.
