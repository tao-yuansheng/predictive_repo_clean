# T3 — Baseline Model: Expected Output Schema

Describes what correct output looks like. Used by Member 5 as a reference when scoring.

---

## task3_results.json
```json
{
  "accuracy": 0.85,
  "precision": 0.74,
  "recall": 0.62,
  "f1": 0.67,
  "roc_auc": 0.89
}
```
- All values must be floats between 0 and 1
- All 5 keys must be present
- ROC-AUC must be > 0.5
- Indicative expected range for a clean logistic regression on this dataset:
    accuracy  ~0.82–0.87
    roc_auc   ~0.87–0.92
- ROC-AUC > 0.99 is a leakage red flag

## confusion_matrix.png
- 2x2 matrix for binary classification (0=<=50K, 1=>50K)
- Cells show counts: TN, FP, FN, TP
- Axis labels: Predicted / Actual
- Readable at normal viewing size

## baseline_model.pkl
- Loadable with: import joblib; model = joblib.load('baseline_model.pkl')
- Must be a fitted sklearn LogisticRegression object
- model.predict() must run without error on a correctly preprocessed test set

## requirements_task3.txt
Format:
  scikit-learn==x.x.x
  pandas==x.x.x
  numpy==x.x.x

## task3_baseline.py
- Runnable with `python task3_baseline.py` from the repo root
- Produces identical metrics on each run (seeds fixed)
- Saves all output files to the correct results path

## What FAIL looks like
- ROC-AUC = 0.5 (random — likely label encoding or split error)
- ROC-AUC > 0.99 (likely leakage)
- task3_results.json missing keys or values stored as strings
- baseline_model.pkl not loadable
- StandardScaler fit_transform called on test set
