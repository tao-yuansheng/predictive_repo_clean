# Leakage Audit Report
Agent: claude_code | Task: T4_leakage | Prompt: specific

## 1. Target Variable
- **Column**: `income`
- **Type**: Binary categorical (<=50K / >50K)
- **Distribution**: {'<=50K': 24720, '>50K': 7841}
- All 14 remaining columns are candidate features.

## 2. Feature Leakage Audit Summary Table

| Feature | Correlation with Target | Leakage Risk | Reason |
|---------|------------------------|--------------|--------|
| age | 0.234 | NONE | No leakage detected |
| fnlwgt | 0.0095 | MEDIUM | fnlwgt is a post-stratification census weight, not a demographic feature. Its values are derived from the census methodology, not from income, but it is not a meaningful predictor. |
| education.num | 0.3352 | NONE | No leakage detected |
| capital.gain | 0.2233 | NONE | No leakage detected |
| capital.loss | 0.1505 | NONE | No leakage detected |
| hours.per.week | 0.2297 | NONE | No leakage detected |
| workclass | 0.0027 | NONE | No leakage detected |
| education | 0.0793 | MEDIUM | education and education.num are perfectly redundant — one is the ordinal encoding of the other. Using both would be redundant, not leakage of the target per se, but bad practice. |
| marital.status | 0.1993 | NONE | No leakage detected |
| occupation | 0.0346 | NONE | No leakage detected |
| relationship | 0.2509 | NONE | No leakage detected |
| race | 0.0718 | NONE | No leakage detected |
| sex | 0.216 | NONE | No leakage detected |
| native.country | 0.0231 | NONE | No leakage detected |

## 3. Flagged Features — Detailed Analysis

### `education` — MEDIUM risk (redundant derived feature)
- **Risk type**: redundant_derived_feature
- **Evidence**: `education.num` is a perfect ordinal encoding of `education`. Each education label maps to exactly one numeric value. Including both is redundant and introduces perfect multicollinearity.
- **Action**: **DROP** — keep `education.num`.

### `fnlwgt` — MEDIUM risk (non-predictive administrative variable)
- **Risk type**: non_predictive_administrative_variable
- **Evidence**: `fnlwgt` is a census sampling weight assigned post-collection. It has near-zero correlation with income (r ≈ 0.01) and no causal relationship to individual earning capacity.
- **Action**: **DROP** — not a meaningful predictor.

### High Correlation Check
- No feature had |correlation| > 0.95 with the target. No direct target encoding detected.
- Max |correlation| after removal: **0.3352** (below 0.95 threshold).

## 4. Before/After Shape
- Before: 32561 rows × 15 feature columns
- After:  32561 rows × 12 feature columns

## 5. Before/After Accuracy
- Original (all features): **0.8254**
- Cleaned (education + fnlwgt dropped): **0.8245**
- Difference: +0.0009

**Interpretation**: The accuracy difference is small, confirming the dropped features
did not provide meaningful predictive signal. Their removal is justified on grounds of
redundancy (education) and non-predictive administrative nature (fnlwgt), not because
they directly encoded the target.
