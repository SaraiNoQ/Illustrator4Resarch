#!/usr/bin/env python3
"""End-to-end v0.9 verified, style-confirmed, compact-export demo figure."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from figure_design import FigureStyle, apply_publication_style, auto_figure_design
from figure_fonts import select_font_family
from figure_toolkit import finalize_figure, make_grouped_bar


CONFIRMED_CHART_STYLE = "publication_minimal"
DATA_PATH = Path(__file__).with_name("guided_workflow_demo.data.csv")


def load_verified_data() -> tuple[list[str], list[str], np.ndarray]:
    with DATA_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    labels = ["Fed-SOLO", "FedAvg-LoRA", "Local LoRA", "FedReFT"]
    categories = [row["Dataset"] for row in rows]
    values = np.array(
        [[float(row[label]) for row in rows] for label in labels],
        dtype=float,
    )
    return categories, labels, values


def main() -> None:
    request = (
        "Main paper result comparing four methods on four datasets. "
        "Use the recommended general-publication double-column style, "
        "colorblind-safe palette, clean sans-serif typography, grouped bars, "
        "and strong but honest proposed-method emphasis."
    )
    categories, labels, values = load_verified_data()

    design = auto_figure_design(
        request,
        figure_type="grouped_bar",
        n_colors=len(labels),
        data_role="categorical",
        venue="general_publication",
    )
    font_family = select_font_family(
        request=request,
        chart_style=CONFIRMED_CHART_STYLE,
        venue="general_publication",
    )
    apply_publication_style(
        FigureStyle(
            palette=design.palette.colors,
            color_roles=design.palette.color_roles,
            chart_style=CONFIRMED_CHART_STYLE,
            font_family=font_family,
            dpi=300,
        )
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    make_grouped_bar(
        ax,
        categories,
        values,
        labels,
        ylabel="Accuracy / Success Rate (%)",
        colors=design.palette.colors,
        annotate=False,
        edgecolor="#202124",
        linewidth=0.8,
        hatch=["", "//", "..", "\\\\"],
    )
    ax.set_ylim(0, 80)
    ax.set_xlabel("Dataset", fontsize=11)
    ax.set_ylabel("Accuracy / Success Rate (%)", fontsize=11)
    ax.tick_params(axis="both", labelsize=10)
    ax.grid(axis="y", color="#D9DEE7", linewidth=0.7, alpha=0.65)
    ax.grid(axis="x", visible=False)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        fontsize=9,
        handlelength=1.8,
        columnspacing=1.4,
    )
    ax.text(
        0.01,
        0.98,
        "Higher is better",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#50555C",
    )

    output_stem = Path("figures/guided_workflow_demo")
    written = finalize_figure(
        fig,
        output_stem,
        formats=("png", "pdf"),
        dpi=300,
        close=True,
    )
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
