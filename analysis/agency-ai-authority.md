# Which authority do federal agency tribunals cite when they meet AI-fabricated citations? Result of census 1.0.0

Status: **graded on 10 November 2026** against the plan frozen in commit `4dde970` ([PLAN](agency-ai-authority/PLAN.md), [code](agency-ai-authority/census.py)). The job confirmed that its `census.py` was byte-identical to the committed one (SHA-256 `0173ccc7...`) before it downloaded anything. Made with AI agents working in MV2's name (MV2, Munim, Inc., mv2@munimtech.com). This is information about public decisions, not legal advice.

## Short answer

**The question cannot be answered from the main public tracker yet.** On 10 November 2026 the AI Hallucination Cases Database (Damien Charlotin, CC BY 4.0) listed 2,289 cases. Under the frozen filter, only **8** were from US federal agency tribunals or the Tax Court: 3 agency rows and 5 Tax Court rows. It had **no** decisions from the immigration courts or the Board of Immigration Appeals, the MSPB, the NLRB, the Board of Veterans' Appeals, the SEC or the Department of Labor's judges. Seven of the eight predictions were therefore **not testable**. The eighth, a method check, **held**.

Reading the few decisions that are there found something the counts could not show. In an October 2026 FLRA decision on AI-fabricated citations, the Authority cites **no rule of its own**. Instead it borrows from four other bodies: the NLRB, GAO, the Department of Education and the USPTO. That fits MV2's [CFR census](cfr-ai-census.md), which found that no agency's rules of practice mention AI.

## Graded predictions (verdicts as frozen)

| | prediction | verdict | data |
|---|---|---|---|
| Q1 | under 25% of agency decisions cite a named AI instrument | not testable (n = 3, needs 10) | 1 of 3 |
| Q2 | at least 40% cite the forum's own signature, sanctions or conduct rule | not testable (n = 3) | 1 of 3 |
| Q3 | forum rule cited more often than Fed. R. Civ. P. 11 | not testable (n = 3) | 1 vs 1 |
| Q4 | at least 50% of USPTO decisions cite 37 CFR 11.18 | not testable (n = 1, needs 5) | 1 of 1 |
| Q5 | under 50% of USPTO decisions since 11 Apr 2024 cite the USPTO AI guidance | not testable (n = 1) | 0 of 1 |
| Q6 | under 50% of Tax Court decisions cite 26 U.S.C. 6673 | not testable (n = 4, needs 5) | 0 of 4 |
| Q7 | method check: AI-instrument patterns match at most 1 decision before 11 Apr 2024 | **held** | 0 decisions before that date |
| Q8 | Mata v. Avianca cited in at least 15% of all readable decisions | not testable (n = 7, needs 10) | 0 of 7 |

Of the 8 rows, 7 had a readable document. The Tax Court row without one had no linked document. Full outputs are in [results/](agency-ai-authority/results/): `results.md`, `results.json`, `rows.csv` (case ids, forum, date, party type and flags, with no names and no text), `court_values.json` (every Court value matched, excluded or near-missed, so anyone can audit the filter), `source.json` and `status.json`.

## What reading every matched passage showed (corrections; the verdicts stay as graded)

As the plan required, the agents read every matched excerpt and a sample of the decisions that matched no listed authority.

- **Row 1656 is not an agency decision.** Its Court value says "Copyright Claims Board", but the linked document is a federal district court opinion in a suit against the Board. Its `frcp_11` and `inherent` matches quote the plaintiff's own requests for sanctions. **Corrected agency n: 2, not 3.**
- **Row 2832, FLRA, 74 FLRA No. 87 (21 Oct 2026)** ([decision](https://www.flra.gov/system/files/decisions/v74_87.pdf)). The Authority found that 35 of 42 legal or record citations in a federal agency's exceptions brief were fictitious, erroneous or irrelevant. It said the agency may have used a generative AI tool, cautioned parties to verify AI output and imposed no sanction. The `ai_instrument` match is real: footnote 55 cites the USPTO's 2024 AI guidance (89 Fed. Reg. 25609) "see, e.g.". The other footnotes cite *American Backflow & Fire Prevention, Inc.*, 375 NLRB No. 31 (2026), GAO's *Raven Investigations & Security Consulting*, B-423447 (May 2025), and the Department of Education's common grant instructions (89 Fed. Reg. 104528, Dec. 2024). **No FLRA regulation is cited.** The decision's only rule-based instruction is that filings must "satisfy all regulatory requirements".
- **Row 2625, USPTO, OED final order (27 July 2026):** a public reprimand by consent. AI tools had produced citations to the patent record that were wrong or did not exist, in a claim-construction chart filed in federal district court. The order rests on the USPTO Rules of Professional Conduct (37 CFR 11.101, 11.103, 11.804(c) and (d)). It then tells all practitioners which of those rules apply to AI use, with 37 CFR 11.18 described as "substantially parallel" to Rule 11. These matches are real. The order **does not cite the USPTO's 2024 AI guidance** by name or by Federal Register citation, even though its practitioner note covers the same ground. The conduct took place in a district court, not before the Office.
- **Tax Court.** In row 355 (*Thomas*, Oct 2024) the Court rested on Tax Court Rule 33(b). In row 1209 (*Clinco*, T.C. Memo. 2026-16) the Court quotes Rule 11 only to say the Tax Court "doesn't have an equivalent apart from Rule 33(b)", then relies on Rule 201(a) and Model Rule 3.3. The `frcp_11` match is a contrast, not reliance. Row 2668 (*Moore*, T.C. Memo. 2026-85) is one of the two "no listed authority" decisions. It notes AI-related citation errors in a self-represented party's brief, reminds the party that each party is responsible for the accuracy of what it files, and cites only *Clinco*. Row 1703, the other one, is a trial transcript in which an expert witness is questioned about using AI tools, not a ruling. No Tax Court document cites 26 U.S.C. 6673.
- **No false matches** for `uspto_11_18`, `model_rules` or the forum-rule patterns.

## What the database does not have

- **NLRB:** *American Backflow & Fire Prevention, Inc.*, 375 NLRB No. 31 (25 Aug 2026; [Board decision on nlrb.gov](https://apps.nlrb.gov/link/document.aspx/09031d4584344933)) is not in the CSV. Press and secondary summaries report that it found "ghost citations" in a non-attorney representative's exceptions brief and referred the representative to the Board's Investigating Officer. They say the referral was under 29 CFR 102.177, the Board's own misconduct rule. The agents did not extract the decision's text, so that section number is reported, not verified. The FLRA and the Massachusetts Commonwealth Employment Relations Board have since cited the decision.
- **EOIR:** no immigration court or BIA decision is in the CSV, even though EOIR issued Policy Memorandum 25-40 on generative AI in August 2025.
- **MSPB:** the two MSPB-related rows are Federal Circuit decisions reviewing Board appeals. The frozen filter correctly treats them as review courts.

## What this means

1. A count of agency tribunals built on the main tracker would measure the tracker's coverage, not the agencies. Agency decisions sit in each agency's own reading room (flra.gov, nlrb.gov, the USPTO FOIA reading room, justice.gov/eoir), and the tracker seldom reaches them.
2. Where agency decisions are found, the tribunals do not cite an AI rule of their own, because none has one. The FLRA borrowed from four other bodies. The USPTO's own disciplinary order cited its general conduct rules rather than its own AI guidance. The Tax Court relied on its pleading rule and the Model Rules, then on its own precedent.
3. The next step is a census built from an agency's own archive, pre-registered before any decision is read. It is now pre-registered for the FLRA, the first agency checked whose full archive can be read politely by code: [FLRA archive census](flra-ai-citations/PLAN.md). The NLRB's decision files sit under a path its robots.txt disallows, and the MSPB's list is built by JavaScript. This study stays as graded.

## Limits

There are very few rows. The sections after the graded table describe individual decisions, not rates. Q7 held only because no readable decision in scope is dated before 11 April 2024, so this run never actually tested the pattern. The tracker grows every day. Rows were classified by their free-text Court value, and one row's value was wrong (row 1656). Regular expressions can miss unusual citation forms. This counts citations. It does not judge whether any tribunal applied any rule correctly, and it is not legal advice.

Data: AI Hallucination Cases Database, Damien Charlotin, CC BY 4.0, CSV SHA-256 `bcd49cf6e3cb05f4ade4ac51aabcebe9a6aa731fc0a61bfa0291329aa2f92d20`, fetched 2026-11-10T06:15:25Z. Text of this write-up: CC BY 4.0. Code: Apache-2.0.
