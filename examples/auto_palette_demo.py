import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scientific_figure_skill import (
    auto_palette,
    FigureStyle,
    apply_publication_style,
    make_grouped_bar,
    dynamic_ylim,
    finalize_figure,
)

selection = auto_palette("简洁大气，Nature 科研风格，适合多方法柱状图", "grouped_bar", n_colors=4)
print(selection)

style = FigureStyle(
    font_size=18,
    axes_linewidth=2.5,
    palette=selection.colors,
    color_roles={
        "Fed-SOLO": "proposed",
        "FedAvg-LoRA": "baseline",
        "FedReFT": "secondary",
        "Local LoRA": "neutral",
    },
)
apply_publication_style(style)

categories = ["GSM8K", "MATH", "HotpotQA", "WebShop"]
labels = ["Fed-SOLO", "FedAvg-LoRA", "FedReFT", "Local LoRA"]
series = np.array([
    [72.4, 41.8, 68.2, 58.0],
    [68.1, 38.7, 64.5, 54.2],
    [69.5, 39.9, 65.8, 55.1],
    [63.0, 34.9, 61.3, 49.8],
])

fig, ax = plt.subplots(figsize=(12, 4.5))
make_grouped_bar(
    ax,
    categories,
    series,
    labels,
    ylabel="Accuracy / Success Rate (%)",
    palette=selection.colors,
    color_roles=style.color_roles,
    annotate=True,
    hatch=True,
)
ax.set_ylim(*dynamic_ylim(series, lower=30))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=4)
finalize_figure(fig, "figures/auto_palette_demo")
