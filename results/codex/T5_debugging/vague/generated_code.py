from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[4]
DATA_PATH = ROOT_DIR / "data/raw/dataset.csv"
OUTPUT_DIR = ROOT_DIR / "results/codex/T5_debugging/vague/output"


def load_and_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, na_values="?", skipinitialspace=True)
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    df = df.dropna().copy()
    return df


def save_plots(df: pd.DataFrame) -> None:
    plt.figure(figsize=(6, 4))
    df["income"].value_counts().plot(kind="bar", color=["steelblue", "coral"])
    plt.title("Income Distribution")
    plt.xlabel("Income")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "income_distribution.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 4))
    for label, group in df.groupby("income"):
        group["age"].hist(alpha=0.6, bins=25, label=label)
    plt.title("Age Distribution by Income")
    plt.xlabel("Age")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "age_by_income.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7, 4))
    sns.boxplot(x="income", y="hours.per.week", data=df)
    plt.title("Hours per Week by Income")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hours_by_income.png", dpi=200)
    plt.close()


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    encoded = df.copy()
    cat_cols = [
        "workclass",
        "education",
        "marital.status",
        "occupation",
        "relationship",
        "race",
        "sex",
        "native.country",
    ]

    encoders: dict[str, LabelEncoder] = {}
    for column in cat_cols:
        encoder = LabelEncoder()
        encoded[column] = encoder.fit_transform(encoded[column])
        encoders[column] = encoder

    encoded["income"] = (encoded["income"] == ">50K").astype(int)
    return encoded


def train_and_evaluate(df: pd.DataFrame) -> tuple[dict[str, float | int], pd.DataFrame]:
    X = df.drop(columns=["income", "fnlwgt"])
    y = df["income"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    report = pd.DataFrame(classification_report(y_test, y_pred, output_dict=True)).T
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "rows_after_cleaning": int(df.shape[0]),
    }
    return metrics, report


def write_debug_summary(metrics: dict[str, float | int]) -> None:
    summary = f"""# Debugging Summary

Fixed issues:
- Replaced `?` markers across the dataset by reading them as missing values and dropping incomplete rows.
- Standardized whitespace in string columns before encoding the target.
- Used a separate `LabelEncoder` per categorical column.
- Prevented test-set leakage by applying `scaler.transform(X_test)` instead of refitting on test data.
- Made file paths robust and saved outputs to the required task folder.

Results:
- Rows after cleaning: {metrics['rows_after_cleaning']}
- Train rows: {metrics['train_rows']}
- Test rows: {metrics['test_rows']}
- Accuracy: {metrics['accuracy']:.4f}
"""
    (OUTPUT_DIR / "debug_summary.md").write_text(summary)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_and_clean_data()
    save_plots(df)
    encoded_df = encode_features(df)
    metrics, report = train_and_evaluate(encoded_df)

    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    report.to_csv(OUTPUT_DIR / "classification_report.csv")
    write_debug_summary(metrics)


if __name__ == "__main__":
    main()
