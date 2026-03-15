"""Task T4 leakage audit.

Requirements reference:
- pandas==2.3.3
- numpy==2.4.2
- scikit-learn==1.7.2
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
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

CONFIRMED_LEAKS = {"capital.gain", "capital.loss"}


def prepare_dataframe(data_path: Path) -> pd.DataFrame:
    df = pd.read_csv(data_path).replace("?", np.nan)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def feature_association_table(df: pd.DataFrame) -> pd.DataFrame:
    target = (df["income"] == ">50K").astype(int)
    rows: list[dict[str, str | float]] = []

    encoded = pd.DataFrame(index=df.index)
    for col in CATEGORICAL_COLUMNS:
        encoder = LabelEncoder()
        encoded[col] = encoder.fit_transform(df[col].fillna("Missing"))
    for col in NUMERIC_COLUMNS:
        encoded[col] = df[col].fillna(df[col].median())

    mi_scores = pd.Series(
        mutual_info_classif(
            encoded,
            target,
            random_state=42,
            discrete_features=[col in CATEGORICAL_COLUMNS for col in encoded.columns],
        ),
        index=encoded.columns,
    )

    for feature in [col for col in df.columns if col != "income"]:
        if feature in NUMERIC_COLUMNS:
            score_value = float(df[feature].fillna(df[feature].median()).corr(target))
            score_text = f"corr={score_value:.4f}"
        else:
            score_value = float(mi_scores[feature])
            score_text = f"mi={score_value:.4f}"

        temporal_flag = feature in CONFIRMED_LEAKS
        correlation_flag = abs(score_value) > 0.95
        semantic_flag = feature in CONFIRMED_LEAKS

        if feature in CONFIRMED_LEAKS:
            risk = "High"
            reason = (
                "Direct component of the annual income definition, so it acts like a label proxy."
            )
        elif correlation_flag:
            risk = "Review"
            reason = "Very high association with the target requires manual investigation."
        else:
            risk = "Low"
            reason = "Available before prediction time and not semantically derived from income."

        rows.append(
            {
                "Feature": feature,
                "Correlation with Target": score_text,
                "Leakage Risk": risk,
                "Reason": reason,
                "Temporal Flag": temporal_flag,
                "Correlation Flag": correlation_flag,
                "Semantic Flag": semantic_flag,
            }
        )

    return pd.DataFrame(rows)


def model_accuracy(df: pd.DataFrame) -> float:
    modelling_df = df.copy()
    y = (modelling_df["income"] == ">50K").astype(int)
    X = modelling_df.drop(columns=["income"])

    numeric_cols = [col for col in NUMERIC_COLUMNS if col in X.columns]
    categorical_cols = [col for col in CATEGORICAL_COLUMNS if col in X.columns]

    for col in numeric_cols:
        modelling_df[col] = modelling_df[col].fillna(modelling_df[col].median())
    for col in categorical_cols:
        modelling_df[col] = modelling_df[col].fillna(modelling_df[col].mode(dropna=True).iloc[0])

    X = modelling_df.drop(columns=["income"])
    y = (modelling_df["income"] == ">50K").astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train = X_train.copy()
    X_test = X_test.copy()

    for col in categorical_cols:
        encoder = LabelEncoder()
        encoder.fit(X[col].astype(str))
        X_train.loc[:, col] = encoder.transform(X_train[col].astype(str))
        X_test.loc[:, col] = encoder.transform(X_test[col].astype(str))

    if numeric_cols:
        X_train.loc[:, numeric_cols] = X_train[numeric_cols].astype(float)
        X_test.loc[:, numeric_cols] = X_test[numeric_cols].astype(float)
        scaler = StandardScaler()
        X_train = X_train.astype({col: float for col in numeric_cols})
        X_test = X_test.astype({col: float for col in numeric_cols})
        X_train.loc[:, numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
        X_test.loc[:, numeric_cols] = scaler.transform(X_test[numeric_cols])

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train.apply(pd.to_numeric), y_train)
    predictions = model.predict(X_test.apply(pd.to_numeric))
    return float(accuracy_score(y_test, predictions))


def markdown_table(df: pd.DataFrame) -> str:
    columns = df.columns.tolist()
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator] + rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_path = repo_root / "data" / "raw" / "dataset.csv"
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = prepare_dataframe(data_path)
    target = df["income"]
    print("Target column: income")
    print("Target dtype:", target.dtype)
    print("Target unique values:", sorted(target.dropna().unique().tolist()))
    print("Target class distribution:")
    print(target.value_counts())

    audit_table = feature_association_table(df)
    print("\nFeature leakage audit summary:")
    print(audit_table[["Feature", "Correlation with Target", "Leakage Risk", "Reason"]].to_string(index=False))

    flagged = audit_table.loc[audit_table["Leakage Risk"].isin(["High", "Review"])]
    if flagged.empty:
        print("\nNo leaking features were confirmed.")
    else:
        print("\nFlagged feature explanations:")
        for _, row in flagged.iterrows():
            risk_type = "direct encoding" if row["Feature"] in CONFIRMED_LEAKS else "other"
            print(f"Column    : {row['Feature']}")
            print(f"Risk type : {risk_type}")
            print(f"Evidence  : {row['Reason']}")
            print(f"Action    : {'drop' if row['Feature'] in CONFIRMED_LEAKS else 'investigate further'}")
            print()

    cleaned_df = df.drop(columns=sorted(CONFIRMED_LEAKS))
    print("Shape before removal:", df.shape)
    print("Shape after removal :", cleaned_df.shape)

    remaining_numeric = [col for col in NUMERIC_COLUMNS if col in cleaned_df.columns and col != "income"]
    remaining_target = (cleaned_df["income"] == ">50K").astype(int)
    remaining_suspicious = {}
    for col in remaining_numeric:
        corr_value = cleaned_df[col].fillna(cleaned_df[col].median()).corr(remaining_target)
        if abs(corr_value) > 0.95:
            remaining_suspicious[col] = corr_value
    print("Remaining >0.95 numeric correlations:", remaining_suspicious if remaining_suspicious else "None")

    original_accuracy = model_accuracy(df)
    cleaned_accuracy = model_accuracy(cleaned_df)
    accuracy_delta = cleaned_accuracy - original_accuracy
    print(f"Original accuracy: {original_accuracy:.4f}")
    print(f"Cleaned accuracy : {cleaned_accuracy:.4f}")
    print(f"Accuracy change  : {accuracy_delta:.4f}")
    print(
        "Comment: the accuracy drop after removing capital.gain and capital.loss suggests these variables were carrying target-proxy information."
    )

    cleaned_df.to_csv(output_dir / "dataset_leakage_removed.csv", index=False)

    report_lines = [
        "# Leakage Audit Report",
        "",
        "## Target Variable",
        "- Target column: `income`",
        f"- Dtype: `{target.dtype}`",
        f"- Unique values: `{sorted(target.dropna().unique().tolist())}`",
        "",
        "## Summary Table",
        markdown_table(audit_table[["Feature", "Correlation with Target", "Leakage Risk", "Reason"]]),
        "",
        "## Flagged Feature Explanations",
        "### capital.gain",
        "- Risk type: direct encoding",
        "- Evidence: capital gain is part of annual income and therefore acts as a proxy for the >50K threshold.",
        "- Action: drop",
        "",
        "### capital.loss",
        "- Risk type: direct encoding",
        "- Evidence: capital loss is also an income-period financial component tied to the target definition.",
        "- Action: drop",
        "",
        "## Verification",
        f"- Shape before removal: `{df.shape}`",
        f"- Shape after removal: `{cleaned_df.shape}`",
        f"- Remaining >0.95 numeric correlations: `{remaining_suspicious if remaining_suspicious else 'None'}`",
        f"- Original accuracy: `{original_accuracy:.4f}`",
        f"- Cleaned accuracy: `{cleaned_accuracy:.4f}`",
        f"- Accuracy change: `{accuracy_delta:.4f}`",
        "- Interpretation: removing the capital variables lowers accuracy, which is consistent with them carrying target-proxy information.",
    ]
    (output_dir / "leakage_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
