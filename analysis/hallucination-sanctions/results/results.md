# AI-hallucination sanctions over time: graded result (analysis 1.0.0)

Source: AI Hallucination Cases Database, Damien Charlotin, https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0). CSV fetched 2026-11-06T14:58:08Z, SHA-256 9201eecd5ea30ac3eda884062a6421f84882abf2f58415aa4391e283ef297c87, 2175509 bytes.

Rows read 2267 (malformed skipped 0); US 1536 (no date 1); US with a lawyer 602; US with a pro se litigant 913.

## Predictions (primary)

- **P1: held** {"a": 0.4737, "b": 0.249, "diff": -0.2247, "perm_p_rise": 0.9989}
- **P2: held** {"a": 1750.0, "b": 2731.0, "n_a": 16, "n_b": 58, "diff": 981.0, "perm_p_rise": 0.1241}
- **P3: failed** {"a": 0.1579, "b": 0.1494, "diff": -0.0085, "perm_p_rise": 0.6595}
- **P4: held** {"by_period": [{"period": "2025H1", "lawyer": 0.4737, "pro_se": 0.0172, "n_lawyer": 38, "n_pro_se": 58, "pro_se_lower": true}, {"period": "2025H2", "lawyer": 0.3765, "pro_se": 0.0632, "n_lawyer": 170, "n_pro_se": 253, "pro_se_lower": true}, {"period": "2026H1", "lawyer": 0.249, "pro_se": 0.0682, "n_lawyer": 241, "n_pro_se": 381, "pro_se_lower": true}]}
- **P5: held** {"b": 0.3112, "n_b": 241}

## Sensitivity

| analysis | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| S1_exclude_alleged | held | held | failed | held | held |
| S2_lawyer_broad | held | held | failed | held | held |
| S3_fined_strict | held | held | failed | held | held |
| S4_years_2025_vs_2026 | held | held | failed | held | held |

## US decisions involving a lawyer, by half-year of decision

| period | n | share with money penalty | USD amounts | median USD | p75 USD | max USD | share >= $10k | share prof. sanction |
|---|---|---|---|---|---|---|---|---|
| 2023H1 | 1 | 1 | 1 | 5,000 | - | 5,000 | 0 | 0 |
| 2023H2 | 3 | 0 | 0 | - | - | - | - | 0.333 |
| 2024H1 | 6 | 0.167 | 1 | 2,000 | - | 2,000 | 0 | 0.333 |
| 2024H2 | 8 | 0.125 | 1 | 2,000 | - | 2,000 | 0 | 0 |
| 2025H1 | 38 | 0.474 | 16 | 1,750 | 4,221 | 31,100 | 0.125 | 0.158 |
| 2025H2 | 170 | 0.377 | 57 | 4,030 | 7,472 | 85,567 | 0.175 | 0.312 |
| 2026H1 | 241 | 0.249 | 58 | 2,731 | 7,875 | 110,204 | 0.224 | 0.149 |
| 2026H2 | 134 | 0.216 | 27 | 4,000 | 10,000 | 46,511 | 0.296 | 0.149 |

## US decisions involving a pro se litigant, by half-year of decision

| period | n | share with money penalty | USD amounts | median USD | p75 USD | max USD | share >= $10k | share prof. sanction |
|---|---|---|---|---|---|---|---|---|
| 2023H1 | 1 | 0 | 0 | - | - | - | - | 0 |
| 2023H2 | 5 | 0 | 0 | - | - | - | - | 0 |
| 2024H1 | 6 | 0.167 | 1 | 10,000 | - | 10,000 | 1 | 0 |
| 2024H2 | 17 | 0 | 0 | - | - | - | - | 0 |
| 2025H1 | 58 | 0.017 | 1 | 921 | - | 921 | 0 | 0 |
| 2025H2 | 253 | 0.063 | 12 | 3,000 | 9,280 | 66,129 | 0.250 | 0 |
| 2026H1 | 381 | 0.068 | 21 | 500 | 1,665 | 11,799 | 0.095 | 0 |
| 2026H2 | 192 | 0.088 | 9 | 1,000 | 2,341 | 23,222 | 0.111 | 0.005 |

Amounts are as the database records them; they can include fee awards as well as penalties. Made with AI agents working in MV2's name. Information only, not legal advice.
