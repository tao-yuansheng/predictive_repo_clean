# Bug Report — T5: Debugging

## Bug 1
- **Location**: Line 20, `df = df[df['workclass'] != '?']`
- **Type**: Data bug / Incomplete cleaning
- **Severity**: Major
- **What it does wrong**: Only removes '?' from the 'workclass' column, ignoring other columns like 'occupation' and 'native.country' that also use '?' as a missing value marker.
- **Why it matters**: Leaves invalid strings in the categorical features, which leads to incorrect cardinality and potentially poor model performance.

## Bug 2
- **Location**: Line 55, `df[col] = le.fit_transform(df[col])` (within for loop)
- **Type**: Logic bug / Encoder reuse
- **Severity**: Critical
- **What it does wrong**: Reuses a single `LabelEncoder` instance across multiple different categorical columns.
- **Why it matters**: Each `fit_transform` call overwrites the previous column's mapping. The encoder only retains the mapping for the *last* column processed, making inverse transforms or consistent encoding of new data impossible for all other columns.

## Bug 3
- **Location**: Line 78, `X_test = scaler.fit_transform(X_test)`
- **Type**: Data leakage / Improper scaling
- **Severity**: Major
- **What it does wrong**: Calls `fit_transform` on the test set instead of just `transform`.
- **Why it matters**: This causes data leakage because the scaler is re-fitted using the test set's own mean and standard deviation, rather than using the statistics learned from the training set. This can artificially inflate or deflate model evaluation metrics.

---

## Severity Classification Summary
| Bug | Severity | Impact |
|-----|----------|--------|
| 1   | Major    | Leaves dirty data in the pipeline |
| 2   | Critical | Corrupts the categorical encoding state |
| 3   | Major    | Causes data leakage from the test set |
