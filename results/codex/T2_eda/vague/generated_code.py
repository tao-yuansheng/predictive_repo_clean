from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DATA_PATH = Path("predictive_repo_clean/data/raw/dataset.csv")
OUTPUT_DIR = Path("predictive_repo_clean/results/codex/T2_eda/vague/output")


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, na_values="?", skipinitialspace=True)
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()
    df["income_binary"] = (df["income"] == ">50K").astype(int)
    return df


def save_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    numeric_summary = df.describe().T.reset_index().rename(columns={"index": "column"})
    categorical_columns = [
        "workclass",
        "education",
        "marital.status",
        "occupation",
        "relationship",
        "race",
        "sex",
        "native.country",
        "income",
    ]
    categorical_summary = []
    for column in categorical_columns:
        top_counts = df[column].fillna("Missing").value_counts(dropna=False).head(5)
        categorical_summary.append(
            {
                "column": column,
                "missing_count": int(df[column].isna().sum()),
                "unique_values": int(df[column].nunique(dropna=True)),
                "top_1": top_counts.index[0] if len(top_counts) > 0 else None,
                "top_1_count": int(top_counts.iloc[0]) if len(top_counts) > 0 else 0,
                "top_2": top_counts.index[1] if len(top_counts) > 1 else None,
                "top_2_count": int(top_counts.iloc[1]) if len(top_counts) > 1 else 0,
                "top_3": top_counts.index[2] if len(top_counts) > 2 else None,
                "top_3_count": int(top_counts.iloc[2]) if len(top_counts) > 2 else 0,
            }
        )
    categorical_summary_df = pd.DataFrame(categorical_summary)

    sex_income_rate = (
        df.groupby("sex", dropna=False)["income_binary"].mean().mul(100).round(2).reset_index(name="gt_50k_rate_pct")
    )
    race_income_rate = (
        df.groupby("race", dropna=False)["income_binary"].mean().mul(100).round(2).reset_index(name="gt_50k_rate_pct")
    )
    occupation_income_rate = (
        df.groupby("occupation", dropna=False)
        .agg(count=("income_binary", "size"), gt_50k_rate=("income_binary", "mean"))
        .reset_index()
    )
    occupation_income_rate["gt_50k_rate_pct"] = occupation_income_rate["gt_50k_rate"].mul(100).round(2)
    occupation_income_rate = occupation_income_rate.drop(columns="gt_50k_rate").sort_values(
        ["gt_50k_rate_pct", "count"], ascending=[False, False]
    )

    tables = {
        "numeric_summary.csv": numeric_summary,
        "categorical_summary.csv": categorical_summary_df,
        "sex_income_rate.csv": sex_income_rate,
        "race_income_rate.csv": race_income_rate,
        "occupation_income_rate.csv": occupation_income_rate,
    }

    for file_name, table in tables.items():
        table.to_csv(OUTPUT_DIR / file_name, index=False)

    return tables


def create_plots(df: pd.DataFrame) -> None:
    income_counts = df["income"].value_counts().sort_index()
    plt.figure(figsize=(7, 5))
    income_counts.plot(kind="bar", color=["#9ecae1", "#3182bd"])
    plt.title("Income Class Distribution")
    plt.ylabel("Count")
    plt.xlabel("Income")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "income_distribution.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    for income_label, color in [("<=50K", "#9ecae1"), (">50K", "#e6550d")]:
        subset = df.loc[df["income"] == income_label, "age"]
        plt.hist(subset, bins=20, alpha=0.6, label=income_label, color=color)
    plt.title("Age Distribution by Income")
    plt.xlabel("Age")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "age_by_income.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    for income_label, color in [("<=50K", "#9ecae1"), (">50K", "#31a354")]:
        subset = df.loc[df["income"] == income_label, "hours.per.week"]
        plt.hist(subset, bins=20, alpha=0.6, label=income_label, color=color)
    plt.title("Hours per Week by Income")
    plt.xlabel("Hours per Week")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hours_by_income.png", dpi=200)
    plt.close()

    sex_rates = df.groupby("sex")["income_binary"].mean().mul(100).sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    sex_rates.plot(kind="bar", color="#756bb1")
    plt.title(">50K Rate by Sex")
    plt.ylabel("Rate (%)")
    plt.xlabel("Sex")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "income_rate_by_sex.png", dpi=200)
    plt.close()

    top_occupations = (
        df.groupby("occupation")
        .agg(count=("income_binary", "size"), rate=("income_binary", "mean"))
        .dropna()
        .query("count >= 200")
        .sort_values("rate", ascending=False)
        .head(10)
    )
    plt.figure(figsize=(10, 6))
    plt.barh(top_occupations.index[::-1], top_occupations["rate"].mul(100)[::-1], color="#dd1c77")
    plt.title("Top Occupations by >50K Rate (n >= 200)")
    plt.xlabel("Rate (%)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_occupation_income_rates.png", dpi=200)
    plt.close()


def write_summary(df: pd.DataFrame) -> None:
    income_rate = df["income_binary"].mean() * 100
    age_means = df.groupby("income")["age"].mean()
    hours_means = df.groupby("income")["hours.per.week"].mean()
    sex_rates = df.groupby("sex")["income_binary"].mean().mul(100)
    race_rates = df.groupby("race")["income_binary"].mean().mul(100).sort_values(ascending=False)
    gain_rates = (
        df.assign(has_capital_gain=df["capital.gain"] > 0)
        .groupby("income")["has_capital_gain"]
        .mean()
        .mul(100)
    )
    top_occupation = (
        df.groupby("occupation")
        .agg(count=("income_binary", "size"), rate=("income_binary", "mean"))
        .dropna()
        .query("count >= 200")
        .sort_values("rate", ascending=False)
        .head(3)
    )

    summary = f"""# EDA Summary

Dataset size: {df.shape[0]:,} rows x {df.shape[1] - 1} original columns.

Key findings:
- Income is imbalanced: {income_rate:.2f}% of records are `>50K`.
- Higher earners are older on average ({age_means['>50K']:.2f} vs {age_means['<=50K']:.2f} years).
- Higher earners also work more hours on average ({hours_means['>50K']:.2f} vs {hours_means['<=50K']:.2f} per week).
- The `>50K` rate differs sharply by sex: Male {sex_rates['Male']:.2f}% vs Female {sex_rates['Female']:.2f}%.
- Capital gains are uncommon overall but much more common among high earners ({gain_rates['>50K']:.2f}% vs {gain_rates['<=50K']:.2f}%).
- Highest observed `>50K` rates among larger occupations:
"""

    for occupation, row in top_occupation.iterrows():
        summary += f"- {occupation}: {row['rate'] * 100:.2f}% (`n`={int(row['count'])})\n"

    summary += "\nRace-level >50K rates:\n"
    for race, rate in race_rates.items():
        summary += f"- {race}: {rate:.2f}%\n"

    (OUTPUT_DIR / "eda_summary.md").write_text(summary)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    save_tables(df)
    create_plots(df)
    write_summary(df)


if __name__ == "__main__":
    main()
