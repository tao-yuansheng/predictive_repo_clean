# T2 — EDA: Expected Output Schema

Describes what correct output looks like. Used by Member 5 as a reference when scoring.

---

## Plot Files (saved to output/)
Minimum expected files:

| Filename (indicative)        | Content                                              |
|------------------------------|------------------------------------------------------|
| income_distribution.png      | Bar/pie chart of <=50K vs >50K counts                |
| dist_age.png (or similar)    | Distribution plot for each numeric column            |
| correlation_heatmap.png      | Heatmap of numeric feature correlations              |
| barplot_workclass.png (etc.) | Bar chart per categorical column (top categories)    |
| bivariate_*.png              | Boxplot or stacked bar for top 3 features vs income  |

All plots must have readable titles and axis labels.

## Printed Output (captured in session_log.txt)
Must include:
- Shape of dataset
- Missing value counts/percentages per column (after "?" -> NaN)
- Summary stats table for numeric columns
- Outlier counts per numeric column
- Cardinality per categorical column
- Class imbalance ratio (e.g. "<=50K : >50K = 3.0 : 1")
- Top 5 features correlated with income
- Leakage flags with justification

## Written Summary
Present at end of script as either:
- A multi-line print() block, or
- A block of # comment lines
Must cover: key patterns, columns needing special handling, preprocessing recommendations.

## What FAIL looks like
- "?" still treated as a valid category in plots
- Correlation computed on un-encoded target (string comparison)
- No class imbalance ratio
- Plots saved with no labels or titles
- Summary section missing
