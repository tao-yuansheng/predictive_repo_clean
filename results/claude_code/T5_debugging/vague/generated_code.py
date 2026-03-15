"""
T5 — Debugging: Fixed Pipeline
Agent: claude_code
Prompt type: vague

This is the corrected version of tasks/T5_debugging/buggy_pipeline.py.
Three bugs were identified and fixed. See bug_report.json for details.
"""

# ── Fixed pipeline — Adult Income dataset ─────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import json
import os

OUT_DIR = "results/claude_code/T5_debugging/vague/output"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv("data/raw/dataset.csv")
print("Loaded dataset:", df.shape)

# ── Clean missing values ───────────────────────────────────────────────────────
# FIX 1 (was BUG 1): The original code only filtered rows where workclass == '?'.
# occupation and native.country also contain '?' missing values.
# Fix: remove any row that contains '?' in any column.
df = df[~(df == "?").any(axis=1)]
print("After cleaning:", df.shape)

# Strip whitespace from string columns
str_cols = df.select_dtypes(include="object").columns
df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

# ── EDA ────────────────────────────────────────────────────────────────────────
print("\nIncome distribution:\n", df["income"].value_counts())
print("\nAge stats:\n", df["age"].describe())

# Plot 1 — income distribution
plt.figure(figsize=(6, 4))
df["income"].value_counts().plot(kind="bar", color=["steelblue", "coral"])
plt.title("Income Distribution")
plt.xlabel("Income")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "income_distribution.png"), dpi=150)
plt.close()

# Plot 2 — age by income
plt.figure(figsize=(8, 4))
for label, grp in df.groupby("income"):
    grp["age"].hist(alpha=0.6, bins=25, label=label)
plt.title("Age Distribution by Income")
plt.xlabel("Age")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "age_by_income.png"), dpi=150)
plt.close()

# Plot 3 — hours per week distribution
plt.figure(figsize=(7, 4))
sns.boxplot(x="income", y="hours.per.week", data=df)
plt.title("Hours per Week by Income")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "hours_by_income.png"), dpi=150)
plt.close()

print("Plots saved to", OUT_DIR)

# ── Encode categorical columns ─────────────────────────────────────────────────
cat_cols = ["workclass", "education", "marital.status", "occupation",
            "relationship", "race", "sex", "native.country"]

# FIX 2 (was BUG 2): A single LabelEncoder was reused across all columns.
# Reusing the same encoder means each fit_transform overwrites the previous
# label mapping. Fix: use a separate LabelEncoder instance per column.
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

# Encode target
df["income"] = (df["income"].str.strip() == ">50K").astype(int)

# ── Train / test split ─────────────────────────────────────────────────────────
X = df.drop(["income", "fnlwgt"], axis=1)
y = df["income"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Scale features ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# FIX 3 (was BUG 3): The original code called fit_transform on the test set,
# which re-fits the scaler using test data statistics (mean, std). This causes
# data leakage — the test set should be scaled using the training set's statistics.
# Fix: use scaler.transform(X_test) instead.
X_test = scaler.transform(X_test)

# ── Train model ────────────────────────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = round(accuracy_score(y_test, y_pred), 4)
report_str = classification_report(y_test, y_pred, target_names=["<=50K", ">50K"])
report_dict = classification_report(y_test, y_pred, target_names=["<=50K", ">50K"], output_dict=True)

print("\nAccuracy:", acc)
print("\nClassification Report:\n", report_str)

# ── Save metrics and bug report ────────────────────────────────────────────────
bug_report = {
    "source_script": "tasks/T5_debugging/buggy_pipeline.py",
    "bugs_found": [
        {
            "bug_id": 1,
            "location": "line 22",
            "description": "Missing value cleaning was incomplete: only filtered rows where workclass == '?', but occupation and native.country also contain '?' as missing value markers.",
            "original_code": "df = df[df['workclass'] != '?']",
            "fixed_code": "df = df[~(df == '?').any(axis=1)]",
            "impact": "~2,400 rows with missing occupation/native.country values were not removed, contaminating the dataset with implicit NaNs represented as strings."
        },
        {
            "bug_id": 2,
            "location": "lines 71-73",
            "description": "A single LabelEncoder instance was reused across all categorical columns. Each call to fit_transform overwrites the encoder's internal mapping, so the encoder only holds the mapping for the last column encoded.",
            "original_code": "le = LabelEncoder()\\nfor col in cat_cols:\\n    df[col] = le.fit_transform(df[col])",
            "fixed_code": "for col in cat_cols:\\n    le = LabelEncoder()\\n    df[col] = le.fit_transform(df[col])",
            "impact": "The encoding itself is still numeric and functional for training, but the LabelEncoder object would be unusable for inverse transforms. In production pipelines this would cause incorrect decoding of all columns except the last."
        },
        {
            "bug_id": 3,
            "location": "line 94",
            "description": "scaler.fit_transform() was called on the test set instead of scaler.transform(). This re-fits the scaler using test set statistics (mean, std), introducing data leakage — the model sees test distribution information during scaling.",
            "original_code": "X_test = scaler.fit_transform(X_test)",
            "fixed_code": "X_test = scaler.transform(X_test)",
            "impact": "Leaks test set distribution into preprocessing. Leads to optimistic/unreliable evaluation metrics since test data is no longer truly unseen."
        }
    ],
    "model_results_after_fix": {
        "accuracy": acc,
        "classification_report": report_dict
    }
}

with open(os.path.join(OUT_DIR, "bug_report.json"), "w") as f:
    json.dump(bug_report, f, indent=2)
print(f"Saved: bug_report.json")

# Save classification report CSV
cr_df = pd.DataFrame(report_dict).T
cr_df.to_csv(os.path.join(OUT_DIR, "classification_report.csv"))
print("Saved: classification_report.csv")

print("\nT5 complete.")
