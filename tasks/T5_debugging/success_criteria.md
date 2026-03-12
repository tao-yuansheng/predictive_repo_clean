# T5 — Debugging: Success Criteria

Pass/fail checklist for Member 5 to apply when scoring each run.
Mark each item: PASS / FAIL / PARTIAL

## Correctness
- [ ] Bug 1 identified: incomplete "?" removal (only workclass cleaned, not occupation/native.country)
- [ ] Bug 2 identified: single LabelEncoder reused across all categorical columns
- [ ] Bug 3 identified: scaler.fit_transform(X_test) instead of scaler.transform(X_test)
- [ ] All 3 bugs have: line number, bug type, explanation of what goes wrong
- [ ] Fixed script runs end-to-end without errors

## Statistical Validity
- [ ] Bug 3 (test set leakage) classified as Critical or Major — not Minor
- [ ] Before/after accuracy comparison present for any numerically impactful fix
- [ ] Agent explains how silent bugs were detected without running the code

## Reproducibility
- [ ] Fixed script is self-contained and runnable
- [ ] random_state=42 preserved in the fixed version
- [ ] Fixed script produces identical results on each run

## Output Files
- [ ] fixed_pipeline.py saved to correct output path
- [ ] bug_report.md saved to correct output path
- [ ] Each fix annotated with # FIX [N]: comment directly above changed line

## Code Quality
- [ ] Fixed script stays close to the original — no unnecessary refactoring
- [ ] Bug report is structured and readable
- [ ] No new bugs introduced by the fixes
