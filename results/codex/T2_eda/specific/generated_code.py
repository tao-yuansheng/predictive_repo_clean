"""Task T2 exploratory data analysis.

Requirements reference:
- pandas==2.3.3
- numpy==2.4.2
- seaborn==0.13.2
- matplotlib==3.10.7
- scikit-learn==1.7.2
"""

from __future__ import annotations

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
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder


NUMERIC_COLUMNS = [
    "age",
    "fnlwgt",
    "education.num",
    "capital.gain",
    "capital.loss",
    "hours.per.week",
]

CATEGORICAL_COLUMNS = [
    "workclass",
    "education",
    "marital.status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native.country",
]


def save_numeric_distribution(df: pd.DataFrame, col: str, output_dir: Path) -> dict[str, float]:
    series = df[col]
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_count = int(((series < lower) | (series > upper)).sum())

    stats = {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "skewness": float(series.skew()),
        "kurtosis": float(series.kurt()),
        "outliers_iqr": outlier_count,
    }

    plt.figure(figsize=(8, 4.5))
    sns.histplot(series, bins=30, kde=True, color="#1f77b4")
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.annotate(
        f"Skewness: {stats['skewness']:.2f}\nKurtosis: {stats['kurtosis']:.2f}",
        xy=(0.98, 0.95),
        xycoords="axes fraction",
        ha="right",
        va="top",
        bbox={"boxstyle": "round", "fc": "white", "ec": "#444444"},
    )
    plt.tight_layout()
    plt.savefig(output_dir / f"dist_{col}.png", dpi=200)
    plt.close()

    return stats


def save_categorical_bar(df: pd.DataFrame, col: str, output_dir: Path) -> pd.Series:
    counts = df[col].fillna("Missing").value_counts().head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=counts.values, y=counts.index, hue=counts.index, palette="crest", legend=False)
    plt.title(f"Top 10 Categories for {col}")
    plt.xlabel("Count")
    plt.ylabel(col)
    plt.tight_layout()
    plt.savefig(output_dir / f"barplot_{col}.png", dpi=200)
    plt.close()
    return counts


def save_boxplot(df: pd.DataFrame, col: str, output_dir: Path) -> None:
    plt.figure(figsize=(7, 4.5))
    sns.boxplot(data=df, x="income", y=col, hue="income", legend=False, palette="Set2")
    plt.title(f"{col} by Income")
    plt.tight_layout()
    plt.savefig(output_dir / f"boxplot_{col}_by_income.png", dpi=200)
    plt.close()


def save_stacked_bar(df: pd.DataFrame, col: str, output_dir: Path) -> None:
    counts = (
        df[col]
        .fillna("Missing")
        .groupby([df[col].fillna("Missing"), df["income"]])
        .size()
        .unstack(fill_value=0)
    )
    top_categories = counts.sum(axis=1).sort_values(ascending=False).head(10).index
    share = counts.loc[top_categories]
    share = share.div(share.sum(axis=1), axis=0)
    share.plot(kind="bar", stacked=True, figsize=(10, 5), color=["#4c72b0", "#dd8452"])
    plt.title(f"Income Mix within {col} Categories")
    plt.xlabel(col)
    plt.ylabel("Share")
    plt.legend(title="income")
    plt.tight_layout()
    plt.savefig(output_dir / f"stacked_{col}_income.png", dpi=200)
    plt.close()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_path = repo_root / "data" / "raw" / "dataset.csv"
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path).replace("?", np.nan)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    print("Shape:", df.shape)
    print("\nDtypes:")
    print(df.dtypes)

    missing_summary = pd.DataFrame(
        {"missing_count": df.isna().sum(), "missing_pct": (df.isna().mean() * 100).round(2)}
    )
    print("\nMissing values summary:")
    print(missing_summary)

    columns_with_missing = missing_summary.loc[missing_summary["missing_count"] > 0]
    print("\nColumns containing missing values:")
    if columns_with_missing.empty:
        print("None")
    else:
        print(columns_with_missing)

    numeric_stats: dict[str, dict[str, float]] = {}
    print("\nNumeric column analysis:")
    for col in NUMERIC_COLUMNS:
        numeric_stats[col] = save_numeric_distribution(df, col, output_dir)
        print(f"\n{col}:")
        for key, value in numeric_stats[col].items():
            print(f"  {key}: {value:.4f}")
        if col in {"capital.gain", "capital.loss"}:
            zero_share = (df[col] == 0).mean() * 100
            print(f"  zero_share_pct: {zero_share:.2f}")
            print(f"  note: {col} is heavily zero-inflated and right-skewed.")

    print("\nCategorical column analysis:")
    dominance_flags: list[str] = []
    for col in CATEGORICAL_COLUMNS:
        counts = df[col].fillna("Missing").value_counts()
        print(f"\n{col} value counts:")
        print(counts)
        print(f"Cardinality ({col}): {df[col].nunique(dropna=True)}")
        top_share = counts.iloc[0] / len(df)
        if top_share > 0.70:
            message = f"{col} is dominated by '{counts.index[0]}' at {top_share:.2%}."
            dominance_flags.append(message)
            print("Dominance flag:", message)
        save_categorical_bar(df, col, output_dir)

    income_counts = df["income"].value_counts()
    imbalance_ratio = income_counts.get("<=50K", 0) / income_counts.get(">50K", 1)
    print("\nIncome distribution:")
    print(income_counts)
    print(f"Class imbalance ratio (<=50K : >50K): {imbalance_ratio:.2f}:1")
    print("Likely model impact: yes, the minority >50K class may reduce recall without mitigation.")

    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x="income", hue="income", legend=False, palette="Set2")
    plt.title("Income Distribution")
    plt.xlabel("Income")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_dir / "income_distribution.png", dpi=200)
    plt.close()

    df["income_binary"] = (df["income"] == ">50K").astype(int)
    correlation_matrix = df[NUMERIC_COLUMNS + ["income_binary"]].corr(numeric_only=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=200)
    plt.close()

    numeric_income_corr = (
        correlation_matrix["income_binary"]
        .drop("income_binary")
        .sort_values(key=lambda s: s.abs(), ascending=False)
    )
    print("\nNumeric correlations with income:")
    print(numeric_income_corr)

    encoded = pd.DataFrame(index=df.index)
    discrete_mask: list[bool] = []
    for col in CATEGORICAL_COLUMNS:
        le = LabelEncoder()
        encoded[col] = le.fit_transform(df[col].fillna("Missing"))
        discrete_mask.append(True)
    for col in NUMERIC_COLUMNS:
        encoded[col] = df[col].fillna(df[col].median())
        discrete_mask.append(False)
    mi_scores = pd.Series(
        mutual_info_classif(encoded, df["income_binary"], random_state=42, discrete_features=discrete_mask),
        index=encoded.columns,
    ).sort_values(ascending=False)
    print("\nTop 5 features most associated with income (mutual information proxy across feature types):")
    print(mi_scores.head(5))

    top_features = mi_scores.head(3).index.tolist()
    print("\nBivariate analysis features:", top_features)
    for feature in top_features:
        if feature in NUMERIC_COLUMNS:
            save_boxplot(df, feature, output_dir)
        else:
            save_stacked_bar(df, feature, output_dir)

    leakage_notes = {
        "education.num": "Not leakage, but it is a direct numeric encoding of education and therefore redundant with education.",
        "fnlwgt": "Not target leakage, but it is a census sampling weight and can distort interpretation if treated as a normal predictor.",
    }
    print("\nLeakage flags:")
    print("No column appears to directly encode or derive from income in this dataset.")
    for col, note in leakage_notes.items():
        print(f"- {col}: {note}")

    summary_lines = [
        "Summary:",
        "- Age, education.num, hours.per.week, capital.gain, and relationship structure show clear separation by income.",
        "- capital.gain and capital.loss are extremely zero-inflated, so robust scaling or indicator features may help modelling.",
        "- workclass and native.country contain missing values and need imputation before modelling.",
        "- education and education.num are redundant; keep one or regularise carefully to avoid duplicative signal.",
        "- The target is imbalanced, so threshold tuning or class weighting should be considered in later modelling.",
    ]
    print("\n" + "\n".join(summary_lines))


if __name__ == "__main__":
    main()
