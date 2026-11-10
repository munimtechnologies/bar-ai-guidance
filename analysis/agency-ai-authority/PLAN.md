# Pre-registration: which authority do federal agency tribunals cite when they meet AI-fabricated citations? (census 1.0.0)

Status: **frozen before any data row is read.** Written 2026-11-10 by AI agents working in MV2's
name (MV2, Munim, Inc., mv2@munimtech.com). Code: `census.py` in this folder (standard library
only, Apache-2.0), tests in `test_census.py`, job wrapper `run_job.py` (uses pypdf 5.1.0 to
extract text). The job checks that this PLAN and `census.py` are public in this repository and
that its local `census.py` is identical to the newest committed one before it downloads
anything. Information about public decisions, not legal advice.

## Question

MV2's census of AI terms in the Code of Federal Regulations ([result](../cfr-ai-census.md))
found that, as of 5 November 2026, no agency rules of practice or procedure mention artificial
intelligence. Yet agency tribunals do meet briefs with invented cases. When they rule on one,
what do they rest the ruling on?

- the forum's own general signature, sanctions or practitioner-conduct regulation (for example
  37 CFR 11.18 at the USPTO, 8 CFR 1003.102 at EOIR, 5 CFR 1201.43 at the MSPB);
- one of the two named AI instruments that exist outside the CFR: the USPTO's *Guidance on Use
  of Artificial Intelligence-Based Tools in Practice Before the USPTO* (11 April 2024, 89 FR
  25609) and EOIR Policy Memorandum 25-40, *Use of Generative Artificial Intelligence in EOIR
  Proceedings* (8 August 2025);
- Federal Rule of Civil Procedure 11 by analogy, inherent authority, the ABA Model Rules, or
  18 U.S.C. 1001;
- or nothing named at all.

The United States Tax Court and the Court of Appeals for Veterans Claims are Article I courts
that hear agency-type cases. They are counted as a separate stratum, never pooled with the
agencies in Q1-Q3.

## Prior art (searched 2026-11-10)

- USPTO's own TTAB slides (Trademarks Hour, January 2026) list where TTAB sanctions can come
  from: 37 CFR 11.18(c), 18 U.S.C. 1001, Fed. R. Civ. P. 11 or inherent authority, and cite
  Hamlett v. Bronx Native (Cancellation No. 92077944, 7 Feb 2024). IPWatchdog (28 Aug 2026)
  reports the first USPTO discipline order over AI-invented citations to the record.
- Reporting on Tax Court decisions (Tax Notes; Journal of Accountancy, Sept 2026) describes
  Clinco v. Commissioner, T.C. Memo. 2026-16, resting on Tax Court Rule 201(a) and the Model
  Rules rather than section 6673, and Moore, T.C. Memo. 2026-85.
- Reporting on EOIR PM 25-40 (legalaigovernance.com, practitioners' posts) says it imposes no
  disclosure or verification duty beyond existing rules and points to the attorney discipline
  rules.
- Trackers (the AI Hallucination Cases Database, legalaigovernance.com, HAQQ, GC AI) count
  cases. MV2's procurement study counted GAO and board decisions. We found **no count of which
  authority agency tribunals cite**, for any agency.

## Data

- **Rows:** the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0), full CSV export,
  downloaded by the job after this PLAN is public. SHA-256, size and time are recorded.
- **Texts:** the decision document each row links (`Source`, or `Pointer` if that is a URL),
  fetched one at a time, 5 seconds apart, as `MV2-Munim-research/1.0 (mv2@munimtech.com)`.
  Nothing here trains a model.
- Texts, excerpts, case names and the raw CSV stay private to the job. The published table has
  case ids (look a case up in the database), forum, Court value, date, party type and the flags.

**What was seen before freezing, stated plainly.** MV2's earlier studies processed the same
database's CSV by code (sanctions, procurement tribunals, state rule citations). Their published
outputs contain no agency-tribunal rows, and no agency-tribunal row, Court value, count or
decision text was looked at for this plan. The prior-art reading above named five decisions
(Hamlett, the OED order, Clinco, Moore, and Thomas, a 2024 Tax Court order); their outcomes as
reported shaped Q4 and Q6. The thresholds for "not testable" were set without knowing how many
rows exist.

## Definitions (as coded in census.py)

- **In scope:** `State(s)` contains USA; the decision date, if any, is on or before 2026-11-09.
  Forum from the free-text `Court` value, in this order: Article I courts (Court of Appeals for
  Veterans Claims; the United States Tax Court, but not a state tax court); then rows naming GAO
  or a board of contract appeals are excluded (MV2's procurement study covers them); then the
  agencies: USPTO (TTAB, PTAB, OED), EOIR (BIA, immigration courts), MSPB, Board of Veterans'
  Appeals, NLRB, SEC, Department of Labor adjudicators, and a named list of other federal
  adjudicators (OTHER_FED). A value that also names a reviewing court (district court, circuit,
  court of appeals, Supreme Court, bankruptcy, Court of Federal Claims) is excluded as a review
  court. SEC, DOL and OTHER_FED values that name a US state are excluded as state agencies.
  Undated rows are kept but left out of the date-based Q5 and Q7.
- **Readable:** the document was fetched and its extracted text has at least 1,500 characters
  after whitespace is collapsed. Unreadable, missing and failed documents are counted and
  reported, never graded.
- **Flags** (regular expressions on the text, exactly as in census.py):
  - `ai_instrument`: the USPTO 2024 AI guidance (89 FR 25609 or its title) or EOIR PM 25-40
    (number or title);
  - `forum_rule`: the forum's own provisions: USPTO 37 CFR 11.18, 2.193, 42.11, 42.12, 41.128,
    11.101, 11.303, 11.804; EOIR 8 CFR 1003.101-1003.109, 1292.3, 1003.1(d)(2); MSPB 1201.43;
    BVA 38 CFR 14.632-14.633; NLRB 102.177; SEC 201.180 or 201.102; DOL 29 CFR 18.12, 18.35,
    18.57; Tax Court Rule 33(b), Rule 201(a) or 26 U.S.C. 6673; CAVC Rule 38 or 46; OTHER_FED none;
  - `uspto_11_18` (USPTO only), `tax_6673` (Tax Court only);
  - `frcp_11`, `inherent` (inherent authority or power), `model_rules`, `usc_1001`, `mata`
    (Mata v. Avianca), `ai_words`.
- **Party:** `Party(ies)` contains `Lawyer`, else `Pro Se`, else other.

## Predictions (fixed now)

- **Q1:** fewer than 25% of readable agency decisions cite a named AI instrument. Not testable
  below 10.
- **Q2:** at least 40% of readable agency decisions cite their forum's own signature, sanctions
  or conduct provision. Not testable below 10.
- **Q3:** more readable agency decisions cite the forum's own provision than cite Fed. R. Civ. P.
  11. Not testable below 10.
- **Q4:** at least 50% of readable USPTO decisions cite 37 CFR 11.18. Not testable below 5.
- **Q5:** fewer than 50% of readable USPTO decisions dated on or after 11 April 2024 cite the
  USPTO AI guidance. Not testable below 5.
- **Q6:** fewer than 50% of readable Tax Court decisions cite 26 U.S.C. 6673. Not testable
  below 5.
- **Q7 (method check):** the AI-instrument patterns match at most 1 readable decision dated
  before 11 April 2024, when neither instrument existed. More would mean the patterns catch
  something else.
- **Q8:** Mata v. Avianca is cited in at least 15% of all readable decisions (both strata).
  Not testable below 10.

Each prediction is reported as held, failed or not testable, every one of them, either way.
Grading uses the regular expressions exactly as frozen. After grading, the agents will read
every matched excerpt and report any false match separately, with a corrected count beside the
graded one; the verdicts stay as graded. A sample of decisions with no listed authority will be
read and described (what, if anything, they rest on), without changing any verdict.

## Outputs

`results.json`, `results.md`, `rows.csv` (no case names, no text), `source.json` and
`court_values.json` (every Court value matched, excluded or near-missed, and how it was
classified, so anyone can audit the filter).

## Limits

The database is a growing collection, not a census of agency decisions; agencies publish only
some decisions, and coverage depends on contributors. Some agencies may have very few rows, so
several predictions may be not testable. A decision may apply a rule without citing it by
number, or cite a rule only to quote a party. Text extraction can fail on scanned documents. A
regular expression can miss an unusual citation form or catch an unrelated one; Q7 and the
excerpt review are there to show how often. This counts citations. It does not judge whether
any tribunal applied any rule correctly, and it is not legal advice.
