# T4 — Leakage Detection: Success Criteria

Pass/fail checklist for Member 5 to apply when scoring each run.
Mark each item: PASS / FAIL / PARTIAL

## Correctness
- [ ] Target variable correctly identified as `income`
- [ ] All 14 feature columns audited (not just a subset)
- [ ] Three checks applied per feature: temporal, correlation, semantic
- [ ] Summary table printed: Feature | Correlation with Target | Leakage Risk | Reason
- [ ] Flagged columns explained with structured evidence (column, risk type, evidence, action)
- [ ] Confirmed leaking columns removed from the dataset
- [ ] Dataset shape printed before and after removal

## Statistical Validity
- [ ] Correlation/mutual information computed correctly (target encoded as 0/1)
- [ ] Post-removal correlation check confirms no remaining feature > 0.95 with target
- [ ] Before/after accuracy comparison present and commented on
- [ ] Accuracy drop (if any) correctly interpreted as evidence of real leakage

## Reproducibility
- [ ] random_state=42 used on any model trained
- [ ] Code runs end-to-end without errors on a fresh kernel
- [ ] Library versions pinned at top of file

## Output Files
- [ ] dataset_leakage_removed.csv saved to correct output path
- [ ] leakage_report.md saved to correct output path
- [ ] leakage_report.md contains: summary table + per-column explanations for all flagged features

## Code Quality
- [ ] Audit logic is systematic — not just checking a single column
- [ ] Decisions justified with evidence, not just asserted
