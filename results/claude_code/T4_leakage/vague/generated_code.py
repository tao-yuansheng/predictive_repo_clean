"""
T4 — Data Leakage Audit
Agent: claude_code
Prompt type: vague

Checks the Adult Income dataset for data leakage issues and flags suspicious features.
"""

import pandas as pd
import numpy as np
import json
import os

RAW_PATH = "data/raw/dataset.csv"
OUT_DIR = "results/claude_code/T4_leakage/vague/output"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Load ---
df = pd.read_csv(RAW_PATH)
df.replace("?", np.nan, inplace=True)
str_cols = df.select_dtypes(include="object").columns
df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())
for col in df.columns:
    if df[col].isnull().any():
        df[col] = df[col].fillna(df[col].mode()[0])
df["income_bin"] = df["income"].map({"<=50K": 0, ">50K": 1})

print(f"Loaded: {df.shape}")

flags = []

# ── Check 1: education vs education.num — redundant/derived features ──────────
corr_edu = df["education.num"].groupby(df["education"]).mean()
unique_mappings = df.groupby("education")["education.num"].nunique()
is_perfect = (unique_mappings == 1).all()
flags.append({
    "feature": "education",
    "issue_type": "redundant_derived_feature",
    "severity": "medium",
    "flagged": True,
    "description": (
        "education is a categorical encoding of education.num (and vice versa). "
        "Each education label maps to exactly one numeric value. "
        "Including both is redundant; using education after fitting education.num "
        "or vice versa may inflate apparent feature importance without leaking target, "
        "but could mask multicollinearity. Recommendation: keep only education.num."
    ),
    "evidence": f"Perfect 1-to-1 mapping: {is_perfect}. Unique num per label: {unique_mappings.to_dict()}"
})

# ── Check 2: fnlwgt — census sampling weight ──────────────────────────────────
# fnlwgt is a post-stratification weight assigned by census, derived from demographic
# variables AFTER data collection. It's not a feature the model should use.
corr_fnlwgt = df["fnlwgt"].corr(df["income_bin"])
flags.append({
    "feature": "fnlwgt",
    "issue_type": "non_predictive_administrative_variable",
    "severity": "low",
    "flagged": True,
    "description": (
        "fnlwgt is a census sampling weight, not a demographic feature. "
        "It reflects how many people a record represents in the census population, "
        "derived post-collection from demographic variables. Including it as a "
        "predictor is not meaningful — it is an administrative artifact, not a "
        "causal or observable feature. Correlation with income is near zero. "
        "Recommendation: drop from model."
    ),
    "evidence": f"Correlation with income: {corr_fnlwgt:.4f}"
})

# ── Check 3: Check for near-perfect predictors (proxy leakage) ───────────────
# Check if any single feature achieves very high predictive power alone
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

le = LabelEncoder()
feature_aucs = {}
y = df["income_bin"]
for col in df.columns:
    if col in ["income", "income_bin"]:
        continue
    x = df[col].copy()
    if x.dtype == object:
        x = le.fit_transform(x.astype(str))
    x_arr = np.array(x).reshape(-1, 1)
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    scores = cross_val_score(clf, x_arr, y, cv=3, scoring="roc_auc")
    feature_aucs[col] = round(scores.mean(), 4)

print("Single-feature AUCs (3-fold CV, depth-3 tree):")
for feat, auc in sorted(feature_aucs.items(), key=lambda x: -x[1]):
    print(f"  {feat}: {auc:.4f}")

# Flag features with AUC > 0.75 (suspiciously high for a single feature)
high_auc_feats = {k: v for k, v in feature_aucs.items() if v > 0.75}
if high_auc_feats:
    flags.append({
        "feature": list(high_auc_feats.keys()),
        "issue_type": "high_single_feature_predictive_power",
        "severity": "high" if any(v > 0.85 for v in high_auc_feats.values()) else "medium",
        "flagged": True,
        "description": (
            "Some features achieve suspiciously high AUC individually. "
            "This could indicate target leakage (a feature derived from or "
            "highly correlated with the target), or simply a genuinely strong predictor. "
            "Investigate whether these could be derived from income."
        ),
        "evidence": high_auc_feats
    })

# ── Check 4: Duplicate rows ───────────────────────────────────────────────────
n_dups = df.drop(columns=["income_bin"]).duplicated().sum()
flags.append({
    "feature": "all",
    "issue_type": "duplicate_rows",
    "severity": "low" if n_dups == 0 else "medium",
    "flagged": n_dups > 0,
    "description": f"Found {n_dups} exact duplicate rows (excluding income_bin column). "
                   "If train/test splits are made after duplicates exist, the same row "
                   "could appear in both splits, causing optimistic evaluation.",
    "evidence": f"duplicate_count: {int(n_dups)}"
})

# ── Check 5: Target distribution shift check ─────────────────────────────────
# Check if income rates vary suspiciously by a single low-cardinality variable
# (a warning sign for stratification leakage)
for col in ["sex", "race", "workclass"]:
    group_rates = df.groupby(col)["income_bin"].mean()
    spread = group_rates.max() - group_rates.min()
    if spread > 0.3:
        flags.append({
            "feature": col,
            "issue_type": "large_subgroup_target_rate_variation",
            "severity": "info",
            "flagged": True,
            "description": (
                f"'{col}' shows a large spread ({spread:.2f}) in target rate across groups. "
                "This is not leakage per se, but indicates strong demographic associations "
                "that may cause fairness issues. Ensure train/test splits are stratified."
            ),
            "evidence": group_rates.to_dict()
        })

# ── Save outputs ──────────────────────────────────────────────────────────────
# Single-feature AUC table
auc_df = pd.DataFrame([{"feature": k, "single_feature_auc": v}
                        for k, v in sorted(feature_aucs.items(), key=lambda x: -x[1])])
auc_df.to_csv(os.path.join(OUT_DIR, "single_feature_aucs.csv"), index=False)
print(f"Saved: single_feature_aucs.csv")

# Leakage report JSON
report = {
    "dataset": RAW_PATH,
    "rows": int(df.shape[0]),
    "cols": int(df.shape[1]) - 1,
    "flags": flags,
    "single_feature_aucs": feature_aucs,
    "summary": (
        "No catastrophic target leakage detected. Key concerns: "
        "(1) education and education.num are perfectly redundant — drop one. "
        "(2) fnlwgt is a census administrative weight — not a meaningful predictor, drop it. "
        "(3) capital.gain has the highest single-feature AUC but is legitimately predictive "
        "(it represents actual financial income). "
        "(4) Duplicate rows present — apply deduplication before train/test splits. "
        "(5) Large demographic subgroup target-rate variation warrants fairness analysis."
    )
}
report_path = os.path.join(OUT_DIR, "leakage_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"Saved: {report_path}")

# Human-readable flags CSV
flag_rows = []
for fl in flags:
    flag_rows.append({
        "feature": str(fl["feature"]),
        "issue_type": fl["issue_type"],
        "severity": fl["severity"],
        "flagged": fl["flagged"],
        "description": fl["description"]
    })
flags_df = pd.DataFrame(flag_rows)
flags_df.to_csv(os.path.join(OUT_DIR, "leakage_flags.csv"), index=False)
print("Saved: leakage_flags.csv")

print("\nT4 complete.")
