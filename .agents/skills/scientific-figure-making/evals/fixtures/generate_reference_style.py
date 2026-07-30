#!/usr/bin/env python3
"""Generate the deterministic visual-reference fixture used by style-intake evals."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": ["DejaVu Sans", "sans-serif"],
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "pdf.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=(5.4, 3.0), facecolor="#FAFAF7")
    ax.set_facecolor("#FAFAF7")

    datasets = ["Set A", "Set B", "Set C", "Set D"]
    baseline = [72.0, 64.5, 58.0, 69.0]
    proposed = [76.5, 69.0, 63.2, 73.8]
    ax.plot(
        datasets,
        baseline,
        color="#9AA0A6",
        marker="o",
        linewidth=1.6,
        label="Baseline",
    )
    ax.plot(
        datasets,
        proposed,
        color="#087E8B",
        marker="D",
        linewidth=2.4,
        label="Proposed",
    )
    ax.set_ylabel("Score (%)")
    ax.grid(axis="y", color="#D9DEDC", linewidth=0.7, alpha=0.8)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2)
    ax.tick_params(length=3, width=0.7)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.79, bottom=0.18)

    output = Path(__file__).with_name("reference-style.png")
    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
