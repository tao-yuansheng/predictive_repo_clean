"""
T1 — Data Ingestion, Missingness Audit, and Wrangling
Agent: claude_code
Prompt type: specific

# Requirements:
# pandas==2.2.x, numpy==1.26.x, matplotlib==3.8.x, seaborn==0.13.x
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

np.random.seed(42)

RAW_PATH = "data/raw/dataset.csv"
OUT_DIR = "results/claude_code/T1_ingestion/specific/output"
os.makedirs(OUT_DIR, exist_ok=True)

EXPECTED_COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education.num",
    "marital.status", "occupation", "relationship", "race", "sex",
    "capital.gain", "capital.loss", "hours.per.week", "native.country", "income"
]

# ── 1. Data Ingestion ──────────────────────────────────────────────────────────
df = pd.read_csv(RAW_PATH)
print("=" * 60)
print("1. DATA INGESTION")
print("=" * 60)
print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"\nFirst 5 rows:\n{df.head()}")

# Replace "?" with NaN before any audit
df.replace("?", np.nan, inplace=True)
print("\nReplaced '?' with NaN across all columns.")

# Report dtypes and flag mis-typed columns
print(f"\nColumn dtypes:")
for col in df.columns:
    flag = ""
    if df[col].dtype == object:
        try:
            non_null = df[col].dropna()
            pd.to_numeric(non_null)
            flag = "  <- POSSIBLE NUMERIC STORED AS OBJECT"
        except (ValueError, TypeError):
            pass
    print(f"  {col:20s}: {str(df[col].dtype):10s}{flag}")

# ── 2. Schema Validation ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. SCHEMA VALIDATION")
print("=" * 60)
missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
if missing_cols:
    raise ValueError(f"SCHEMA ERROR - missing expected columns: {missing_cols}")
print("All 15 expected columns present. OK")

cat_cols = df.select_dtypes(include="object").columns.tolist()
print(f"\nCardinality (nunique) of categorical columns:")
for col in cat_cols:
    print(f"  {col:20s}: {df[col].nunique()} unique values")

# ── 3. Missingness Audit ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. MISSINGNESS AUDIT")
print("=" * 60)
miss_count = df.isnull().sum()
miss_pct = (miss_count / len(df) * 100).round(2)
miss_df = pd.DataFrame({"missing_count": miss_count, "missing_pct": miss_pct})
miss_df_nonzero = miss_df[miss_df["missing_count"] > 0]
print(f"Columns with missing values:\n{miss_df_nonzero}")

# Categorise and impute
drop_cols = []
flag_review = []
imputed_cols = []

for col in df.columns:
    pct = miss_pct[col]
    if pct > 50:
        # Drop - too much missing data
        drop_cols.append(col)
        print(f"  DROP    '{col}': {pct:.1f}% missing (>50%)")
    elif pct >= 20:
        # Flag for manual review
        flag_review.append(col)
        print(f"  FLAG    '{col}': {pct:.1f}% missing (20-50%) - manual review recommended")
    elif pct > 0:
        # Impute based on dtype
        if df[col].dtype in [np.float64, np.int64]:
            # Numeric -> median imputation
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            imputed_cols.append(col)
            print(f"  IMPUTE  '{col}': {pct:.1f}% missing -> median={median_val:.2f}")
        else:
            # Categorical -> mode imputation
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            imputed_cols.append(col)
            print(f"  IMPUTE  '{col}': {pct:.1f}% missing -> mode='{mode_val}'")

if drop_cols:
    df.drop(columns=drop_cols, inplace=True)
    print(f"\nDropped columns: {drop_cols}")
else:
    print("\nNo columns dropped (none exceeded 50% missing threshold).")

# Missingness heatmap (seaborn-based)
raw_for_heatmap = pd.read_csv(RAW_PATH)
raw_for_heatmap.replace("?", np.nan, inplace=True)
miss_matrix = raw_for_heatmap.isnull().astype(int)

fig, ax = plt.subplots(figsize=(14, 4))
sns.heatmap(
    miss_matrix.T,
    cbar=False, cmap=["#e8e8e8", "#d73027"],
    yticklabels=raw_for_heatmap.columns,
    xticklabels=False, ax=ax
)
ax.set_title("Missingness Heatmap (red = missing)", fontsize=13)
ax.set_xlabel("Rows")
ax.set_ylabel("Columns")
plt.tight_layout()
heatmap_path = os.path.join(OUT_DIR, "missingness_heatmap.png")
plt.savefig(heatmap_path, dpi=150)
plt.close()
print(f"\nSaved missingness heatmap: {heatmap_path}")

# ── 4. Data Cleaning ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. DATA CLEANING")
print("=" * 60)
rows_before = len(df)

# Remove exact duplicate rows
df = df.drop_duplicates()
rows_after_dedup = len(df)
print(f"Duplicate rows removed: {rows_before - rows_after_dedup}")

# Strip leading/trailing whitespace from string columns (preserve casing)
str_cols = df.select_dtypes(include="object").columns
df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())
print("Stripped whitespace from all string columns (casing preserved).")

# Detect and cap outliers in numeric columns using IQR (1.5x rule)
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
outlier_counts = {}
for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    n_lower = int((df[col] < lower).sum())
    n_upper = int((df[col] > upper).sum())
    total_capped = n_lower + n_upper
    outlier_counts[col] = total_capped
    df[col] = df[col].clip(lower=lower, upper=upper)
    if total_capped > 0:
        print(f"  Outliers capped in '{col}': {total_capped} values "
              f"(lower={lower:.2f}, upper={upper:.2f})")

# ── 5. Output & Reproducibility ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. OUTPUT")
print("=" * 60)

clean_path = os.path.join(OUT_DIR, "dataset_clean.csv")
df.to_csv(clean_path, index=False)
print(f"Saved cleaned dataset: {clean_path}")

print("\n-- CLEANING REPORT -----------------------------------------------")
print(f"  Rows before cleaning : {rows_before}")
print(f"  Rows after dedup     : {rows_after_dedup}")
print(f"  Final row count      : {len(df)}")
print(f"  Columns dropped      : {drop_cols if drop_cols else 'none'}")
print(f"  Columns for review   : {flag_review if flag_review else 'none'}")
print(f"  Columns imputed      : {imputed_cols}")
for col, cnt in outlier_counts.items():
    if cnt > 0:
        print(f"  Outliers capped [{col}]: {cnt}")
print("------------------------------------------------------------------")
print("T1 specific complete.")
