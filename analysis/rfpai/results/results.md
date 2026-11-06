# Results: how 2026 legal-aid RFPs treat a vendor's own use of AI

Machine-written by grade_rfpai.py (Apache-2.0). MV2 of Munim, Inc.; made with AI agents working in his name. Not legal advice.

- Coding file sha256: `d9f8456e502ffacc039c7784dc5385ca17fc4046a5547a4a485c6ab878af5335`
- Files fetched: 18 of 18 with matching SHA-256; quotations found: 34 of 34; structure problems: 0
- Verified: **True**

## Full frame (17 codable postings)

| | Result | Numbers |
|---|---|---|
| P1 VENDOR_AI share <= 30% | held | 3/17 = 17.6% |
| P2 H2 share > H1 share | failed | H1 2/9 = 22.2%; H2 1/8 = 12.5% |
| P3 no `ban` | held | ban records: none |
| P4 AI_IN_SCOPE among TECH >= 25% | held | 5/8 = 62.5% |

VENDOR_AI records: R01, R04, R17; sub-codes: {'disclose': 2, 'human_review': 2, 'data': 1, 'restrict': 1, 'ban': 0}

## Sensitivity frame (12 codable postings)

| | Result | Numbers |
|---|---|---|
| P1 VENDOR_AI share <= 30% | held | 3/12 = 25.0% |
| P2 H2 share > H1 share | not testable | H1 2/8 = 25.0%; H2 1/4 = 25.0% |
| P3 no `ban` | held | ban records: none |
| P4 AI_IN_SCOPE among TECH >= 25% | held | 3/6 = 50.0% |

VENDOR_AI records: R01, R04, R17; sub-codes: {'disclose': 2, 'human_review': 2, 'data': 1, 'restrict': 1, 'ban': 0}

## Exploratory: each borderline call flipped (full frame)

| Record | Field -> alt | Predictions that change |
|---|---|---|
| R01 | vendor_ai -> False | P2: failed -> held |
| R05 | vendor_ai -> True | none |
| R06 | vendor_ai -> True | none |
| R07 | tech -> TECH | none |
| R08 | tech -> TECH | none |
| R09 | tech -> TECH | none |
| R12 | tech -> TECH | none |
| R13 | vendor_ai -> True | P2: failed -> held |
| R13 | tech -> TECH | none |
| R14 | tech -> NON_TECH | none |

## Failed checks

- none
