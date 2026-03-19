# Benchmark Score Sheet

This file records the final scoring for all 30 benchmark runs on the `complete` branch.

## Overall Totals

| Agent | T1 v | T1 s | T2 v | T2 s | T3 v | T3 s | T4 v | T4 s | T5 v | T5 s | Grand Total /120 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Code | 8 | 11 | 9 | 11 | 8 | 12 | 8 | 11 | 7 | 12 | **97** |
| Codex | 7 | 11 | 7 | 10 | 9 | 11 | 7 | 11 | 5 | 9 | **87** |
| Gemini CLI | 7 | 9 | 7 | 9 | 7 | 10 | 5 | 6 | 5 | 7 | **72** |

## Ranking

1. Claude Code: 97/120
2. Codex: 87/120
3. Gemini CLI: 72/120

## Task-by-Task Breakdown

### Claude Code

| Task | Vague /12 | Specific /12 |
| --- | ---: | ---: |
| T1 - Ingestion | 8 | 11 |
| T2 - EDA | 9 | 11 |
| T3 - Baseline Model | 8 | 12 |
| T4 - Leakage Detection | 8 | 11 |
| T5 - Debugging | 7 | 12 |

### Codex

| Task | Vague /12 | Specific /12 |
| --- | ---: | ---: |
| T1 - Ingestion | 7 | 11 |
| T2 - EDA | 7 | 10 |
| T3 - Baseline Model | 9 | 11 |
| T4 - Leakage Detection | 7 | 11 |
| T5 - Debugging | 5 | 9 |

### Gemini CLI

| Task | Vague /12 | Specific /12 |
| --- | ---: | ---: |
| T1 - Ingestion | 7 | 9 |
| T2 - EDA | 7 | 9 |
| T3 - Baseline Model | 7 | 10 |
| T4 - Leakage Detection | 5 | 6 |
| T5 - Debugging | 5 | 7 |

## Dimension Reference

Each run was scored from 0 to 2 on the following dimensions:

- Correctness
- Statistical Validity
- Reproducibility
- Code Quality
- Efficiency
- Safety and Scope Compliance

Maximum per run: `12`

Maximum per agent: `120`
