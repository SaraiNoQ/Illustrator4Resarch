# Chart style workflow

Palette and chart style are separate design layers.

- **Palette** controls colors and semantic color roles.
- **Chart style** controls plotting form: fonts, grid, spines, line widths, bar edges, markers, legend framing, sketch effects, and dark/light background.

This separation matters because different journals, conferences, and use cases prefer different chart grammars even when they use the same colors.

## Pipeline

1. Parse the user's request for venue/style/use-case cues, such as `Nature`, `IEEE`, `NeurIPS`, `seaborn whitegrid`, `Matplotlib 默认`, `卡通手绘`, `答辩`, or `深色展示`.
2. Call `resolve_chart_style(...)` to select a chart-style preset.
3. Call `auto_palette(...)` or `auto_figure_design(...)` separately for color selection.
4. Apply the chosen form with `apply_publication_style(FigureStyle(..., chart_style=...))`.
5. Use the selected style only when it fits the figure purpose. For example, `cartoon_handdrawn` is appropriate for explanatory slides, not formal paper main results.

## One-call design

```python
from scientific_figure_skill import auto_figure_design, FigureStyle, apply_publication_style

design = auto_figure_design(
    request="IEEE Transactions 风格，色盲安全，多方法柱状图",
    figure_type="grouped_bar",
    n_colors=5,
)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
)
apply_publication_style(style)
```

## Built-in chart-style presets

### `publication_minimal`

General academic Matplotlib style. Open axes, no decorative grid, high readability. Good default when user gives vague requirements.

### `nature_journal`

Compact high-impact journal style. Restrained axes, small but clean typography, minimal grid. Good for Nature/Science/Cell-like paper panels.

### `ieee_transactions`

Engineering-paper style. Compact fonts, conservative line widths, y-grid, print-safe look. Good for IEEE Transactions figures.

### `acm_conference`

Compact CS conference style. Designed for one-column or two-column conference layouts.

### `neurips_ml`

Modern ML conference style. Clean white background, light y-grid, thicker method curves. Good for NeurIPS/ICML/ICLR-style empirical plots.

### `seaborn_whitegrid`

Seaborn-like whitegrid grammar implemented with Matplotlib rcParams only. Good for statistical exploration or clean report figures. Do not import seaborn unless explicitly requested.

### `seaborn_ticks`

Seaborn-like ticks grammar with cleaner spines and less grid emphasis.

### `boxed_classic`

Classic boxed Matplotlib academic style. Good for conservative reports, legacy paper reproductions, or when the user explicitly wants Matplotlib default/classic style.

### `thesis_clean`

Slightly larger-font report/thesis style, suitable for Word, PowerPoint, or thesis chapters.

### `presentation_large`

Large-font slide style. Use for presentations, defenses, or classroom explanation.

### `cartoon_handdrawn`

Sketch-style chart using Matplotlib path sketching. Use only for explanatory slides or informal conceptual figures.

### `dark_presentation`

Dark-background style for slides/posters. Avoid for formal paper submission unless explicitly requested.

## Decision rules

- Main-paper results: prefer `publication_minimal`, `nature_journal`, `ieee_transactions`, `acm_conference`, or `neurips_ml`.
- Statistical exploratory plots: allow `seaborn_whitegrid` or `seaborn_ticks`.
- Thesis/report figures: use `thesis_clean`.
- Slides: use `presentation_large` or `dark_presentation` if requested.
- Explanatory informal charts: use `cartoon_handdrawn` only when the user asks for a hand-drawn/cartoon style.
- Heatmaps generally do not need dense xy grids because the heatmap cells already define a grid.
- Dense grouped bars benefit from black bar edges and hatch/marker redundancy.
