# T3 — Baseline Model: Success Criteria

Pass/fail checklist for Member 5 to apply when scoring each run.
Mark each item: PASS / FAIL / PARTIAL

## Correctness
- [ ] Data loaded correctly (preferring cleaned T1 output, falling back to raw)
- [ ] Target column `income` encoded as binary 0/1
- [ ] 80/20 train/test split applied with random_state=42
- [ ] All 5 metrics reported: Accuracy, Precision, Recall, F1-score, ROC-AUC
- [ ] Full classification report printed
- [ ] ROC-AUC > 0.5 (better than random baseline)

## Statistical Validity
- [ ] StandardScaler fitted on training set ONLY — transform (not fit_transform) applied to test set
- [ ] LabelEncoder applied per column — not a single shared encoder reused across columns
- [ ] No target-derived or post-outcome features included as inputs (no leakage)

## Reproducibility
- [ ] random_state=42 set on train/test split and model
- [ ] task3_baseline.py reruns and produces identical metrics
- [ ] Library versions recorded in requirements_task3.txt

## Output Files
- [ ] task3_baseline.py saved
- [ ] baseline_model.pkl saved (loadable with joblib)
- [ ] task3_results.json saved with correct keys: accuracy, precision, recall, f1, roc_auc
- [ ] confusion_matrix.png saved and readable
- [ ] requirements_task3.txt saved

## Code Quality
- [ ] Code is modular and commented
- [ ] No hardcoded magic numbers without explanation
