# T5 — Debugging: Expected Output Schema

Describes what correct output looks like. Used by Member 5 as a reference when scoring.

---

## bug_report.md
Must contain a structured entry for each of the 3 planted bugs:

  Bug 1
  Location  : line 22, data cleaning block
  Type      : silent error / incomplete cleaning
  Severity  : Major
  What it does wrong : Only removes "?" from workclass; occupation and native.country
                       still contain "?" strings which corrupt downstream encoding.
  Why it matters     : LabelEncoder treats "?" as a valid category, producing a
                       spurious label that distorts the model.

  Bug 2
  Location  : lines 47-49, categorical encoding loop
  Type      : logic bug
  Severity  : Major
  What it does wrong : A single LabelEncoder is reused for all categorical columns;
                       each fit_transform call overwrites the previous mapping.
  Why it matters     : Encoder holds no valid mapping for any column except the last.

  Bug 3
  Location  : line 63, feature scaling block
  Type      : data leakage
  Severity  : Critical
  What it does wrong : scaler.fit_transform(X_test) re-fits the scaler on test data.
  Why it matters     : Test set scaled using its own statistics, leaking test
                       distribution and inflating reported metrics.

## fixed_pipeline.py
- Contains exactly 3 # FIX [N]: comments above corrected lines
- Bug 1 fix: df = df[~(df == '?').any(axis=1)]
- Bug 2 fix: le = LabelEncoder() instantiated inside the loop (one per column)
- Bug 3 fix: X_test = scaler.transform(X_test)
- Script runs end-to-end and prints accuracy + classification report

## Printed Output (captured in session_log.txt)
- Structured bug identification report
- Severity classifications for all 3 bugs
- Before/after accuracy comparison (Bug 3 typically changes accuracy by ~0.5-2%)

## What FAIL looks like
- Only Bug 3 found — Bugs 1 and 2 missed
- Bug 3 classified as Minor (underestimates leakage severity)
- Fixed script introduces new errors
- # FIX comments absent or misplaced
- bug_report.md is unstructured prose
