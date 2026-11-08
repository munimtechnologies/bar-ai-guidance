# AI-fabricated authority at US procurement tribunals: graded result (analysis 1.0.0)

Source: AI Hallucination Cases Database, Damien Charlotin, https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0). CSV fetched 2026-11-08T14:59:11Z, SHA-256 9201eecd5ea30ac3eda884062a6421f84882abf2f58415aa4391e283ef297c87, 2175509 bytes.

Rows read 2267 (malformed skipped 0); procurement rows at GAO/COFC/ASBCA/CBCA 32.

## Predictions (primary)

- **A1: failed**. Jan-Jul 2026 rows at GAO/COFC/ASBCA/CBCA >= 15 (Timm: 19). {"n": 14, "threshold": 15, "timm": 19}
- **A2: failed**. 2025 rows at these forums >= 17 (Timm: 23 in all). {"n": 15, "threshold": 17, "timm": 23}
- **A3: held**. lawyer share higher in Jan-Oct 2026 than in 2025. {"share_2025": 0.1333, "share_2026": 0.4118, "lawyer_2025": 2, "n_2025": 15, "lawyer_2026": 7, "n_2026": 17}
- **A4: held**. pro se share of GAO rows (2025 to Oct 2026) >= 60%. {"pro_se": 17, "n": 24, "share": 0.7083, "threshold": 0.6, "lawyer": 7}
- **A5: held**. at most 1 row (2025 to Oct 2026) with a monetary penalty. {"n_money": 0, "n": 32, "max_allowed": 1}
- **A6: failed**. one protester accounts for >= 25% of GAO rows (2025 to Oct 2026). {"top_count": 2, "n": 24, "share": 0.0833, "threshold": 0.25, "top_key": "oready", "n_distinct_keys": 23}

## Sensitivity

| analysis | A1 | A2 | A3 | A4 | A5 | A6 |
|---|---|---|---|---|---|---|
| S1_cofc_all_rows | held | held | held | held | held | failed |
| S2_forum_also_from_case_name_or_source | failed | failed | held | held | held | failed |
| S3_exclude_alleged | failed | failed | held | held | held | failed |

## Rows by forum and half-year (procurement rows)

| forum | half | rows | lawyer | pro se | money penalty | prof. sanction |
|---|---|---|---|---|---|---|
| GAO | 2025H1 | 3 | 1 | 2 | 0 | 0 |
| GAO | 2025H2 | 8 | 0 | 8 | 0 | 0 |
| GAO | 2026H1 | 9 | 5 | 4 | 0 | 0 |
| GAO | 2026H2 | 4 | 1 | 3 | 0 | 0 |
| ASBCA | 2025H1 | 0 | 0 | 0 | 0 | 0 |
| ASBCA | 2025H2 | 1 | 1 | 0 | 0 | 0 |
| ASBCA | 2026H1 | 2 | 1 | 1 | 0 | 0 |
| ASBCA | 2026H2 | 1 | 0 | 1 | 0 | 0 |
| CBCA | 2025H1 | 0 | 0 | 0 | 0 | 0 |
| CBCA | 2025H2 | 1 | 0 | 1 | 0 | 0 |
| CBCA | 2026H1 | 1 | 0 | 1 | 0 | 0 |
| CBCA | 2026H2 | 0 | 0 | 0 | 0 | 0 |
| COFC | 2025H1 | 0 | 0 | 0 | 0 | 0 |
| COFC | 2025H2 | 2 | 0 | 2 | 0 | 0 |
| COFC | 2026H1 | 0 | 0 | 0 | 0 | 0 |
| COFC | 2026H2 | 0 | 0 | 0 | 0 | 0 |

## Against Timm (Burr & Forman, 11 Sep 2026), January-July 2026

| forum | Timm | database |
|---|---|---|
| GAO | 12 | 10 |
| ASBCA | 4 | 3 |
| CBCA | 1 | 1 |
| COFC | 2 | 0 |
| FEDCIR | 1 | 0 |

Made with AI agents working in MV2's name. Information only, not legal advice.
