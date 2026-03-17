"""
T3 — Baseline Model Training and Evaluation
Agent: claude_code
Prompt type: vague

Trains a Logistic Regression baseline on the Adult Income dataset
and evaluates classification performance.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
)

RAW_PATH = "data/raw/dataset.csv"
CLEAN_PATH = "results/claude_code/T1_ingestion/vague/output/cleaned_dataset.csv"
OUT_DIR = "results/claude_code/T3_model/vague/output"
os.makedirs(OUT_DIR, exist_ok=True)

# --- 1. Load cleaned dataset ---
if os.path.exists(CLEAN_PATH):
    df = pd.read_csv(CLEAN_PATH)
    print(f"Using cleaned dataset: {CLEAN_PATH}")
else:
    df = pd.read_csv(RAW_PATH)
    df.replace("?", np.nan, inplace=True)
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())
    for col in df.columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])
    df["income"] = df["income"].map({"<=50K": 0, ">50K": 1})
    print("Using raw dataset (no clean version found)")

print(f"Dataset shape: {df.shape}")

# --- 2. Feature engineering ---
# Drop fnlwgt (census weight, not predictive) and education (redundant with education.num)
drop_cols = ["fnlwgt", "education"]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# Encode remaining categorical columns
cat_cols = df.select_dtypes(include="object").columns.tolist()
le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col].astype(str))

X = df.drop(columns=["income"])
y = df["income"]

# --- 3. Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

# --- 4. Scale features ---
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# --- 5. Train Logistic Regression baseline ---
model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
model.fit(X_train_sc, y_train)

# --- 6. Evaluate ---
y_pred = model.predict(X_test_sc)
y_prob = model.predict_proba(X_test_sc)[:, 1]

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
report = classification_report(y_test, y_pred, target_names=["<=50K", ">50K"], output_dict=True)
cm = confusion_matrix(y_test, y_pred)

print(f"\nAccuracy:  {acc:.4f}")
print(f"ROC-AUC:   {auc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["<=50K", ">50K"]))

# --- 7. Save outputs ---

# 7a. Metrics JSON
metrics = {
    "model": "LogisticRegression",
    "features_used": list(X.columns),
    "features_dropped": drop_cols,
    "train_size": int(len(X_train)),
    "test_size": int(len(X_test)),
    "accuracy": round(acc, 4),
    "roc_auc": round(auc, 4),
    "classification_report": report,
    "confusion_matrix": cm.tolist(),
    "notes": [
        "Baseline model: Logistic Regression with class_weight='balanced' for imbalanced classes.",
        "fnlwgt dropped (census weight, not predictive). education dropped (redundant with education.num).",
        "Categorical features label-encoded; numeric features standardized.",
        "80/20 stratified train/test split with random_state=42."
    ]
}
metrics_path = os.path.join(OUT_DIR, "model_metrics.json")
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"Saved: {metrics_path}")

# 7b. Classification report CSV
report_df = pd.DataFrame(report).T
report_df.to_csv(os.path.join(OUT_DIR, "classification_report.csv"))
print(f"Saved: classification_report.csv")

# 7c. Confusion matrix plot
fig, ax = plt.subplots(figsize=(5, 4))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
ax.set_xticklabels(["<=50K", ">50K"]); ax.set_yticklabels(["<=50K", ">50K"])
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title("Confusion Matrix")
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14)
plt.colorbar(im)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "confusion_matrix.png"), dpi=150)
plt.close()
print("Saved: confusion_matrix.png")

# 7d. ROC curve plot
fpr, tpr, _ = roc_curve(y_test, y_prob)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, label=f"Logistic Regression (AUC={auc:.3f})", color="steelblue")
ax.plot([0, 1], [0, 1], "k--", label="Random baseline")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "roc_curve.png"), dpi=150)
plt.close()
print("Saved: roc_curve.png")

# 7e. Feature importance (coefficients)
coef_df = pd.DataFrame({
    "feature": X.columns,
    "coefficient": model.coef_[0]
}).sort_values("coefficient", key=abs, ascending=False)
coef_df.to_csv(os.path.join(OUT_DIR, "feature_coefficients.csv"), index=False)

fig, ax = plt.subplots(figsize=(8, 6))
colors = ["coral" if c > 0 else "steelblue" for c in coef_df["coefficient"]]
ax.barh(coef_df["feature"], coef_df["coefficient"], color=colors, edgecolor="black")
ax.set_title("Logistic Regression Feature Coefficients")
ax.set_xlabel("Coefficient (positive = more likely >50K)")
ax.axvline(0, color="black", linewidth=0.8)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "feature_coefficients.png"), dpi=150)
plt.close()
print("Saved: feature_coefficients.png")

print(f"\nT3 complete. Accuracy={acc:.4f}, AUC={auc:.4f}")
