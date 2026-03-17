"""
T1 — Data Ingestion and Cleaning
Agent: claude_code
Prompt type: vague

Loads data/raw/dataset.csv, handles missing values (encoded as "?"),
and saves a cleaned dataset ready for modelling.
"""

import pandas as pd
import numpy as np
import os
import json

# --- Paths ---
RAW_PATH = "data/raw/dataset.csv"
OUT_DIR = "results/claude_code/T1_ingestion/vague/output"
os.makedirs(OUT_DIR, exist_ok=True)

# --- 1. Load ---
df = pd.read_csv(RAW_PATH)
print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# --- 2. Replace "?" with NaN ---
df.replace("?", np.nan, inplace=True)

# Strip whitespace from string columns (common in UCI datasets)
str_cols = df.select_dtypes(include="object").columns
df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

# --- 3. Assess missing values (before imputation) ---
raw_df = pd.read_csv(RAW_PATH)
raw_df.replace("?", np.nan, inplace=True)
raw_df[str_cols] = raw_df[str_cols].apply(lambda c: c.str.strip())
raw_missing = raw_df.isnull().sum()
raw_pct = (raw_missing / len(raw_df) * 100).round(2)

print("\nMissing values (after replacing '?'):")
print(raw_missing[raw_missing > 0])

# --- 4. Handle missing values ---
# workclass, occupation, native.country are categorical -> impute with mode
for col in df.columns:
    if df[col].isnull().any():
        mode_val = df[col].mode()[0]
        df[col].fillna(mode_val, inplace=True)
        print(f"  Filled '{col}' NaNs with mode: '{mode_val}'")

print(f"\nMissing values after imputation: {df.isnull().sum().sum()}")

# --- 5. Encode target variable as binary integer ---
df["income"] = df["income"].map({"<=50K": 0, ">50K": 1})
print(f"\nTarget distribution:\n{df['income'].value_counts()}")

# --- 6. Save outputs ---

# 6a. Cleaned dataset
clean_path = os.path.join(OUT_DIR, "cleaned_dataset.csv")
df.to_csv(clean_path, index=False)
print(f"\nSaved: {clean_path}")

# 6b. Missing-value report
report = pd.DataFrame({
    "column": raw_df.columns,
    "missing_count": raw_missing.values,
    "missing_pct": raw_pct.values,
    "imputation_strategy": [
        "mode" if raw_missing[c] > 0 else "none" for c in raw_df.columns
    ]
})
missing_report_path = os.path.join(OUT_DIR, "missing_value_report.csv")
report.to_csv(missing_report_path, index=False)
print(f"Saved: {missing_report_path}")

# 6c. Data summary JSON
summary = {
    "rows_raw": int(raw_df.shape[0]),
    "cols": int(df.shape[1]),
    "rows_cleaned": int(df.shape[0]),
    "missing_values_before": {c: int(v) for c, v in raw_missing.items() if v > 0},
    "missing_values_after": int(df.isnull().sum().sum()),
    "target_distribution": {str(k): int(v) for k, v in df["income"].value_counts().items()},
    "columns": list(df.columns),
    "dtypes": {c: str(t) for c, t in df.dtypes.items()},
    "notes": [
        "Missing values encoded as '?' in raw data; replaced with NaN.",
        "Categorical NaNs (workclass, occupation, native.country) imputed with column mode.",
        "Target 'income' encoded as binary: 0=<=50K, 1=>50K.",
        "Whitespace stripped from all string columns.",
        "fnlwgt retained but flagged as census weight, not a predictive feature.",
        "education and education.num are redundant; both retained for downstream tasks."
    ]
}
summary_path = os.path.join(OUT_DIR, "data_summary.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"Saved: {summary_path}")

print("\nT1 complete.")
