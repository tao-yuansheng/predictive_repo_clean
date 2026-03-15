from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RAW_DATA_PATH = Path("predictive_repo_clean/data/raw/dataset.csv")
CLEAN_DATA_PATH = Path("predictive_repo_clean/results/codex/T1_ingestion/vague/output/dataset_clean.csv")
OUTPUT_DIR = Path("predictive_repo_clean/results/codex/T3_model/vague/output")


def load_dataset() -> pd.DataFrame:
    data_path = CLEAN_DATA_PATH if CLEAN_DATA_PATH.exists() else RAW_DATA_PATH
    df = pd.read_csv(data_path, na_values="?", skipinitialspace=True)
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()
    return df


def build_pipeline(df: pd.DataFrame) -> tuple[Pipeline, list[str], list[str]]:
    target = "income"
    feature_columns = [column for column in df.columns if column != target]
    X = df[feature_columns]

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include="object").columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
    return pipeline, numeric_features, categorical_features


def save_plots(y_test: pd.Series, y_pred: pd.Series, y_prob: pd.Series) -> None:
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["<=50K", ">50K"])
    disp.plot(cmap="Blues")
    plt.title("Baseline Model Confusion Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=200)
    plt.close()

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plt.figure(figsize=(6, 6))
    plt.plot(fpr, tpr, label="Logistic regression")
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=200)
    plt.close()


def save_feature_importance(pipeline: Pipeline, numeric_features: list[str], categorical_features: list[str]) -> None:
    preprocessor = pipeline.named_steps["preprocessor"]
    onehot = preprocessor.named_transformers_["categorical"].named_steps["onehot"]
    feature_names = numeric_features + onehot.get_feature_names_out(categorical_features).tolist()
    coefficients = pipeline.named_steps["model"].coef_[0]
    feature_importance = (
        pd.DataFrame({"feature": feature_names, "coefficient": coefficients})
        .assign(abs_coefficient=lambda df: df["coefficient"].abs())
        .sort_values("abs_coefficient", ascending=False)
    )
    feature_importance.to_csv(OUTPUT_DIR / "feature_coefficients.csv", index=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    df["income_binary"] = (df["income"] == ">50K").astype(int)

    X = df.drop(columns=["income", "income_binary"])
    y = df["income_binary"]

    pipeline, numeric_features, categorical_features = build_pipeline(df.drop(columns=["income_binary"]))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
    }

    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))

    report = classification_report(y_test, y_pred, target_names=["<=50K", ">50K"], output_dict=True)
    pd.DataFrame(report).T.to_csv(OUTPUT_DIR / "classification_report.csv")

    prediction_sample = X_test.copy()
    prediction_sample["actual"] = y_test.values
    prediction_sample["predicted"] = y_pred
    prediction_sample["predicted_probability"] = y_prob
    prediction_sample.head(200).to_csv(OUTPUT_DIR / "prediction_sample.csv", index=False)

    save_plots(y_test, y_pred, y_prob)
    save_feature_importance(pipeline, numeric_features, categorical_features)

    summary_lines = [
        "# Baseline Model Results",
        "",
        "Model: Logistic regression with median imputation, scaling, one-hot encoding, and balanced class weights.",
        f"Accuracy: {metrics['accuracy']:.4f}",
        f"Precision: {metrics['precision']:.4f}",
        f"Recall: {metrics['recall']:.4f}",
        f"F1: {metrics['f1']:.4f}",
        f"ROC AUC: {metrics['roc_auc']:.4f}",
    ]
    (OUTPUT_DIR / "model_summary.md").write_text("\n".join(summary_lines))


if __name__ == "__main__":
    main()
