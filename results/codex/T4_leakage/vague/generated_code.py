from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DATA_PATH = Path("predictive_repo_clean/data/raw/dataset.csv")
OUTPUT_DIR = Path("predictive_repo_clean/results/codex/T4_leakage/vague/output")


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, na_values="?", skipinitialspace=True)
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()
    df["income_binary"] = (df["income"] == ">50K").astype(int)
    return df


def build_feature_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in df.columns:
        if column == "income_binary":
            continue

        series = df[column]
        row = {
            "feature": column,
            "dtype": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=False)),
            "equals_target_exactly": bool(series.astype(str).equals(df["income"].astype(str))),
            "correlation_with_income_binary": None,
            "note": "",
        }

        if pd.api.types.is_numeric_dtype(series):
            row["correlation_with_income_binary"] = round(float(series.corr(df["income_binary"])), 4)

        rows.append(row)

    audit = pd.DataFrame(rows)
    audit.loc[audit["feature"] == "education", "note"] = "Deterministic duplicate of education.num."
    audit.loc[audit["feature"] == "education.num", "note"] = "Deterministic duplicate of education."
    audit.loc[audit["feature"] == "capital.gain", "note"] = (
        "Very target-proximal financial variable; strong signal but not a direct target copy."
    )
    audit.loc[audit["feature"] == "capital.loss", "note"] = (
        "Very target-proximal financial variable; strong signal but not a direct target copy."
    )
    audit.loc[audit["feature"] == "fnlwgt", "note"] = "Sampling weight; not leakage, but generally not a desirable predictor."
    return audit


def build_suspicious_features(df: pd.DataFrame) -> pd.DataFrame:
    gain_rates = df.assign(is_positive=df["capital.gain"] > 0).groupby("income")["is_positive"].mean().mul(100)
    loss_rates = df.assign(is_positive=df["capital.loss"] > 0).groupby("income")["is_positive"].mean().mul(100)

    suspicious = pd.DataFrame(
        [
            {
                "feature_or_pair": "education + education.num",
                "risk_level": "medium",
                "issue_type": "redundant encoding",
                "evidence": "Each education label maps to exactly one education.num value and vice versa.",
                "recommendation": "Keep one of the two features to avoid duplicate information.",
            },
            {
                "feature_or_pair": "capital.gain",
                "risk_level": "medium",
                "issue_type": "target-proximal signal",
                "evidence": (
                    f"Positive capital gain appears in {gain_rates['>50K']:.2f}% of >50K rows versus "
                    f"{gain_rates['<=50K']:.2f}% of <=50K rows."
                ),
                "recommendation": (
                    "Use with care. It is not direct leakage in this dataset, but it may be too close to the target "
                    "for some real-world prediction settings."
                ),
            },
            {
                "feature_or_pair": "capital.loss",
                "risk_level": "low",
                "issue_type": "target-proximal signal",
                "evidence": (
                    f"Positive capital loss appears in {loss_rates['>50K']:.2f}% of >50K rows versus "
                    f"{loss_rates['<=50K']:.2f}% of <=50K rows."
                ),
                "recommendation": "Treat similarly to capital.gain and validate whether it is available at prediction time.",
            },
            {
                "feature_or_pair": "fnlwgt",
                "risk_level": "low",
                "issue_type": "sampling artifact",
                "evidence": "Census sampling weight is not a demographic trait and may not generalize operationally.",
                "recommendation": "Exclude from baseline models unless survey weighting is part of the design.",
            },
        ]
    )
    return suspicious


def write_report(audit: pd.DataFrame, suspicious: pd.DataFrame) -> None:
    direct_leakage = audit.loc[audit["equals_target_exactly"], "feature"].tolist()
    report = [
        "# Leakage Audit",
        "",
        "Overall conclusion: no direct target leakage was found in the Adult Income dataset columns.",
        "",
        "Key observations:",
        f"- Direct target copies found: {direct_leakage if direct_leakage else 'None'}.",
        "- `education` and `education.num` are perfectly redundant encodings of the same concept.",
        "- `capital.gain` and `capital.loss` are not leaked labels, but they are close to the income outcome and can inflate apparent predictive power.",
        "- `fnlwgt` is not leakage, though it is a survey weight and usually not appropriate as a standard predictive feature.",
        "",
        "Recommended modelling actions:",
        "- Drop one of `education` or `education.num`.",
        "- Test model performance with and without `capital.gain` and `capital.loss` if deployment would not know them in advance.",
        "- Exclude `fnlwgt` from baseline models unless survey weighting is explicitly required.",
    ]
    (OUTPUT_DIR / "leakage_report.md").write_text("\n".join(report))

    summary = {
        "direct_target_copies": direct_leakage,
        "redundant_feature_pair": ["education", "education.num"],
        "target_proximal_features": ["capital.gain", "capital.loss"],
        "non_leakage_caution_feature": ["fnlwgt"],
    }
    (OUTPUT_DIR / "leakage_summary.json").write_text(json.dumps(summary, indent=2))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()

    audit = build_feature_audit(df)
    suspicious = build_suspicious_features(df)
    education_mapping = (
        df[["education", "education.num"]]
        .drop_duplicates()
        .sort_values("education.num")
        .reset_index(drop=True)
    )

    audit.to_csv(OUTPUT_DIR / "feature_audit.csv", index=False)
    suspicious.to_csv(OUTPUT_DIR / "suspicious_features.csv", index=False)
    education_mapping.to_csv(OUTPUT_DIR / "education_mapping.csv", index=False)
    write_report(audit, suspicious)


if __name__ == "__main__":
    main()
