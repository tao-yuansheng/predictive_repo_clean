# Leakage Audit Report

## Target Variable
- Target column: `income`
- Dtype: `object`
- Unique values: `['<=50K', '>50K']`

## Summary Table
| Feature | Correlation with Target | Leakage Risk | Reason |
| --- | --- | --- | --- |
| age | corr=0.2340 | Low | Available before prediction time and not semantically derived from income. |
| workclass | mi=0.0150 | Low | Available before prediction time and not semantically derived from income. |
| fnlwgt | corr=-0.0095 | Low | Available before prediction time and not semantically derived from income. |
| education | mi=0.0649 | Low | Available before prediction time and not semantically derived from income. |
| education.num | corr=0.3353 | Low | Available before prediction time and not semantically derived from income. |
| marital.status | mi=0.1085 | Low | Available before prediction time and not semantically derived from income. |
| occupation | mi=0.0644 | Low | Available before prediction time and not semantically derived from income. |
| relationship | mi=0.1146 | Low | Available before prediction time and not semantically derived from income. |
| race | mi=0.0058 | Low | Available before prediction time and not semantically derived from income. |
| sex | mi=0.0258 | Low | Available before prediction time and not semantically derived from income. |
| capital.gain | corr=0.2233 | High | Direct component of the annual income definition, so it acts like a label proxy. |
| capital.loss | corr=0.1505 | High | Direct component of the annual income definition, so it acts like a label proxy. |
| hours.per.week | corr=0.2297 | Low | Available before prediction time and not semantically derived from income. |
| native.country | mi=0.0060 | Low | Available before prediction time and not semantically derived from income. |

## Flagged Feature Explanations
### capital.gain
- Risk type: direct encoding
- Evidence: capital gain is part of annual income and therefore acts as a proxy for the >50K threshold.
- Action: drop

### capital.loss
- Risk type: direct encoding
- Evidence: capital loss is also an income-period financial component tied to the target definition.
- Action: drop

## Verification
- Shape before removal: `(32537, 15)`
- Shape after removal: `(32537, 13)`
- Remaining >0.95 numeric correlations: `None`
- Original accuracy: `0.8231`
- Cleaned accuracy: `0.8075`
- Accuracy change: `-0.0157`
- Interpretation: removing the capital variables lowers accuracy, which is consistent with them carrying target-proxy information.
