---
name: scientific-figure-making
description: Generate publication-ready Python/Matplotlib scientific figures with automatic palette selection from natural-language style requests. Use when the user asks for paper figures, experimental plots, Nature/IEEE-style charts, grouped bars, ablations, trend curves, heatmaps, scatter plots, or research-slide visualizations.
argument-hint: "<figure request, data, style, palette preference>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python *)
  - Bash(python3 *)
---

# Scientific figure making

Use this skill to create or refine publication-ready scientific figures. The goal is not decorative graphic design; the goal is accurate, readable, reproducible research visualization.

## Inputs to extract

From the user request, identify:

1. Figure type: grouped bar, ablation bar, trend line, multi-panel comparison, heatmap, scatter, schematic, or other.
2. Data structure: method × metric, method × dataset, round × score, matrix, embedding coordinates, or custom.
3. Target style: examples include `简洁大气`, `Nature科研风格`, `IEEE风格`, `色盲安全`, `黑白打印`, `科技冷色`, `柔和高级`.
4. Number of visually distinct colors needed.
5. Semantic roles: proposed/ours, baseline, secondary comparator, ablation, neutral reference, highlight, uncertainty band.
6. Output path and formats.

## Required workflow

1. Convert the user's natural-language style request into palette candidates using the local implementation:

```python
from scientific_figure_skill import auto_palette

selection = auto_palette(
    request="Nature科研风格，简洁大气，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=5,
)
```

2. If an LLM-based palette decision is available, call `build_llm_palette_selection_prompt(...)`, pass the candidate JSON to the model, then apply the returned JSON with `apply_llm_palette_decision(...)`.

3. If no external palette decision is available, use the deterministic `auto_palette(...)` result.

4. Build the figure with:

```python
from scientific_figure_skill import FigureStyle, apply_publication_style

style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

5. Use Matplotlib helper functions from `scientific_figure_skill`, or write raw Matplotlib code that follows the same visual rules.

6. Export PNG and PDF unless the user specifies otherwise.

## Palette decision rules

- Method comparison / grouped bars / line comparisons: prefer categorical palettes with strong separation and colorblind safety.
- Heatmaps with magnitude-only values: prefer sequential palettes such as viridis/cividis/blue sequential.
- Signed differences, residuals, centered correlations: prefer diverging palettes.
- Black-and-white print: prefer grayscale palette plus hatching/markers.
- `proposed` or `ours`: dominant but non-neon color.
- `baseline`: contrast color or neutral dark gray.
- `ablation`: visually weaker variant, often softer or hatched.
- `highlight`: use once only; do not turn every method into a highlight.

## Matplotlib style rules

- Use sans-serif fonts: Arial, Helvetica, DejaVu Sans fallback.
- Hide top and right spines.
- Use frameless legends.
- Use explicit line widths and axes widths.
- Preserve editable text in SVG/PDF where possible.
- Use black bar edges for grouped bars when readability matters.
- Do not use seaborn unless explicitly requested.
- Do not use random colors.
- Do not over-compress axes in a misleading way.

## Supporting references

- Palette workflow: `references/palette-workflow.md`
- API usage: `references/api-usage.md`
- Prompt template: `../../../prompt/scientific_figure_prompt.md`
- Python implementation: `../../../scientific_figure_skill/core.py`

## Expected output

For code-generation requests, return:

1. Brief design decision summary.
2. Complete runnable Python script.
3. Exact output filenames.
4. Any assumptions about data shape.
5. Suggested validation command.

For repository-modification requests, edit the relevant files and run `python -m pytest -q`.
