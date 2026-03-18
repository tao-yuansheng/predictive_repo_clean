"""
Benchmark Comparison Visualizations
Academic minimalistic style, suitable for A4 academic papers.
"""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

matplotlib.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#dddddd",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
})

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

AGENTS = ["Claude Code", "Codex", "Google Antigravity"]
TASKS = ["T1\nIngestion", "T2\nEDA", "T3\nBaseline\nModel", "T4\nLeakage\nDetection", "T5\nDebugging"]
TASK_KEYS = ["T1_ingestion", "T2_eda", "T3_model", "T4_leakage", "T5_debugging"]
DIMENSIONS = ["Correctness", "Statistical\nValidity", "Reproducibility", "Code\nQuality", "Efficiency", "Safety"]

# Raw scores: [correctness, stat_validity, reproducibility, code_quality, efficiency, safety]
SCORES = {
    ("claude_code", "T1_ingestion", "vague"):    [1, 1, 1, 1, 2, 2],
    ("claude_code", "T1_ingestion", "specific"): [2, 2, 1, 2, 2, 2],
    ("claude_code", "T2_eda",       "vague"):    [2, 1, 1, 1, 2, 2],
    ("claude_code", "T2_eda",       "specific"): [2, 2, 1, 2, 2, 2],
    ("claude_code", "T3_model",     "vague"):    [1, 1, 1, 1, 2, 2],
    ("claude_code", "T3_model",     "specific"): [2, 2, 2, 2, 2, 2],
    ("claude_code", "T4_leakage",   "vague"):    [1, 1, 1, 1, 2, 2],
    ("claude_code", "T4_leakage",   "specific"): [2, 2, 1, 2, 2, 2],
    ("claude_code", "T5_debugging", "vague"):    [1, 1, 0, 1, 2, 2],
    ("claude_code", "T5_debugging", "specific"): [2, 2, 2, 2, 2, 2],

    ("codex",       "T1_ingestion", "vague"):    [1, 1, 1, 1, 1, 2],
    ("codex",       "T1_ingestion", "specific"): [2, 2, 2, 2, 1, 2],
    ("codex",       "T2_eda",       "vague"):    [1, 1, 1, 1, 1, 2],
    ("codex",       "T2_eda",       "specific"): [2, 2, 1, 2, 1, 2],
    ("codex",       "T3_model",     "vague"):    [1, 2, 1, 2, 1, 2],
    ("codex",       "T3_model",     "specific"): [2, 2, 2, 2, 1, 2],
    ("codex",       "T4_leakage",   "vague"):    [1, 1, 1, 1, 1, 2],
    ("codex",       "T4_leakage",   "specific"): [2, 2, 2, 2, 1, 2],
    ("codex",       "T5_debugging", "vague"):    [0, 1, 0, 1, 1, 2],
    ("codex",       "T5_debugging", "specific"): [1, 2, 2, 1, 1, 2],

    ("antigravity", "T1_ingestion", "vague"):    [1, 1, 1, 1, 1, 2],
    ("antigravity", "T1_ingestion", "specific"): [2, 2, 1, 1, 1, 2],
    ("antigravity", "T2_eda",       "vague"):    [1, 1, 1, 1, 1, 2],
    ("antigravity", "T2_eda",       "specific"): [2, 2, 1, 1, 1, 2],
    ("antigravity", "T3_model",     "vague"):    [1, 1, 1, 1, 1, 2],
    ("antigravity", "T3_model",     "specific"): [2, 2, 2, 1, 1, 2],
    ("antigravity", "T4_leakage",   "vague"):    [0, 0, 1, 1, 1, 2],
    ("antigravity", "T4_leakage",   "specific"): [1, 0, 1, 1, 1, 2],
    ("antigravity", "T5_debugging", "vague"):    [0, 1, 0, 1, 1, 2],
    ("antigravity", "T5_debugging", "specific"): [1, 1, 1, 1, 1, 2],
}

AGENT_KEYS = ["claude_code", "codex", "antigravity"]

# Muted, colorblind-friendly palette (black, dark grey, light grey for B&W printing)
COLORS = ["#1a1a2e", "#4a7fc1", "#a8c5da"]   # dark navy, medium blue, light blue
HATCHES = ["", "//", ".."]

from pathlib import Path
OUT_DIR = str(Path(__file__).parent / "figures") + "/"
Path(OUT_DIR).mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Helper: compute aggregate totals
# ---------------------------------------------------------------------------

def run_total(agent: str, task: str, prompt: str) -> int:
    return sum(SCORES[(agent, task, prompt)])

def agent_task_total(agent: str, task: str) -> int:
    return run_total(agent, task, "vague") + run_total(agent, task, "specific")

def agent_prompt_total(agent: str, prompt: str) -> int:
    return sum(run_total(agent, t, prompt) for t in TASK_KEYS)

def agent_grand_total(agent: str) -> int:
    return sum(run_total(agent, t, p) for t in TASK_KEYS for p in ["vague", "specific"])

def agent_dim_total(agent: str, dim_idx: int) -> int:
    return sum(SCORES[(agent, t, p)][dim_idx] for t in TASK_KEYS for p in ["vague", "specific"])

# ---------------------------------------------------------------------------
# Figure 1 – Overall total scores (horizontal bar)
# ---------------------------------------------------------------------------

def fig_overall():
    totals = [agent_grand_total(a) for a in AGENT_KEYS]
    pct = [t / 120 * 100 for t in totals]

    fig, ax = plt.subplots(figsize=(7, 3))
    y = np.arange(len(AGENTS))
    bars = ax.barh(y, totals, color=COLORS, edgecolor="black", linewidth=0.8, height=0.55)
    for bar, t, p in zip(bars, totals, pct):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{t}/120  ({p:.1f}%)", va="center", ha="left", fontsize=12)

    ax.set_yticks(y)
    ax.set_yticklabels(AGENTS[::-1][::-1], fontsize=12)  # keep order
    ax.set_xlabel("Total Score (max 120)", fontsize=13)
    ax.set_xlim(0, 135)
    ax.set_title("Overall Benchmark Scores", fontsize=14, pad=10)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig1_overall.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig1_overall.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig1_overall")

# ---------------------------------------------------------------------------
# Figure 2 – Per-task scores (grouped bar, vague+specific combined)
# ---------------------------------------------------------------------------

def fig_per_task():
    n_tasks = len(TASK_KEYS)
    n_agents = len(AGENT_KEYS)
    width = 0.25
    x = np.arange(n_tasks)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, (agent_key, label, color, hatch) in enumerate(zip(AGENT_KEYS, AGENTS, COLORS, HATCHES)):
        vals = [agent_task_total(agent_key, t) for t in TASK_KEYS]
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=label,
                      color=color, edgecolor="black", linewidth=0.7, hatch=hatch)

    task_labels = ["T1\nIngestion", "T2\nEDA", "T3\nBaseline\nModel",
                   "T4\nLeakage\nDetection", "T5\nDebugging"]
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels, fontsize=12)
    ax.set_ylabel("Score (max 24)", fontsize=13)
    ax.set_ylim(0, 28)
    ax.set_title("Scores by Task (Vague + Specific Combined)", fontsize=14, pad=10)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=12)
    ax.grid(axis="y")
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig2_per_task.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig2_per_task.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig2_per_task")

# ---------------------------------------------------------------------------
# Figure 3 – Vague vs Specific per agent (grouped bar)
# ---------------------------------------------------------------------------

def fig_per_prompt():
    prompts = ["vague", "specific"]
    prompt_labels = ["Vague", "Specific"]
    width = 0.25
    x = np.arange(len(prompts))

    fig, ax = plt.subplots(figsize=(6, 4))
    for i, (agent_key, label, color, hatch) in enumerate(zip(AGENT_KEYS, AGENTS, COLORS, HATCHES)):
        vals = [agent_prompt_total(agent_key, p) for p in prompts]
        offset = (i - 1) * width
        ax.bar(x + offset, vals, width, label=label,
               color=color, edgecolor="black", linewidth=0.7, hatch=hatch)

    ax.set_xticks(x)
    ax.set_xticklabels(prompt_labels, fontsize=13)
    ax.set_ylabel("Score (max 60)", fontsize=13)
    ax.set_ylim(0, 70)
    ax.set_title("Scores by Prompt Specificity", fontsize=14, pad=10)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=12)
    ax.grid(axis="y")
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig3_per_prompt.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig3_per_prompt.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig3_per_prompt")

# ---------------------------------------------------------------------------
# Figure 4 – Per-dimension radar chart
# ---------------------------------------------------------------------------

def fig_radar():
    n_dims = len(DIMENSIONS)
    angles = np.linspace(0, 2 * np.pi, n_dims, endpoint=False).tolist()
    angles += angles[:1]  # close polygon

    max_dim = 20  # 10 runs × 2 max per run

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})

    for agent_key, label, color in zip(AGENT_KEYS, AGENTS, COLORS):
        vals = [agent_dim_total(agent_key, d) for d in range(n_dims)]
        vals_norm = [v / max_dim for v in vals]
        vals_norm += vals_norm[:1]
        ax.plot(angles, vals_norm, "o-", linewidth=1.8, color=color, markersize=5, label=label)
        ax.fill(angles, vals_norm, alpha=0.12, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), DIMENSIONS, fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([])  # remove labels — they overlap plotted lines
    # add subtle reference ring labels outside the plot area instead
    for r, lbl in zip([0.25, 0.5, 0.75, 1.0], ["25%", "50%", "75%", "100%"]):
        ax.text(np.pi / 6, r, lbl, ha="left", va="center", fontsize=9,
                color="#666666", transform=ax.transData)
    ax.set_title("Scores by Evaluation Dimension\n(proportion of maximum)", fontsize=14, pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=12)
    # clean grid — only the circular reference rings, no radial spokes clutter
    ax.grid(color="#cccccc", linewidth=0.6)
    ax.spines["polar"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig4_radar.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig4_radar.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig4_radar")

# ---------------------------------------------------------------------------
# Figure 5 – Heatmap of all 30 runs
# ---------------------------------------------------------------------------

def fig_heatmap():
    # Rows: agents × prompts (6 rows); Cols: tasks (5 cols)
    # Organised as 3 agent blocks of 2 rows each
    row_labels = []
    data = []
    for agent_key, agent_label in zip(AGENT_KEYS, AGENTS):
        for prompt in ["vague", "specific"]:
            row_labels.append(f"{agent_label}\n({prompt.capitalize()})")
            row = [run_total(agent_key, t, prompt) for t in TASK_KEYS]
            data.append(row)

    data = np.array(data, dtype=float)
    col_labels = ["T1\nIngestion", "T2\nEDA", "T3\nBaseline\nModel",
                  "T4\nLeakage\nDetection", "T5\nDebugging"]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    im = ax.imshow(data, cmap="Blues", vmin=0, vmax=12, aspect="auto")
    ax.grid(False)  # prevent rcParams grid from overlaying the cells

    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=12)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=11)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Annotate cells
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = int(data[i, j])
            text_color = "white" if val >= 9 else "black"
            ax.text(j, i, f"{val}/12", ha="center", va="center",
                    fontsize=12, color=text_color, fontweight="bold")

    # Horizontal separator lines between agent blocks
    for pos in [1.5, 3.5]:
        ax.axhline(pos, color="black", linewidth=1.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Run Score (max 12)", fontsize=12)
    cbar.ax.tick_params(labelsize=11)

    ax.set_title("Per-Run Scores Across All Agents and Tasks", fontsize=14, pad=14)
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig5_heatmap.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig5_heatmap.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig5_heatmap")

# ---------------------------------------------------------------------------
# Figure 6 – Vague vs Specific per task per agent (small multiples)
# ---------------------------------------------------------------------------

def fig_vague_vs_specific_per_task():
    fig, axes = plt.subplots(1, 5, figsize=(13, 4), sharey=True)
    task_labels_long = ["T1 – Ingestion", "T2 – EDA", "T3 – Baseline\nModel",
                        "T4 – Leakage\nDetection", "T5 – Debugging"]

    width = 0.3
    x = np.array([0, 1])  # vague=0, specific=1

    for col, (task_key, task_label) in enumerate(zip(TASK_KEYS, task_labels_long)):
        ax = axes[col]
        for i, (agent_key, agent_label, color, hatch) in enumerate(
                zip(AGENT_KEYS, AGENTS, COLORS, HATCHES)):
            v = run_total(agent_key, task_key, "vague")
            s = run_total(agent_key, task_key, "specific")
            offset = (i - 1) * width
            ax.bar(x + offset, [v, s], width, color=color, edgecolor="black",
                   linewidth=0.7, hatch=hatch, label=agent_label if col == 0 else None)
        ax.set_title(task_label, fontsize=12, pad=6)
        ax.set_xticks(x)
        ax.set_xticklabels(["Vague", "Specific"], fontsize=11)
        ax.set_ylim(0, 14)
        ax.grid(axis="y")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if col == 0:
            ax.set_ylabel("Score (max 12)", fontsize=13)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=12,
               bbox_to_anchor=(0.5, -0.06), framealpha=0.9)
    fig.suptitle("Vague vs. Specific Prompt Scores per Task", fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR + "fig6_vague_vs_specific_per_task.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR + "fig6_vague_vs_specific_per_task.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("Saved fig6_vague_vs_specific_per_task")

# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fig_overall()
    fig_per_task()
    fig_per_prompt()
    fig_radar()
    fig_heatmap()
    fig_vague_vs_specific_per_task()
    print("\nAll figures saved to:", OUT_DIR)
