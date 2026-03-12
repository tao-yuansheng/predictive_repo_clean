# Project Context — MSIN0097 Benchmarking Study

Read this file before starting any task. It provides the background you need
to make informed decisions throughout the pipeline.

---

## What You Are Doing

You are working through a structured data science pipeline on the UCI Adult
Income dataset. There are 5 tasks to complete in order. Each task builds on
the previous one.

You are being evaluated. Work carefully, document your decisions, and save
all outputs to the correct folders as instructed in each task prompt.

---

## Dataset

- File: data/raw/dataset.csv
- Source: UCI Adult Income dataset (1994 US Census)
- Size: ~32,000 rows, 15 columns
- Missing values are encoded as the string "?" — treat as NaN throughout

### Columns

| Column          | Type        | Description                                      |
|-----------------|-------------|--------------------------------------------------|
| age             | numeric     | Age in years                                     |
| workclass       | categorical | Employment type (Private, Gov, Self-emp, etc.)   |
| fnlwgt          | numeric     | Census sampling weight — not a predictive feature|
| education       | categorical | Highest education level attained                 |
| education.num   | numeric     | Education encoded as years (ordinal)             |
| marital.status  | categorical | Marital status                                   |
| occupation      | categorical | Job category                                     |
| relationship    | categorical | Family role (Wife, Husband, Own-child, etc.)     |
| race            | categorical | Race                                             |
| sex             | categorical | Sex                                              |
| capital.gain    | numeric     | Capital gains income — heavily zero-inflated     |
| capital.loss    | numeric     | Capital losses — heavily zero-inflated           |
| hours.per.week  | numeric     | Hours worked per week                            |
| native.country  | categorical | Country of origin                                |
| income          | TARGET      | <=50K or >50K annual income                      |

### Known Data Quirks
- workclass, occupation, and native.country contain "?" as missing value marker
- capital.gain and capital.loss are zero for >90% of rows
- education and education.num are redundant (ordinal encoding of the same variable)
- fnlwgt is a census weight, not a demographic feature — treat with caution in models

---

## Target Variable

**income** — binary classification:
- Positive class (1): >50K annual income
- Negative class (0): <=50K annual income
- Class distribution: approximately 75% <=50K, 25% >50K (imbalanced)

---

## Research Questions

### Primary
Which demographic and employment features best predict whether an individual
earns above $50K annually?

### Secondary
1. Does capital gain/loss dominate predictions over labour-market features
   (occupation, hours worked per week)?
2. How does model performance vary across demographic slices (sex, race)?
   Are there fairness gaps?
3. What is the optimal classification threshold when balancing precision vs
   recall for income prediction?

Keep these questions in mind as you work. Note relevant findings in your
code comments and outputs — they will inform the final analysis.

---

## Your Results Folder

All your output files must be saved to: results/[AGENT_NAME]/

Do not write to any other agent's results folder.
Do not modify files in tasks/ or data/raw/.

---

## Task Overview

| Task | Folder            | What it does                          |
|------|-------------------|---------------------------------------|
| T1   | T1_ingestion      | Load, clean, and validate the dataset |
| T2   | T2_eda            | Exploratory data analysis and insight |
| T3   | T3_model          | Train and evaluate a baseline model   |
| T4   | T4_leakage        | Audit the dataset for data leakage    |
| T5   | T5_debugging      | Find and fix bugs in a broken pipeline|

Complete tasks in order T1 → T2 → T3 → T4 → T5.
Confirm outputs are saved after each task before moving to the next.

---

## File Access Rules

You may only read files you have been explicitly directed to.

### Permitted
- `tasks/project_context.md` (this file)
- `tasks/T*/prompt_vague.txt` or `tasks/T*/prompt_specific.txt` (as directed per task)
- `tasks/T5_debugging/buggy_pipeline.py` (T5 only)
- `data/raw/dataset.csv`
- Your own results folder: `results/[your agent name]/`

### Forbidden
| File / Folder | Reason |
|---------------|--------|
| `tasks/*/success_criteria.md` | Scoring rubric — for Member 5 only |
| `tasks/*/expected_output_schema.md` | Answer keys — reading these invalidates your run |
| `scoring/rubric.md` | Scoring sheet — for Member 5 only |
| Any other agent's results folder | Stays in your own results only |
| Any file not listed above | Out of scope |

Your own results folder (as declared in your pipeline file) is permitted.

Reading forbidden files invalidates the run.
