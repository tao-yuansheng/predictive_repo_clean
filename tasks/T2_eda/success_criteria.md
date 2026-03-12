# T2 — EDA: Success Criteria

Pass/fail checklist for Member 5 to apply when scoring each run.
Mark each item: PASS / FAIL / PARTIAL

## Correctness
- [ ] Dataset loaded and "?" values replaced with NaN before any analysis
- [ ] Summary statistics computed for all 6 numeric columns (mean, median, std, skew, kurtosis)
- [ ] Outlier counts reported per numeric column using IQR
- [ ] Value counts and cardinality reported for all 8 categorical columns
- [ ] capital.gain and capital.loss zero-inflation noted explicitly
- [ ] Class imbalance ratio reported (<=50K : >50K)
- [ ] Top 5 features correlated with income identified

## Statistical Validity
- [ ] Correlation computed only on numeric features (no raw string columns)
- [ ] Target encoded as binary (0/1) before correlation — not left as string
- [ ] Bivariate plots cover at least the top 3 correlated features

## Code Quality
- [ ] Plots have titles, axis labels, and are saved with descriptive filenames
- [ ] Code is commented and readable
- [ ] No silent errors — all steps produce visible output

## Output Files
- [ ] At minimum these plots saved to output folder:
      - income distribution (bar or pie)
      - distribution plots for numeric columns
      - correlation heatmap
      - at least 1 bivariate plot
- [ ] Written summary present at end of script (printed or as comments)
- [ ] Leakage flags section present with at least 1 justified flag

## Reproducibility
- [ ] Code runs end-to-end on a fresh kernel without errors
