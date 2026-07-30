#!/usr/bin/env python3
"""Generate table and chart screenshot fixtures for data-intake evals."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
ROWS = [
    ["CIFAR-10", "Baseline", "84.2", "0.8"],
    ["CIFAR-10", "Proposed", "89.8", "0.4"],
    ["CIFAR-100", "Baseline", "61.5", "1.2"],
    ["CIFAR-100", "Proposed", "69.3", "0.7"],
]


def make_table() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.axis("off")
    table = ax.table(
        cellText=ROWS,
        colLabels=["Dataset", "Method", "Accuracy (%)", "Error"],
        cellLoc="center",
        colLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 1.45)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#C8CDD5")
        cell.set_linewidth(0.7)
        if row == 0:
            cell.set_facecolor("#E9EEF5")
            cell.set_text_props(weight="bold")
    fig.savefig(
        ROOT / "results-table.png",
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def make_chart() -> None:
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    labels = ["Baseline", "Proposed"]
    values = [84.2, 89.8]
    ax.bar(labels, values, color=["#8C96A5", "#197D8C"])
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("CIFAR-10 result")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(
        ROOT / "chart-screenshot.png",
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


if __name__ == "__main__":
    make_table()
    make_chart()
