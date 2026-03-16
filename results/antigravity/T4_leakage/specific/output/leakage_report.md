# Data Leakage Audit Report

Target variable: income

## Audit Summary Table
| Feature        |   Correlation |         MI | Risk   | Reason                                   |
|:---------------|--------------:|-----------:|:-------|:-----------------------------------------|
| age            |    0.234037   | 0.0663501  | Low    | No obvious leakage                       |
| workclass      |   -0.0551802  | 0.0199094  | Low    | No obvious leakage                       |
| fnlwgt         |   -0.00950235 | 0.0331076  | Medium | Census weight, not a demographic feature |
| education      |    0.0793664  | 0.0655448  | Low    | No obvious leakage                       |
| education.num  |    0.335272   | 0.069784   | Medium | Direct ordinal encoding of 'education'   |
| marital.status |   -0.199199   | 0.107781   | Low    | No obvious leakage                       |
| occupation     |    0.0106743  | 0.0641103  | Low    | No obvious leakage                       |
| relationship   |   -0.250948   | 0.118573   | Low    | No obvious leakage                       |
| race           |    0.0718475  | 0.00795013 | Low    | No obvious leakage                       |
| sex            |    0.215969   | 0.0237145  | Low    | No obvious leakage                       |
| capital.gain   |    0.223336   | 0.0827833  | Low    | No obvious leakage                       |
| capital.loss   |    0.150501   | 0.0375484  | Low    | No obvious leakage                       |
| hours.per.week |    0.229658   | 0.039091   | Low    | No obvious leakage                       |
| native.country |    0.0229568  | 0.00657443 | Low    | No obvious leakage                       |

## Flagged Column Explanations
- No columns were found with correlation > 0.95 or obvious temporal leakage.

## Verification Results
- Original Accuracy: 0.8251
- Cleaned Accuracy: 0.8251
- Difference: 0.0000
