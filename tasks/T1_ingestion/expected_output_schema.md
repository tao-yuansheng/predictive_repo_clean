# T1 — Data Ingestion: Expected Output Schema

Describes what correct output looks like. Used by Member 5 as a reference when scoring.

---

## dataset_clean.csv
- Same 15 column names as input (unless a column was confirmed >50% missing and dropped)
- No "?" strings remaining anywhere in the file
- Numeric columns contain no NaN (imputed)
- Categorical columns contain no NaN (imputed)
- Row count: <= 32,561 (original) — reduced by duplicate removal
- Expected approximate row count after cleaning: ~30,000–32,000
- File encoding: UTF-8, comma-separated

## missingness_heatmap.png
- A heatmap showing missing value pattern across columns
- Axes: columns on x-axis, rows (sampled) on y-axis
- Readable column labels
- Accepted libraries: missingno, seaborn, matplotlib

## Printed Cleaning Report (captured in session_log.txt)
Must include all of:
- Rows before cleaning: 32,561
- Rows after cleaning: [actual number]
- Columns dropped: [list or "none"]
- Columns imputed: workclass (mode), occupation (mode), native.country (mode)
- Outliers capped per numeric column: [counts]

## What FAIL looks like
- "?" still present as string values in the cleaned CSV
- Rows dropped instead of imputed for <20% missingness
- Heatmap missing or blank
- Row count unchanged (no deduplication attempted)
- No printed summary
