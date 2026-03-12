# T1 — Data Ingestion: Success Criteria

Pass/fail checklist for Member 5 to apply when scoring each run.
Mark each item: PASS / FAIL / PARTIAL

## Correctness
- [ ] Dataset loads without errors from data/raw/dataset.csv
- [ ] All 15 expected columns confirmed present (or a clear error raised if missing)
- [ ] "?" values treated as NaN — not left as strings
- [ ] Missing value count AND percentage reported per column
- [ ] Imputation strategy is appropriate: median for numeric, mode for categorical
- [ ] No duplicate rows remain; count of removed duplicates is reported

## Statistical Validity
- [ ] Outliers detected using IQR (1.5× rule), not a fixed threshold
- [ ] Outliers are capped (not dropped) and count per column is logged
- [ ] Imputation fitted on data without contaminating a held-out test set

## Reproducibility
- [ ] random_state / random seed set to 42 where applicable
- [ ] Code runs end-to-end on a fresh kernel without errors
- [ ] Cleaning decisions documented with inline comments
- [ ] Library versions pinned in a comment at the top of the script

## Output Files
- [ ] dataset_clean.csv saved to the correct results/[AGENT_NAME]/T1_ingestion/{prompt_type}/output/ path
- [ ] missingness_heatmap.png saved to the same output folder
- [ ] Final cleaning report printed (rows before/after, columns dropped, columns imputed, outliers capped)

## Code Quality
- [ ] No silent failures — every check prints a result
- [ ] Cleaning decisions are commented and justified
