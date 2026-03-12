# MSIN0097 — Agent Benchmarking Study

## What is this study?

We are comparing three AI coding agents — **Claude Code, Codex, and Google Antigravity** —
on their ability to autonomously complete five data science tasks on the same dataset
(UCI Adult Income, ~32,000 rows, binary classification).

Each agent is given the tasks twice: once with a **vague prompt** (minimal guidance) and
once with a **specific prompt** (fully structured requirements). This lets us measure not
just whether agents can do data science, but how much their output quality depends on how
well the task is specified — a key question for practitioners deciding how to use these tools.

**30 total runs**: 3 agents × 5 tasks × 2 prompt types
**Deadline**: 20 March 2026 | **Team size**: 5

---

## The Five Tasks

| Task | What the agent must do |
|------|------------------------|
| **T1 — Data Ingestion** | Load and clean the raw CSV: handle missing values, fix dtypes, remove duplicates, cap outliers |
| **T2 — EDA** | Explore the dataset: distributions, correlations, class imbalance, visualisations |
| **T3 — Baseline Model** | Train a baseline classifier, evaluate with accuracy/F1/confusion matrix, save the model |
| **T4 — Leakage Detection** | Audit all features for data leakage risk; remove confirmed leakers; compare before/after accuracy |
| **T5 — Debugging** | Find and fix 3 deliberately planted bugs in a broken ML pipeline script |

Tasks run sequentially in one session (T1 → T2 → T3 → T4 → T5). Each agent reads only
its own results folder and the shared `tasks/` files — never another agent's folder or the answer keys.

---

## Team Roles

| Member | Role | Responsibility |
|--------|------|----------------|
| 1 | Dataset & Harness | Repo owner. Push to GitHub, merge PRs when all runs are done. |
| 2 | Claude Code Runner | Run two sessions (vague + specific). See Section: Member 2. |
| 3 | Codex Runner | Run two sessions (vague + specific). See Section: Member 3. |
| 4 | Antigravity Runner | Run two sessions (vague + specific). See Section: Member 4. |
| 5 | Scoring & Analysis | Score all 30 runs using the rubric. See Section: Member 5. |

---

## Repo Structure

```
msin0097-benchmark/
├── data/
│   └── raw/dataset.csv                        ← shared input — do not modify
├── tasks/
│   ├── project_context.md                     ← dataset overview agents read first
│   ├── run_pipeline_vague_claude_code.txt      ← full T1→T5 pipeline for Member 2, vague
│   ├── run_pipeline_specific_claude_code.txt   ← full T1→T5 pipeline for Member 2, specific
│   ├── run_pipeline_vague_codex.txt
│   ├── run_pipeline_specific_codex.txt
│   ├── run_pipeline_vague_antigravity.txt
│   ├── run_pipeline_specific_antigravity.txt
│   ├── T1_ingestion/
│   ├── T2_eda/
│   ├── T3_model/
│   ├── T4_leakage/
│   └── T5_debugging/
│       └── buggy_pipeline.py                  ← broken script the agent must debug (T5)
├── results/
│   ├── claude_code/                           ← Member 2 writes here
│   ├── codex/                                 ← Member 3 writes here
│   └── antigravity/                           ← Member 4 writes here
└── scoring/
    └── rubric.md                              ← Member 5 owns this
```

Each run is stored at:
```
results/{agent}/{task}/{vague|specific}/
    generated_code.py    ← code the agent wrote (copy from session if not auto-saved)
    session_log.txt      ← full session transcript
    run_notes.md         ← your observations (see guidance below)
    scorecard.md         ← leave blank — Member 5 fills this in
    output/              ← files the agent saved directly (CSVs, plots, models, etc.)
```

---

## Git Workflow — do this before starting any session

### Step 1 — One-time git setup (skip if you have done this before)
If this is your first time using git on this machine, run these two lines first
(replace with your own name and university email):
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@ucl.ac.uk"
```

### Step 2 — Clone the repo and create your branch
```bash
git clone https://github.com/tao-yuansheng/predictive_repo_clean.git
cd predictive_repo_clean
git checkout -b run/claude-code     # Member 2
# git checkout -b run/codex         # Member 3
# git checkout -b run/antigravity   # Member 4
```
Note: the cloned folder is called `predictive_repo_clean` — that is the repo root.
The benchmark files are inside it (README.md, tasks/, data/, results/, scoring/).

Each runner works on their own branch. Because each agent writes only to its own
`results/{agent}/` folder, there are no merge conflicts when combining results.

---

## How to Run a Session (Members 2, 3, 4)

### Before you start
- Complete the Git setup above (clone, create branch)
- Open your agent tool (Claude Code CLI, Codex interface, Antigravity)
- Make sure the working directory is set to `predictive_repo_clean/`

### Starting the session — copy and paste one line
Find your copy-paste line in the section for your member number below.
Paste it as your **first message** to the agent. The agent will then read the
pipeline file and work through all five tasks automatically.

You do not need to send any further prompts unless the agent gets stuck or asks
a question. If it does, answer concisely and record what happened in `run_notes.md`.

### After the session ends
1. **Export the session transcript** and save it as `session_log.txt` in the correct
   run folder. How to export:
   - *Claude Code*: use `/export` or copy the terminal output
   - *Codex*: use the export/download option in the interface
   - *Antigravity*: use the session export feature
2. **Copy any generated code** to `generated_code.py` if the agent did not save it directly
3. **Fill in `run_notes.md`** — see guidance below
4. **Leave `scorecard.md` blank** — Member 5 fills that in

### Step 3 — Once both sessions are complete, commit and push your results
```bash
git add results/claude_code/        # Member 2 — stage only your folder
# git add results/codex/            # Member 3
# git add results/antigravity/      # Member 4
git commit -m "Claude Code runs complete — vague and specific"
git push origin run/claude-code
```
Then open a **Pull Request → `main`** on GitHub.

> **Warning: never use `git add .` or `git add -A`.**
> If the agent accidentally wrote a file outside your `results/{agent}/` folder,
> a blanket add would commit it and corrupt the shared task files for other runners.
> Always stage your folder explicitly by name.

### Step 4 — Member 1 merges all three PRs into `main`
Merge in any order once all three runners have opened their PRs. Member 5 then
pulls `main` to begin scoring.

### What to write in `run_notes.md`
Record these things for every session:
- Total number of prompt–response iterations (a new prompt you sent = one iteration)
- Did the agent complete all 5 tasks without being re-prompted? If not, which task failed and why?
- Did the agent read or attempt to read any forbidden files (answer keys, other agents' folders)?
- Any errors, crashes, or refusals — exact wording if possible
- Your overall impression: did the output look correct at a glance?

This file is what Member 5 uses for the Efficiency and Safety scoring dimensions, so accuracy matters.

---

## ── MEMBER 2 — Claude Code ────────────────────────────────────────────────

### Vague session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_vague_claude_code.txt
```

### Specific session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_specific_claude_code.txt
```

---

## ── MEMBER 3 — Codex ─────────────────────────────────────────────────────

### Vague session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_vague_codex.txt
```

### Specific session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_specific_codex.txt
```

---

## ── MEMBER 4 — Antigravity ───────────────────────────────────────────────

### Vague session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_vague_antigravity.txt
```

### Specific session — copy and paste this as your first message:

```
Read tasks/project_context.md then read and follow tasks/run_pipeline_specific_antigravity.txt
```

---

## ── MEMBER 5 — Scoring ───────────────────────────────────────────────────

Wait until Member 1 has merged all three PRs, then pull `main` and score all 30 runs.

### Scoring process
1. Open `scoring/rubric.md` — it contains the full scoring template and task-specific guidance
2. For each run: open `results/{agent}/{task}/{prompt_type}/`
   - Read `session_log.txt` and `generated_code.py`
   - Check `output/` for the expected files
   - Consult `tasks/{task}/success_criteria.md` for the pass/fail checklist
   - Consult `tasks/{task}/expected_output_schema.md` for exact output format
   - Fill in `scorecard.md` (6 dimensions, 0/1/2 each = max 12 per run)
3. Transfer all scores to the cross-agent summary table in `scoring/rubric.md`

**Max scores**: 12 per run · 60 per agent per prompt type · 120 per agent overall

### Cross-checks (after primary scoring is complete)
Each runner independently scores one run from a different agent as a reliability check:
- Member 2 cross-checks one Codex run
- Member 3 cross-checks one Antigravity run
- Member 4 cross-checks one Claude Code run

Compare your score to Member 5's score for that run. Discuss any dimension where
you differ by more than 1 point.

---

## Rules

- Do not modify files in `tasks/` or `data/raw/` once runs begin
- Do not score your own agent's runs
- Record every iteration and self-correction in `run_notes.md` — do not re-prompt silently
- If an agent crashes or refuses a task, record it exactly as-is and move on
