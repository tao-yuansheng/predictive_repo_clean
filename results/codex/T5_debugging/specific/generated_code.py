"""Task T5 debugging report generator.

Requirements reference:
- pandas==2.3.3
- scikit-learn==1.7.2
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


CAT_COLS = [
    "workclass",
    "education",
    "marital.status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native.country",
]


def buggy_equivalent_accuracy(data_path: Path) -> tuple[float, tuple[int, int]]:
    df = pd.read_csv(data_path)
    df = df[df["workclass"] != "?"].copy()

    le = LabelEncoder()
    for col in CAT_COLS:
        df[col] = le.fit_transform(df[col])

    df["income"] = (df["income"].str.strip() == ">50K").astype(int)
    X = df.drop(["income", "fnlwgt"], axis=1)
    y = df["income"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.fit_transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return float(accuracy_score(y_test, y_pred)), df.shape


def fixed_equivalent_accuracy(data_path: Path) -> tuple[float, tuple[int, int]]:
    df = pd.read_csv(data_path)
    df = df[~(df == "?").any(axis=1)].copy()

    encoders: dict[str, LabelEncoder] = {}
    for col in CAT_COLS:
        encoders[col] = LabelEncoder()
        df[col] = encoders[col].fit_transform(df[col])

    df["income"] = (df["income"].str.strip() == ">50K").astype(int)
    X = df.drop(["income", "fnlwgt"], axis=1)
    y = df["income"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return float(accuracy_score(y_test, y_pred)), df.shape


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_path = repo_root / "data" / "raw" / "dataset.csv"
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    buggy_accuracy, buggy_shape = buggy_equivalent_accuracy(data_path)
    fixed_accuracy, fixed_shape = fixed_equivalent_accuracy(data_path)
    accuracy_delta = fixed_accuracy - buggy_accuracy

    report = f"""# Bug Report

## Bug 1
Location : line 15, load data block
Type      : other
Severity  : Major
What it does wrong : Reads `../../data/raw/dataset.csv` relative to the caller's working directory instead of the script location.
Why it matters     : The script can fail immediately with `FileNotFoundError` when launched from a different directory.

## Bug 2
Location : line 22, clean missing values block
Type      : data bug
Severity  : Critical
What it does wrong : Drops rows only when `workclass` is `?`, leaving `occupation` and `native.country` sentinel-missing values in the data.
Why it matters     : The pipeline silently trains on partially uncleaned data and uses more rows than intended (`{buggy_shape}` vs `{fixed_shape}` after the fix).

## Bug 3
Location : lines 29-30 and plot save calls on lines 39, 50, and 58
Type      : silent error
Severity  : Major
What it does wrong : Creates and writes to `output/` relative to the caller's working directory rather than the script directory.
Why it matters     : The script can appear to succeed while saving files into the wrong folder, which breaks reproducibility.

## Bug 4
Location : lines 71-73, categorical encoding block
Type      : logic bug
Severity  : Minor
What it does wrong : Reuses one `LabelEncoder` object across all categorical columns, overwriting its mapping on every iteration.
Why it matters     : Any later inverse transform or saved preprocessing metadata would be wrong because only the final column mapping survives.

## Bug 5
Location : line 94, scaling block
Type      : leakage
Severity  : Critical
What it does wrong : Calls `fit_transform` on the test set instead of applying the scaler fitted on the training data.
Why it matters     : Test-set statistics leak into evaluation, so the reported accuracy is based on an invalid preprocessing pipeline.

## Bug 6
Location : import block, lines 7-8
Type      : other
Severity  : Minor
What it does wrong : Imports Matplotlib without forcing a non-interactive backend or a writable config directory.
Why it matters     : The script can hang or fail in a fresh headless environment before any plots or metrics are produced.

## Severity Notes
- Critical bugs silently produce incorrect data or invalid evaluation.
- Major bugs break portability or save outputs to the wrong place.
- Minor bugs damage preprocessing correctness even if the current script does not crash.

## Before / After Metrics
- Buggy-equivalent accuracy: `{buggy_accuracy:.4f}`
- Fixed-equivalent accuracy: `{fixed_accuracy:.4f}`
- Accuracy change: `{accuracy_delta:.4f}`
- Interpretation: the fixed pipeline is slightly less accurate because it removes all sentinel-missing rows and stops re-fitting the scaler on the test set.

## Silent Bug Detection
- Bug 4 was detected by static inspection: one `LabelEncoder` instance is created once and overwritten in the loop.
- Bug 5 was detected by static inspection: `fit_transform` on `X_test` proves the scaler is being re-fit on evaluation data.
- Bugs 1 and 3 were detected by checking that plain relative paths depend on the process working directory, not the script path.
- Bug 6 was confirmed during verification when the plotting import stalled until a writable headless Matplotlib configuration was supplied.
"""

    (output_dir / "bug_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
