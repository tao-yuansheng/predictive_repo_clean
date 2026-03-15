from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DATA_PATH = Path("predictive_repo_clean/data/raw/dataset.csv")
OUTPUT_DIR = Path("predictive_repo_clean/results/codex/T1_ingestion/vague/output")


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, na_values="?", skipinitialspace=True)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    object_columns = cleaned.select_dtypes(include="object").columns

    for column in object_columns:
        cleaned[column] = cleaned[column].str.strip()

    categorical_columns = cleaned.select_dtypes(include="object").columns.drop("income")
    cleaned[categorical_columns] = cleaned[categorical_columns].fillna("Missing")
    cleaned["income_binary"] = (cleaned["income"] == ">50K").astype(int)

    return cleaned


def build_column_summary(original: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in cleaned.columns:
        rows.append(
            {
                "column": column,
                "dtype": str(cleaned[column].dtype),
                "missing_before_cleaning": int(original[column].isna().sum()) if column in original.columns else 0,
                "missing_after_cleaning": int(cleaned[column].isna().sum()),
                "unique_values": int(cleaned[column].nunique(dropna=False)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    original = load_dataset(DATA_PATH)
    cleaned = clean_dataset(original)

    missing_summary = pd.DataFrame(
        {
            "column": original.columns,
            "missing_count_before_cleaning": original.isna().sum().values,
            "missing_pct_before_cleaning": (original.isna().mean().values * 100).round(2),
            "missing_count_after_cleaning": [int(cleaned[column].isna().sum()) for column in original.columns],
            "missing_pct_after_cleaning": [
                round(cleaned[column].isna().mean() * 100, 2) for column in original.columns
            ],
        }
    )

    column_summary = build_column_summary(original, cleaned)

    cleaned.to_csv(OUTPUT_DIR / "cleaned_dataset.csv", index=False)
    missing_summary.to_csv(OUTPUT_DIR / "missing_values_summary.csv", index=False)
    column_summary.to_csv(OUTPUT_DIR / "column_summary.csv", index=False)

    report = {
        "rows": int(cleaned.shape[0]),
        "columns": int(cleaned.shape[1]),
        "original_missing_total": int(original.isna().sum().sum()),
        "remaining_missing_total": int(cleaned.isna().sum().sum()),
        "categorical_missing_strategy": "Filled categorical missing values with 'Missing'.",
        "target_encoding": "Added income_binary where >50K=1 and <=50K=0.",
        "files_written": [
            "cleaned_dataset.csv",
            "missing_values_summary.csv",
            "column_summary.csv",
        ],
    }
    (OUTPUT_DIR / "ingestion_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
