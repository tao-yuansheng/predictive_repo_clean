# Debugging Summary

Fixed issues:
- Replaced `?` markers across the dataset by reading them as missing values and dropping incomplete rows.
- Standardized whitespace in string columns before encoding the target.
- Used a separate `LabelEncoder` per categorical column.
- Prevented test-set leakage by applying `scaler.transform(X_test)` instead of refitting on test data.
- Made file paths robust and saved outputs to the required task folder.

Results:
- Rows after cleaning: 30162
- Train rows: 24129
- Test rows: 6033
- Accuracy: 0.8298
