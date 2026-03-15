#!/usr/bin/env python3
"""
task3_baseline.py — Baseline Logistic Regression on UCI Adult Income Dataset
Agent: claude_code | Prompt type: specific
Run from repository root: python results/claude_code/T3_model/specific/output/task3_baseline.py

# Requirements (requirements_task3.txt):
# scikit-learn>=1.3.0
# pandas>=2.0.0
# numpy>=1.24.0
# matplotlib>=3.7.0
# joblib>=1.3.0
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)

# ── Reproducibility ────────────────────────────────────────────────────────────
np.random.seed(42)
RANDOM_STATE = 42

# ── Paths ──────────────────────────────────────────────────────────────────────
CLEAN_PATH = "results/claude_code/T1_ingestion/specific/output/dataset_clean.csv"
RAW_PATH   = "data/raw/dataset.csv"
OUT_DIR    = "results/claude_code/T3_model/specific/output"
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Load Data ──────────────────────────────────────────────────────────────
if os.path.exists(CLEAN_PATH):
    df = pd.read_csv(CLEAN_PATH)
    print(f"Loaded cleaned dataset: {CLEAN_PATH}")
else:
    print("Cleaned dataset not found; applying cleaning to raw data.")
    df = pd.read_csv(RAW_PATH)
    df.replace("?", np.nan, inplace=True)
    str_cols = df.select_dtypes("object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())
    df = df.drop_duplicates()
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype == object:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna(df[col].median())

print(f"Shape: {df.shape}")
assert "income" in df.columns, "Target column 'income' not found!"

# Encode target
df["income"] = df["income"].str.strip().map({"<=50K": 0, ">50K": 1})
assert df["income"].nunique() == 2, "Target is not binary!"
print(f"Target distribution:\n{df['income'].value_counts()}")

# ── 2. Preprocessing ──────────────────────────────────────────────────────────
# Drop fnlwgt (census weight) and education (redundant with education.num)
df = df.drop(columns=[c for c in ["fnlwgt", "education"] if c in df.columns])

# Encode categorical columns (one LabelEncoder per column — no leakage)
cat_cols = df.select_dtypes("object").columns.tolist()
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))

X = df.drop(columns=["income"])
y = df["income"]

# 80/20 stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# Scale numeric features: fit on train only, transform test
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)   # transform only, no leakage

# ── 3. Baseline Model ─────────────────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
model.fit(X_train_sc, y_train)
print("Logistic Regression trained.")

# ── 4. Evaluation Harness ─────────────────────────────────────────────────────
y_pred = model.predict(X_test_sc)
y_prob = model.predict_proba(X_test_sc)[:, 1]

acc       = round(accuracy_score(y_test, y_pred), 4)
precision = round(precision_score(y_test, y_pred, zero_division=0), 4)
recall    = round(recall_score(y_test, y_pred, zero_division=0), 4)
f1        = round(f1_score(y_test, y_pred, zero_division=0), 4)
roc_auc   = round(roc_auc_score(y_test, y_prob), 4)

print(f"\nAccuracy : {acc}")
print(f"Precision: {precision}")
print(f"Recall   : {recall}")
print(f"F1-score : {f1}")
print(f"ROC-AUC  : {roc_auc}")
print(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['<=50K', '>50K'])}")

# Confusion matrix plot
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(5, 4))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
ax.set_xticklabels(["<=50K", ">50K"]); ax.set_yticklabels(["<=50K", ">50K"])
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title(f"Confusion Matrix (Accuracy={acc})")
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14)
plt.colorbar(im)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "confusion_matrix.png"), dpi=150)
plt.close()
print("Saved: confusion_matrix.png")

# ── 5. Output & Reproducibility ───────────────────────────────────────────────
# Save metrics JSON
metrics = {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1, "roc_auc": roc_auc}
with open(os.path.join(OUT_DIR, "task3_results.json"), "w") as f:
    json.dump(metrics, f, indent=2)
print("Saved: task3_results.json")

# Save model
joblib.dump(model, os.path.join(OUT_DIR, "baseline_model.pkl"))
print("Saved: baseline_model.pkl")

print("task3_baseline.py complete.")
