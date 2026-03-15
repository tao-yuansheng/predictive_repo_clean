"""Task T1 ingestion and cleaning.

Requirements reference:
- pandas==2.3.3
- numpy==2.4.2
- seaborn==0.13.2
- matplotlib==3.10.7
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


np.random.seed(42)

EXPECTED_COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education.num",
    "marital.status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital.gain",
    "capital.loss",
    "hours.per.week",
    "native.country",
    "income",
]

NUMERIC_COLUMNS = [
    "age",
    "fnlwgt",
    "education.num",
    "capital.gain",
    "capital.loss",
    "hours.per.week",
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_path = repo_root / "data" / "raw" / "dataset.csv"
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    original_row_count = len(df)
    df = df.replace("?", np.nan)
    object_cols = df.select_dtypes(include="object").columns.tolist()
    for col in object_cols:
        df[col] = df[col].str.strip()

    print("Initial shape:", df.shape)
    print("First 5 rows:")
    print(df.head())

    print("\nColumn dtypes:")
    print(df.dtypes)

    mistyped_columns = [
        col
        for col in NUMERIC_COLUMNS
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])
    ]
    print("\nPotentially mis-typed columns:", mistyped_columns if mistyped_columns else "None")

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")
    print("\nSchema validation passed. All expected columns are present.")

    categorical_cols = [col for col in df.columns if df[col].dtype == "object" and col != "income"]
    print("\nCategorical cardinalities:")
    for col in categorical_cols + ["income"]:
        print(f"{col}: {df[col].nunique(dropna=True)}")

    missing_counts = df.isna().sum()
    missing_pct = df.isna().mean().mul(100).round(2)
    missing_summary = pd.DataFrame(
        {"missing_count": missing_counts, "missing_pct": missing_pct}
    ).sort_values(["missing_count", "missing_pct"], ascending=False)
    print("\nMissingness summary:")
    print(missing_summary)

    plt.figure(figsize=(12, 5))
    sns.heatmap(df.isna(), cbar=False, yticklabels=False, cmap=["#f7f7f7", "#b22222"])
    plt.title("Missingness Heatmap")
    plt.tight_layout()
    heatmap_path = output_dir / "missingness_heatmap.png"
    plt.savefig(heatmap_path, dpi=200)
    plt.close()

    drop_columns: list[str] = []
    manual_review_columns: list[str] = []
    imputed_columns: list[str] = []
    for col in df.columns:
        pct_missing = df[col].isna().mean() * 100
        if pct_missing > 50:
            drop_columns.append(col)
        elif 20 <= pct_missing <= 50:
            manual_review_columns.append(col)
        elif 0 < pct_missing < 20:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numeric columns under 20% missing are median-imputed for robust handling.
                fill_value = df[col].median()
            else:
                # Categorical columns under 20% missing are mode-imputed to preserve common class labels.
                fill_value = df[col].mode(dropna=True).iloc[0]
            df[col] = df[col].fillna(fill_value)
            imputed_columns.append(col)

    if drop_columns:
        df = df.drop(columns=drop_columns)

    rows_before_dedup = len(df)
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    rows_after_dedup = len(df)
    print(f"\nDuplicate rows removed: {duplicate_count}")
    print(f"Rows before deduplication: {rows_before_dedup}, after deduplication: {rows_after_dedup}")

    outlier_caps: dict[str, int] = {}
    for col in NUMERIC_COLUMNS:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        outlier_caps[col] = int(mask.sum())
        df[col] = df[col].clip(lower=lower, upper=upper)

    dataset_path = output_dir / "dataset_clean.csv"
    df.to_csv(dataset_path, index=False)

    cleaning_report = {
        "rows_before_cleaning": int(original_row_count),
        "rows_after_cleaning": int(len(df)),
        "columns_dropped": drop_columns,
        "columns_manual_review": manual_review_columns,
        "columns_imputed": imputed_columns,
        "duplicate_rows_removed": duplicate_count,
        "outliers_capped": outlier_caps,
        "output_dataset": str(dataset_path),
        "output_heatmap": str(heatmap_path),
    }
    print("\nFinal cleaning report:")
    print(json.dumps(cleaning_report, indent=2))


if __name__ == "__main__":
    main()
