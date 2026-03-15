# Leakage Audit

Overall conclusion: no direct target leakage was found in the Adult Income dataset columns.

Key observations:
- Direct target copies found: ['income'].
- `education` and `education.num` are perfectly redundant encodings of the same concept.
- `capital.gain` and `capital.loss` are not leaked labels, but they are close to the income outcome and can inflate apparent predictive power.
- `fnlwgt` is not leakage, though it is a survey weight and usually not appropriate as a standard predictive feature.

Recommended modelling actions:
- Drop one of `education` or `education.num`.
- Test model performance with and without `capital.gain` and `capital.loss` if deployment would not know them in advance.
- Exclude `fnlwgt` from baseline models unless survey weighting is explicitly required.