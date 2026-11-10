# What the binding federal regulations say about AI: a census of AI terms in the in-force CFR (census 1.0.1, done)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
Text CC BY 4.0, code Apache-2.0. Information about public regulations, not legal advice.

Plan: [cfr-ai-census/PLAN.md](cfr-ai-census/PLAN.md), frozen in commit 4d1ac4f before the full download,
with Amendment 1 (commit 2ec6fd8) moving two dates the eCFR does not serve. Run: sealed job cfrai-v2,
2026-11-09 22:03-22:07 UTC, census.py byte-identical to the committed copy (SHA-256 0804fb2d...).
Every query returned its full `total_count`; no date-filter anomalies. All outputs:
[cfr-ai-census/results/](cfr-ai-census/results/).

## Answer in one paragraph

On 5 November 2026 (the date the eCFR was up to date as of), **31 provisions** of the Code of Federal
Regulations used "artificial intelligence", "machine learning", "neural network" or "chatbot", up from 8
on 3 January 2017. The machine count is 32; one of them (the FTC's "Click to Cancel" section, 16 CFR
425.6) was removed on 12 February 2026 but is still served as current by the eCFR search API (see the
data-quality finding below). Read by hand, 2 of the 31 match only a name (an Entity List entry and the
DoD Chief Digital and Artificial Intelligence Office) and 5 use the words only inside a worked example,
which leaves **24 provisions whose operative text says something about AI**. They are export controls
(7), FDA medical-device classifications (6, all from June to November 2026), EPA air rules (7, most about
"neural network" boiler optimisation since 2012), and one each for ICT supply-chain review, outbound
investment, the Medicare Diabetes Prevention Program and a Sea Grant research-priority list. **No
agency's rules of practice or procedure use any of the terms** (the one expectation the plan stated, and
it held), and **"generative AI", "generative artificial intelligence", "large language model", "deep
learning" and "natural language processing" appear nowhere in the in-force CFR.** By contrast, four state
supreme courts changed their own practice rules for AI-generated filings in 2026 (New York Part 161,
Florida Rule 2.515, Connecticut Practice Book 4-9, Indiana Trial Rule 11; see
[state-ai-rule-citations.md](state-ai-rule-citations.md)).

## Counts over time (machine count from the job; corrected count beside it)

| date | machine count | corrected (16 CFR 425.6 removed 2026-02-12) |
|---|---|---|
| 2017-01-03 | 8 | 8 |
| 2018-01-01 | 8 | 8 |
| 2019-01-01 | 8 | 8 |
| 2020-01-01 | 10 | 10 |
| 2021-01-01 | 11 | 11 |
| 2022-01-01 | 12 | 12 |
| 2023-01-01 | 12 | 12 |
| 2024-01-01 | 13 | 13 |
| 2025-01-01 | 13 | 13 |
| 2026-01-01 | 25 | 25 |
| 2026-07-01 | 29 | **28** |
| 2026-11-05 | 32 | **31** |

Of the 31, 18 first took effect in 2025 or later (machine count 19). The jump in 2025 is the January 2025
export-control rules on AI model weights and chips (BIS), the Treasury outbound-investment rule and the
Justice Department's bulk sensitive-data rule; the 2026 growth is almost all FDA device classifications
that now write "machine learning" into the regulation itself.

## Every provision in force on the census date, read by hand

Read from the passage the eCFR search returned for each provision; the DOJ and IRS examples were also
checked on the full current section text (eCFR renderer API, 2026-11-10). "Operative" means the words are
part of a requirement, definition, scope or list that has legal effect; "example" means they appear only
inside a numbered illustration; "name" means they are part of a proper name.

| provision | what the words do | reading |
|---|---|---|
| 15 CFR 774 Supp. 1 (Commerce Control List) | ECCN 4E091: model weights of AI models trained above a compute threshold | operative |
| 15 CFR 774 Supp. 5 | software "specially designed" to train a deep convolutional neural network for geospatial imagery (0D521) | operative |
| 15 CFR 740.27 | License Exception Artificial Intelligence Authorization (AIA) | operative |
| 15 CFR 740 Supp. 5 | list of AI Authorization countries | operative |
| 15 CFR 742.6 | regional-stability licence requirement for AI model weights | operative |
| 15 CFR 748.3 | classification requests for AI models | operative |
| 15 CFR 748 Supp. 2 | purchase orders and licence applications for "Artificial Intelligence commodities" | operative |
| 15 CFR 744 Supp. 4 (Entity List) | entity names (Beijing Academy of Artificial Intelligence; Quanzhou Integrated Circuit and Artificial Intelligence Research Institute) | **name: false match** |
| 15 CFR 791.3 | ICTS transactions integral to AI and machine learning are in scope | operative |
| 15 CFR 917.21 | Sea Grant national needs: AI techniques for undersea vehicles | operative (research-priority list) |
| 21 CFR 864.3900, 868.2200, 868.2250, 868.2378, 870.2380, 892.2055 | FDA device classifications: identification of ML/AI devices or special controls for ML-based algorithms (clinical validation, change-control plans) | operative (6) |
| 26 CFR 1.224-1 | "Qualified tips": a digital content creator's videos on AI image prompts | example (Example 11) |
| 28 CFR 202.214, 202.217, 202.301, 202.304 | bulk sensitive-data rule: AI chatbot, AI personal assistant, AI algorithm, AI development | example (Examples 6, 4, 1, 5) |
| 31 CFR 850.210 | outbound investment: pooled funds in AI sectors | operative |
| 40 CFR 63.10005, 63.10006, 63.10021, 63.10042, Table 3 to Subpart UUUUU | Mercury and Air Toxics Standards: tune-up every 48 instead of 36 months if a coal unit uses neural-network combustion optimisation; definition of neural network | operative (5) |
| 40 CFR 60.5398b | oil and gas methane rule: an alternative leak-detection technology must describe its algorithms/machine-learning procedures | operative |
| 40 CFR 73 Subpart F App. A | acid-rain allowances: "control improvements, including artificial intelligence and expert systems" as a qualified energy-conservation measure | operative (list) |
| 42 CFR 410.79 | Medicare Diabetes Prevention Program: online sessions need a live coach, "including non-artificial intelligence (AI)" | operative |
| 48 CFR 202.101 (DFARS definitions) | "Chief Digital and Artificial Intelligence Office" in the list of defence agencies | **name: false match** |

Not in force on the census date (in the 35 ever matched): 15 CFR 7.3 (moved to 791.3 in 2024), 40 CFR
60.5740a and 60.5805a (the Affordable Clean Energy rule's sootblower and neural-network provisions), and
16 CFR 425.6 (below).

**Rules of practice.** None of the 35 sits under a heading the plan treats as rules of practice or
procedure. The part headings seen were: National Emission Standards for Hazardous Air Pollutants; Standards
of Performance for New Stationary Sources; Sulfur Dioxide Allowance System; National Sea Grant Program
Funding Regulations; The Commerce Control List; License Exceptions; Control Policy (CCL-based and
end-user/end-use based); Applications and Documentation; Securing the ICTS Supply Chain; Definitions of
Words and Terms; Supplementary Medical Insurance Benefits; U.S. Investments in Certain National Security
Technologies; Recurring Subscriptions and Other Negative Option Programs; Access to U.S. Sensitive
Personal Data; Income Taxes; and five FDA device parts. Nothing in the in-force CFR found by these terms
says how a party may or may not use AI in a filing, hearing or submission to a federal agency.

## Data-quality finding: the eCFR search API serves a removed section as current

For the dated queries at 2026-07-01 and 2026-11-05, `https://www.ecfr.gov/api/search/v1/results`
returned 16 CFR 425.6 ("Simple cancellation ('Click to Cancel')") in its 2025-01-14 version with
`ends_on: null` and `removed: false`. The eCFR's own versioner
(`/api/versioner/v1/versions/title-16.json?part=425`) lists a second entry for 425.6 dated 2026-02-12
with `removed: true`, and the current rendered Part 425 holds only 425.1 and 425.2 (source note
91 FR 6509, 12 February 2026). The FTC's 2024 amendments had been vacated by the Eighth Circuit on
8 July 2025 (*Custom Communications, Inc. v. FTC*) and the FTC restored the earlier rule text in that
February 2026 notice. A census or tool that trusts the search API's dates would still count the vacated
"Click to Cancel" section as law.

We then checked every one of the 32 provisions the job counted as in force against the versioner on
2026-11-10: 425.6 is the only one whose latest entry is `removed: true`. We also saw that the search index
leaves superseded versions open: for 40 CFR 63.10021 it returns versions starting 2024-07-08 and
2026-04-27, both with `ends_on: null`, although a 2026-02-24 version sits between them. That does not
change a provision-level count (the section is in force either way) but would inflate any count of
versions. We searched for an earlier report of this behaviour and found none; one third-party guide notes
only that an undated search returns old versions, which is expected. Advice for anyone using the API:
pass `date=`, then confirm each hit's latest `removed` flag in the versioner before counting it. We are
reporting the discrepancy to the eCFR team (ecfr@nara.gov).

## Limits

- Exact phrases only. A provision that says only "AI", "automated decision system", "algorithm" or
  "autonomous" is not counted, so these are floor counts.
- The eCFR is an editorial compilation, not the official legal edition, and it shows a vacated rule until
  the agency removes it (425.6 stayed in it from the July 2025 vacatur to February 2026). Point-in-time
  versions start on 3 January 2017.
- Rules of practice are found by heading. Practice rules under a differently named part would be missed;
  the headings seen are listed above.
- Guidance, policy statements, OMB memoranda, Federal Register preambles and agency orders are not in the
  CFR and are out of scope. So are court rules (federal local rules and standing orders) and state law.
- The corrected counts rest on one post-hoc check (the versioner) that the plan did not name; the machine
  counts are published unchanged beside them.
- Hand reading was done by AI agents working in MV2's name; no lawyer reviewed it.

## Why this is new

We searched for a published count of AI terms in the text of the in-force CFR and found none. Existing
counts (for example the Stanford AI Index's federal tallies) count new Federal Register documents per
year, not the text in force on a date. This census is dated, provision-level and reproducible from public
APIs, and it also documents a defect in the eCFR search index that affects anyone who counts regulations
with it.

## Reproduce

`python -m unittest -v` then `python run_job.py --out-dir out` in `cfr-ai-census/` (Python 3.12, standard
library only, network to www.ecfr.gov, 2 s between requests). Outputs: `results.md`, `results.json`,
`provisions.csv`, `timeline.csv`, `queries.json`, `anomalies.json`, `status.json`, `raw_results.json`.
