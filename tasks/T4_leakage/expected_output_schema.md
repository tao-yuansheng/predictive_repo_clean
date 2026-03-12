# T4 — Leakage Detection: Expected Output Schema

Describes what correct output looks like. Used by Member 5 as a reference when scoring.

---

## dataset_leakage_removed.csv
- Fewer columns than the original 15 (confirmed leakers removed)
- Same row count as input (no rows dropped in this task)
- No "?" strings remaining (replaced with NaN as part of loading)

## leakage_report.md
Must contain:

### Section 1 — Summary Table
| Feature | Correlation with Target | Leakage Risk | Reason |
|---------|------------------------|--------------|--------|
| ...     | ...                    | Low/Med/High | ...    |
All 14 features must appear in this table.

### Section 2 — Flagged Column Explanations
For each flagged column:
  Column    : [name]
  Risk type : temporal / derived / direct encoding / other
  Evidence  : [what in the data confirms it]
  Action    : drop / investigate / keep with justification

## Printed Output (captured in session_log.txt)
- Target variable stated with class distribution
- Dataset shape before removal
- Dataset shape after removal
- Before accuracy (model on original data)
- After accuracy (model on cleaned data)
- Commentary on whether accuracy difference confirms leakage

## What FAIL looks like
- Only 1-2 columns audited, rest skipped
- No structured evidence for flagged columns — just assertion
- leakage_report.md is blank or unformatted
- Before/after accuracy comparison absent
- Agent flags `income` itself (the target) as a leaking feature
- No columns flagged at all (there are legitimate candidates to investigate)
