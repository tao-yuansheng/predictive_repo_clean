"""Task T3 baseline model training.

Requirements reference:
- pandas==2.3.3
- numpy==2.4.2
- scikit-learn==1.7.2
- matplotlib==3.10.7
- seaborn==0.13.2
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


np.random.seed(42)

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


def load_input_data(repo_root: Path) -> tuple[pd.DataFrame, str]:
    preferred = repo_root / "results" / "codex" / "T1_ingestion" / "specific" / "output" / "dataset_clean.csv"
    fallback = repo_root / "data" / "raw" / "dataset.csv"
    if preferred.exists():
        df = pd.read_csv(preferred)
        source = str(preferred)
    else:
        df = pd.read_csv(fallback).replace("?", np.nan)
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()
        df = df.drop_duplicates().reset_index(drop=True)
        for col in NUMERIC_COLUMNS:
            df[col] = df[col].fillna(df[col].median())
        for col in CATEGORICAL_COLUMNS + ["income"]:
            df[col] = df[col].fillna(df[col].mode(dropna=True).iloc[0])
        source = str(fallback)
    return df, source


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    df, input_source = load_input_data(repo_root)
    print("Loaded input from:", input_source)
    print("Dataset shape:", df.shape)

    if "income" not in df.columns:
        raise ValueError("Target column 'income' is missing.")

    df["income"] = df["income"].astype(str).str.strip()
    unique_target_values = sorted(df["income"].dropna().unique().tolist())
    print("Target unique values:", unique_target_values)
    if set(unique_target_values) != {"<=50K", ">50K"}:
        raise ValueError(f"Unexpected target labels: {unique_target_values}")

    y = (df["income"] == ">50K").astype(int)
    print("Binary target confirmed with counts:")
    print(y.value_counts().sort_index())

    X = df.drop(columns=["income"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train = X_train.copy()
    X_test = X_test.copy()

    encoders: dict[str, LabelEncoder] = {}
    for col in CATEGORICAL_COLUMNS:
        encoder = LabelEncoder()
        encoder.fit(X[col].astype(str))
        X_train.loc[:, col] = encoder.transform(X_train[col].astype(str))
        X_test.loc[:, col] = encoder.transform(X_test[col].astype(str))
        encoders[col] = encoder

    scaler = StandardScaler()
    X_train.loc[:, NUMERIC_COLUMNS] = X_train[NUMERIC_COLUMNS].astype(float)
    X_test.loc[:, NUMERIC_COLUMNS] = X_test[NUMERIC_COLUMNS].astype(float)
    scaled_train = scaler.fit_transform(X_train[NUMERIC_COLUMNS])
    scaled_test = scaler.transform(X_test[NUMERIC_COLUMNS])
    X_train = X_train.astype({col: float for col in NUMERIC_COLUMNS})
    X_test = X_test.astype({col: float for col in NUMERIC_COLUMNS})
    X_train.loc[:, NUMERIC_COLUMNS] = scaled_train
    X_test.loc[:, NUMERIC_COLUMNS] = scaled_test
    X_train = X_train.apply(pd.to_numeric)
    X_test = X_test.apply(pd.to_numeric)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
    }

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print("Metrics:")
    print(json.dumps(metrics, indent=2))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(output_dir / "confusion_matrix.png", dpi=200)
    plt.close()

    with open(output_dir / "task3_results.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    joblib.dump(
        {
            "model": model,
            "scaler": scaler,
            "encoders": encoders,
            "feature_columns": X.columns.tolist(),
            "numeric_columns": NUMERIC_COLUMNS,
            "categorical_columns": CATEGORICAL_COLUMNS,
        },
        output_dir / "baseline_model.pkl",
    )

    requirements_text = "\n".join(
        [
            f"pandas=={pd.__version__}",
            f"numpy=={np.__version__}",
            f"scikit-learn=={sklearn.__version__}",
            f"matplotlib=={matplotlib.__version__}",
            f"seaborn=={sns.__version__}",
        ]
    )
    (output_dir / "requirements_task3.txt").write_text(requirements_text + "\n", encoding="utf-8")

    shutil.copyfile(Path(__file__), output_dir / "task3_baseline.py")
    print("\nSaved outputs to:", output_dir)


if __name__ == "__main__":
    main()
