# Benchmark Comparison Report

## Purpose

This report compares Claude Code, Codex, and Google Antigravity across the five benchmark tasks in the repository. Each agent completed the same workflow twice: once with vague prompts and once with specific prompts. The goal of the comparison is not only to identify which model produced the strongest outputs, but also to understand how each model responded to prompt clarity, task structure, and technical constraints.

## Evaluation Logic

Each run was scored on six dimensions, with a score of `0`, `1`, or `2` in each dimension.

- `Correctness`: whether the run actually completed the requested task and saved the required deliverables.
- `Statistical Validity`: whether the modelling, cleaning, analysis, or debugging logic was methodologically sound.
- `Reproducibility`: whether the run could be rerun cleanly from the saved code and artifacts.
- `Code Quality`: whether the implementation was readable, systematic, and avoided unnecessary errors.
- `Efficiency`: whether the run appeared to complete within a low number of interaction cycles.
- `Safety and Scope Compliance`: whether the run stayed within the allowed file-access boundaries.

The strongest runs were not just the ones that produced files. They were the runs that followed the exact task specification, used correct statistical reasoning, and saved reusable outputs in the expected locations.

## Important Scoring Assumptions

- Codex session logs were empty in the saved results, so efficiency for Codex was judged conservatively from the saved artifacts rather than from a full interaction trace.
- Antigravity session logs were placeholders rather than detailed transcripts, so efficiency was also judged conservatively there.
- Safety scoring was based on saved evidence only. No saved artifact showed a confirmed read of forbidden answer-key files.
- Reproducibility was judged mainly from the saved scripts, output completeness, deterministic settings such as `random_state=42`, and whether the run structure looked rerunnable without hidden manual steps.

## Task-by-Task Criteria and Comparison

### T1 - Data Ingestion

The ingestion task tested whether an agent could correctly load the raw Adult Income dataset, replace `"?"` with missing values, audit missingness, clean duplicates, cap outliers using IQR, and save both a cleaned dataset and a missingness heatmap.

The strongest T1 runs were the specific submissions from Claude Code and Codex. Both produced the expected core outputs and followed the cleaning logic more closely. Codex's specific run was especially systematic in its schema validation and final cleaning report. Claude Code's specific run was also strong, though a small reproducibility deduction remained because environment details were recorded only in comments instead of a separate pinned artifact.

The weaker vague runs generally had one of two issues:

- they produced an incomplete output package, or
- they cleaned the data in a way that drifted from the benchmark expectation.

Codex vague is a good example of this tradeoff. It performed useful work, but added an extra derived column and missed required outputs. Claude Code vague cleaned the data, but missed some required benchmark artifacts. Antigravity vague produced the core cleaned dataset but lacked the supporting reporting expected by the rubric.

### T2 - Exploratory Data Analysis

The EDA task evaluated whether the agent could explore the dataset thoroughly, compute meaningful summaries, note important quirks such as class imbalance and zero inflation, and save a broad set of plots with readable titles and labels.

The specific prompts made a clear difference here. Claude Code specific was the strongest run because it produced the most complete set of expected visual artifacts and kept the analysis reasonably aligned with the benchmark goals. Codex specific was close behind, with broad plot coverage and good readability, but it lost a little ground on completeness and supporting narrative. Antigravity specific completed the task competently, but the implementation and written interpretation were less thorough.

The vague runs tended to generate some good EDA outputs, but they usually fell short on completeness. In particular, vague submissions often saved several useful plots but did not fully satisfy the benchmark's expectation for the complete plot set, printed statistical summary, and final written interpretation.

### T3 - Baseline Model

The model task tested whether the agent could train a baseline logistic regression pipeline correctly: encode the target, split the data properly, avoid leakage, report the required metrics, and save the full artifact package including the model, confusion matrix, JSON metrics, and runnable script.

This was one of the strongest tasks across all agents under the specific prompt condition. Claude Code specific scored highest because it delivered the full required output set with strong reproducibility and clean implementation. Codex specific was also very strong and only slightly behind. Antigravity specific completed the full package too, but the code quality and supporting detail were lighter than the top two.

The vague runs showed a different pattern. Codex vague actually performed relatively well methodologically, but it did not save the exact required deliverables. Claude Code vague and Antigravity vague both managed to train and evaluate a model, but the artifact packages were not as complete as the rubric required. This task clearly benefited from the more explicit specific prompt.

### T4 - Leakage Detection

This task was one of the most demanding because it required both statistical judgment and structured reporting. A strong submission needed to audit all 14 features, apply multiple leakage checks, justify flagged features with evidence, remove confirmed leakers, and compare performance before and after removal.

Claude Code specific and Codex specific were the strongest runs here. Both produced complete reports, audited the feature set systematically, and included before/after reasoning. Codex specific in particular was strong on structure and verification. Claude Code specific was also strong and readable, with a clear report format.

The vague runs were notably weaker for all agents. They usually showed some awareness of suspicious features, but they often lacked the full systematic audit required by the task. Antigravity was weakest on T4 overall. Its vague run remained shallow, and its specific run produced a structured report but still failed on key task logic because it did not remove any confirmed leaks and also used a leaky verification step by fitting the scaler on the test data during evaluation.

This task most clearly separated "can discuss the concept" from "can carry out the full benchmark requirement."

### T5 - Debugging

The debugging task required the agent to inspect a buggy pipeline, identify the three planted bugs, explain them with line references and severity, produce a corrected script, and annotate the fixed code with `# FIX [N]` comments.

Claude Code specific was the strongest T5 run. It found the intended bugs, documented them clearly, saved the expected `bug_report.md`, and produced a fixed script that matched the benchmark intent closely.

Codex specific fixed the important planted issues, but it lost points because the bug report expanded into additional non-planted issues and the fixed script drifted further from the benchmark's expected shape. Antigravity specific handled the core bug-fixing logic more successfully than its vague run, but the supporting explanation and reproducibility evidence were still comparatively thin.

The vague debugging runs were weak across the board. They often produced partial analysis or secondary artifacts, but failed to save the full required deliverable set. That matters in this benchmark because debugging is not scored only on whether the model noticed a bug, but also on whether it produced a correct and auditable fix package.

## Overall Comparison

### Claude Code

Claude Code performed best overall with `97/120`. Its main strength was completeness. It was the most consistent at producing full deliverable sets, especially on the specific prompts, and it was strongest on T3 and T5. It also handled the structure-heavy tasks well once the requirements were made explicit.

Its main weakness was under-specification sensitivity in the vague condition. Several vague runs were useful, but did not fully satisfy the required benchmark artifact set.

### Codex

Codex placed second with `87/120`. Its main strength was technical solidity under the specific prompts. On T1, T3, and T4 specific, it was very competitive and sometimes close to the top score. Its code was often systematic and strongly structured.

Its main weakness was similar to Claude Code's, but slightly more pronounced on vague prompts: several runs produced meaningful work without matching the exact required output contract. T5 specific also lost points because the debugging solution solved the planted bugs but introduced extra problem framing that moved away from the benchmark's exact target.

### Google Antigravity

Google Antigravity finished third with `72/120`. It did complete many tasks at a basic functional level, and its specific prompts improved performance noticeably. However, relative to the other two agents, its outputs were less systematic, less fully evidenced, and more likely to miss important benchmark deliverables or methodological details.

Its biggest struggles were on the more reasoning-heavy and verification-heavy tasks, especially T4 and T5, where success depended on precise task interpretation rather than just producing plausible output.

## Effect of Prompt Specificity

One of the clearest findings from the benchmark is that all three agents improved under the specific prompts.

- Claude Code improved from solid-but-incomplete vague runs to highly complete specific runs.
- Codex improved from technically useful but sometimes under-scoped vague runs to strong benchmark-aligned specific runs.
- Antigravity also improved under specific prompts, although the gap between it and the other two agents remained.

This means the benchmark supports the idea that prompt structure materially affects performance, especially on tasks where correctness depends on exact output formats, strict evaluation logic, or explicit methodological constraints.

## Conclusion

The overall result is that Claude Code was the strongest benchmark performer, Codex was a strong second with particularly good specific-prompt performance, and Google Antigravity was clearly more variable and less complete on the harder tasks.

The most important pattern is not just the final ranking. It is that benchmark performance depended heavily on whether the task was fully specified. When the prompt clearly defined the deliverables, evaluation logic, and constraints, all agents improved. The top-performing agent was the one that combined technical capability with stronger completion discipline across the full artifact package.
