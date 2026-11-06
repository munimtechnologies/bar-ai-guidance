# Are US courts "ratcheting up" sanctions for AI-hallucinated filings? A pre-registered per-decision count

*By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
Information only, not legal advice. Text CC BY 4.0; code Apache-2.0.*

**Data:** AI Hallucination Cases Database, Damien Charlotin,
https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0). This study only re-counts his
database; any coding question belongs to the database, not to the courts.

Analysis 1.0.0, graded 2026-11-06. Pre-registration:
[`hallucination-sanctions/PREREG.md`](hallucination-sanctions/PREREG.md), committed in
65bd693 (2026-11-06 09:01 UTC) together with the frozen grader `analyze.py`. The job wrapper
(`run_job.py`) refused to download the data until that commit was public and the committed
`analyze.py` matched the one it ran (both SHA-256 `c74d51a3...083fd`). It then downloaded the CSV
once, at 2026-11-06 14:58:08 UTC (2,175,509 bytes, SHA-256 `9201eecd...ef297c87`). No
definition or line of code was changed after the pre-registration. Full outputs are in
[`hallucination-sanctions/results/`](hallucination-sanctions/results/).

## Short answer

In this database, a US decision involving a lawyer was **about half as likely to carry a
monetary penalty in the first half of 2026 as a year earlier (25% vs 47%)**. When money was
imposed, the amounts were **somewhat larger**: the median rose from $1,750 to $2,731, but that rise
is not statistically clear. The share of amounts of $10,000 or more went from 13% to 22%. The
share of lawyer decisions with a professional sanction (referral, suspension and the like) **did
not rise** (16% vs 15%). Seven in ten 2026H1 lawyer decisions carried neither money nor
discipline.

So the "ratchet" shows up in the size of the penalties that are imposed and in the total number
of penalties. It does not show up in how likely any one decision is to carry one. Total penalties
grow because the number of decisions grows: lawyer decisions with money went from 18 in 2025H1 to
60 in 2026H1, while the share fell.

## Predictions (fixed before any data row was read)

| | prediction | result | 2025H1 | 2026H1 | one-sided permutation p (rise) | verdict |
|---|---|---|---|---|---|---|
| P1 | Share of US lawyer decisions with a monetary penalty is **not** more than 5 points higher in 2026H1 | fell 22.5 points | 47.4% (18/38) | 24.9% (60/241) | 0.999 | **held** |
| P2 | Median USD amount in lawyer decisions is higher in 2026H1 | rose $981 | $1,750 (16 amounts) | $2,731 (58 amounts) | 0.124 | **held** |
| P3 | Share of lawyer decisions with a professional sanction is higher in 2026H1 | fell 0.9 points | 15.8% (6/38) | 14.9% (36/241) | 0.660 | **failed** |
| P4 | In 2025H1, 2025H2 and 2026H1, pro se decisions carry a monetary penalty less often than lawyer decisions | lower in all three | see table | | | **held** |
| P5 | Fewer than half of 2026H1 lawyer decisions carry money or a professional sanction | 31.1% (75/241) | | | | **held** |

Verdicts follow the pre-stated direction or threshold, not the p-values (as pre-registered).
P2 held on direction, but its p-value (0.12) means the rise could well be chance; read it as
"no sign of a fall", not as proof of a rise. 95% Wilson intervals for the P1 shares:
2025H1 32.5-62.7%, 2026H1 19.9-30.7%, so they do not overlap.

## Sensitivity analyses (reported, not graded)

| analysis | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| S1: drop rows flagged "Alleged" | held | held | failed | held | held |
| S2: any party label containing "lawyer" | held | held | failed | held | held |
| S3: count a penalty only if its amount is above 1 | held (42.1% vs 24.1%) | held | failed | held | held |
| S4: calendar 2025 vs 2026 to date | held (39.4% vs 23.7%) | held ($2,500 vs $3,500) | failed (28.4% vs 14.9%) | held | held (29.6%) |

S1 and S2 give the same numbers as the primary analysis because no row they change falls in the
compared periods: the 9 US rows flagged "Alleged" are all dated 2025H2 or 2026H2, and the two US
"Governement Lawyer" rows (spelled so in the database) are dated July 2026. We report this so the
identical rows are not mistaken for a bug.

## Half-year tables (US decisions)

**Involving a lawyer**

| period | n | share with money | USD amounts | median USD | p75 USD | max USD | amounts >= $10k | professional sanction |
|---|---|---|---|---|---|---|---|---|
| 2023H1 | 1 | 1.000 | 1 | 5,000 | - | 5,000 | 0 | 0 |
| 2023H2 | 3 | 0 | 0 | - | - | - | - | 0.333 |
| 2024H1 | 6 | 0.167 | 1 | 2,000 | - | 2,000 | 0 | 0.333 |
| 2024H2 | 8 | 0.125 | 1 | 2,000 | - | 2,000 | 0 | 0 |
| 2025H1 | 38 | 0.474 | 16 | 1,750 | 4,221 | 31,100 | 0.125 | 0.158 |
| 2025H2 | 170 | 0.377 | 57 | 4,030 | 7,472 | 85,567 | 0.175 | 0.312 |
| 2026H1 | 241 | 0.249 | 58 | 2,731 | 7,875 | 110,204 | 0.224 | 0.149 |
| 2026H2 (to 6 Nov, still being collected) | 134 | 0.216 | 27 | 4,000 | 10,000 | 46,511 | 0.296 | 0.149 |

**Involving a pro se litigant**

| period | n | share with money | USD amounts | median USD | max USD | professional sanction |
|---|---|---|---|---|---|---|
| 2025H1 | 58 | 0.017 | 1 | 921 | 921 | 0 |
| 2025H2 | 253 | 0.063 | 12 | 3,000 | 66,129 | 0 |
| 2026H1 | 381 | 0.068 | 21 | 500 | 11,799 | 0 |
| 2026H2 (partial) | 192 | 0.088 | 9 | 1,000 | 23,222 | 0.005 |

Counts: 2,267 rows read (none malformed); 1,536 US (1 with no date); 602 US involving a lawyer;
913 involving a pro se litigant. A decision can involve both.

## Not pre-registered (exploratory, read with care)

- The professional-sanction share for lawyer decisions peaked in **2025H2 at 31% (53/170)**,
  twice the share in the halves before and after it. We did not predict or test this.
- The share with money fell in each half-year after 2025H1 (47% -> 38% -> 25% -> 22%), while the
  75th percentile of amounts rose ($4,221 -> $7,472 -> $7,875 -> $10,000). Fewer decisions carry
  money, but the large awards make up a larger part of those that do.
- Pro se litigants' share with money rose slowly (2% -> 6% -> 7% -> 9%) but stayed far below
  lawyers'. Their 2026H1 median ($500) is much lower than lawyers' ($2,731).

## Limits (stated in the pre-registration, and they matter here)

1. **The database is a collection, not a census.** It holds decisions that came to its author's
   attention, and its coverage grew very fast (US lawyer decisions: 38 in 2025H1, 241 in 2026H1).
   Early collection may have caught mostly the dramatic, sanctioned cases; later collection
   catches routine warnings and show-cause orders too. That alone could produce the falling share.
   This result describes the database. It does not show that any court became more lenient.
2. **Recent rows may be coded less completely.** If penalty fields are filled in after a row is
   first added, the newest periods would show fewer penalties. 2026H2 is reported only for
   context and is not compared.
3. **Amounts are as the database records them.** They can include fee awards as well as
   penalties. "1" placeholders and non-USD amounts are excluded from amount statistics (2025H1
   has 2 placeholders, 2026H1 has 2).
4. **Small early samples.** 2025H1 has 38 lawyer decisions and 16 USD amounts, just above the
   pre-registered minimums (30 decisions, 10 amounts).
5. **"Lawyer" is the database's party label.** Prosecutors and federal defenders are labelled
   separately and are not counted as lawyer decisions here.

## Why this is new

Trackers and articles compare landmark sanctions (*Mata v. Avianca*'s $5,000 in 2023 with
*Couvrette v. Wisnovsky*'s $110,204 in 2026) or add up totals (for example "$145,000 in Q1 2026
penalties"). Vaquill's pooled count of the 12 Oct 2026 CSV gives a single median ($3,000) and a
professional-sanction count across all years. On 6 Nov 2026 we found no published per-period
share of decisions that carry a penalty, and no per-period median. This study reports both, with
the predictions fixed and public before the data was downloaded.

## Reproduce

```
python run_job.py --out-dir out      # waits for the public PREREG, checks analyze.py's hash, downloads, grades
python -m unittest -v                # offline tests of the parser and the grader
```

The database changes daily, so a later download will give somewhat different counts. The
`results/` folder holds the derived US rows (`us_rows.csv`), the full `results.json`,
`results.md`, and the download's time and hash (`source.json`, `status.json`).

*Credit: AI Hallucination Cases Database, Damien Charlotin (CC BY 4.0). Made with AI agents
working in MV2's name. Information only, not legal advice.*
