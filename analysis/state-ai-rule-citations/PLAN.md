# Pre-registration: do state-court decisions on AI-fabricated citations cite the new state AI rules? (census 1.0.0)

Status: **frozen before any decision text is read.** Written 2026-11-09 by AI agents working in
MV2's name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard
library only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (uses pypdf 5.1.0
to extract text). The job checks that this PLAN and `census.py` are public in this repository and
that its local `census.py` is identical to the newest committed one before it downloads anything.
Information about public court decisions, not legal advice.

## Question

In 2026 four states adopted binding court rules that make whoever signs a filing answer for the
accuracy of its citations, with AI named as the reason. They are New York's 22 NYCRR Part 161
(in force 1 June 2026), Florida's amended Rule 2.515 (subdivision (d)(2)(D), 15 June 2026),
Connecticut's Practice Book Section 4-9 (23 June 2026) and Indiana's amended Trial Rule 11 with
new Rules 11.1 and 11.2 (1 August 2026). The dates come from the entries of `data/guidance.json`
(index 0.16.1). When a state court in these states now rules on fabricated or garbled
authority, does its decision cite the new rule? Or does it still rest on older tools: inherent
power, New York's Part 130, Florida's section 57.105, or the case law?

This matters to anyone tracking the rules. A rule nobody cites in its first months is a signal
about how courts actually respond, and the index's agent skill tells lawyers to read these rules
first.

## Prior art (searched 2026-11-09)

Law-firm posts and trackers (legalaigovernance.com, ctalf.com, Mondaq, Rev and others) describe
the rules. Some name single decisions: the Connecticut Supreme Court's TOV Realty v. Suarez order
(31 July 2026), and a Superior Court decision on a prompt injection in a pleading that commentators
report relied on inherent authority and on the certification in Sections 4-2 (b) and 4-9 (the
agents have not read either decision). We found no count of how often decisions cite these rules,
in any state.

## Data

- **Rows:** the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0), full CSV export,
  downloaded by the job after this PLAN is public. SHA-256, size and time are recorded.
- **Texts:** the decision document each row links (`Source`, or `Pointer` if that is a URL),
  fetched one at a time, 5 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`.
  The site's robots.txt allows this path for all agents not named in it; its content signal
  forbids AI training, and nothing here trains a model.
- Texts, excerpts, case names and the raw CSV stay private to the job. The published table has
  case ids (look a case up in the database), court, date, party type and the match flags.

**What was seen before freezing, stated plainly.** From the 2026-11-07 snapshot (SHA-256
`9201eecd...`, used by MV2's earlier studies), the agents listed the case id, name, Court value,
date and party type of the rows in these four states dated June to November 2026. That is about
31 state-court rows after the effective dates (New York 14, Florida 11, Connecticut 2, Indiana 4),
and lawyers and self-represented parties are about evenly split. They also searched the database's
own text fields for the rule numbers. Only one row's description names a rule: a Florida appellate
order to show cause citing rule 2.515(d)(2). No row's description names Part 161, a Practice Book
section or Trial Rule 11. These descriptions are the contributors' summaries, not the decisions.
No decision text had been opened when this plan was written. The thresholds for "not testable"
were set knowing these approximate counts.

## Definitions (as coded in census.py)

- **In scope:** `State(s)` contains USA; the `Court` value names exactly one of New York, Florida,
  Connecticut or Indiana and is not a federal court (it does not start with a district
  abbreviation such as "S.D." or "D.", and does not mention Bankruptcy, Circuit, "Cir", Federal,
  U.S., BIA or International Trade). The decision date is an ISO date.
- **Post period:** from the state's effective date to 2026-11-08. **Pre period:** 2025-11-01 to the
  day before the effective date.
- **Readable:** the document was fetched and its extracted text has at least 1,500 characters
  after whitespace is collapsed. Unreadable, missing and failed documents are counted and
  reported, never graded.
- **Cites the new rule** (primary measure, by regular expression on the text):
  New York `Part 161`, `NYCRR 161` or `§ 161.x`; Florida `2.515` (any subdivision);
  Connecticut `Practice Book § 4-9`, `Section 4-9`, `§ 4-9` or 4-9 within a `§§` list;
  Indiana `Trial Rule 11`, `11.1`, `11.2` or `T.R. 11`. Florida's 2.515 and Indiana's Trial Rule 11
  existed before the 2026 amendments, so for those two states the pre period gives the baseline.
- **Secondary flags** (reported, not graded except H2): New York Part 130 (`Part 130`,
  `130-1.1`); Florida `2.515(d)(2)` and section `57.105`; Connecticut Practice Book `85-2` or
  `62-6` (the appellate rules amended on 14 July 2026); Indiana `11.1` or `11.2`.
- **Party:** `Party(ies)` contains `Lawyer` (lawyer), else `Pro Se` (pro se), else other.

## Predictions (fixed now)

- **H1:** fewer than half of the readable post-period decisions, all four states pooled, cite the
  state's new rule. Not testable below 10 readable decisions.
- **H2:** among readable post-period New York decisions, more cite Part 130 than cite Part 161.
  Not testable below 8.
- **H3:** in Florida, the share of readable decisions citing 2.515 is higher in the post period
  than in the pre period. Not testable if either period has fewer than 4.
- **H4:** the same for Indiana and Trial Rule 11 (with 11.1 and 11.2). Not testable below 4 in
  either period.
- **H5:** in the post period, pooled, decisions with a lawyer party cite the new rule at a higher
  rate than decisions with a self-represented party. Not testable below 5 in either group.
- **H6 (method check):** at most 1 readable New York or Connecticut decision dated 2025-11-01 to
  2026-03-24 (before New York adopted Part 161 on 25 March 2026) matches the new-rule pattern.
  More would mean the patterns catch something else.

Each prediction is reported as held, failed or not testable, every one of them, either way.
Grading uses the regular expressions exactly as frozen. After grading, the agents will read every
matched excerpt and report any false match separately, with a corrected count beside the graded
one; the verdicts stay as graded.

## Outputs

`results.json`, `results.md`, `rows.csv` (no case names, no text), `source.json` and
`court_values.json` (every Court value seen for the four states and how it was classified, so
anyone can audit the filter).

## Limits

The database is a growing collection, not a census of court decisions, and it covers some courts
better than others; Connecticut and Indiana will have few rows. A decision dated after a rule took
effect may concern filings made before it, and a court may apply a rule without citing it by
number. Text extraction can fail on scanned documents. A regular expression can miss an unusual
citation form or catch an unrelated one; H6 and the excerpt review are there to show how often.
This counts citations. It does not judge whether any court applied any rule correctly, and it is
not legal advice.
