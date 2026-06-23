---
name: scientific-figure-making
description: Generate publication-ready Python/Matplotlib scientific figures with automatic palette selection from natural-language style requests. Use for paper figures, experimental plots, Nature/IEEE-style charts, grouped bars, ablations, trend curves, heatmaps, scatter plots, or research-slide visualizations.
compatibility: Works as an Agent Skills package for Codex and Claude Code. Requires Python 3, matplotlib, and numpy for executable plotting helpers.
metadata:
  version: "0.3.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
argument-hint: "<figure request, data, style, palette preference>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python *)
  - Bash(python3 *)
---

# Scientific figure making

Use this skill to create or refine publication-ready scientific figures. The objective is accurate, readable, reproducible research visualization, not decorative graphic design.

## Skill package layout

This repository exposes the same skill through three paths:

- `.agents/skills/scientific-figure-making/`: Codex repo-scoped discovery path.
- `.claude/skills/scientific-figure-making/`: Claude Code project-scoped discovery path.
- `skills/scientific-figure-making/`: portable source copy for manual installation, sharing, and synchronization.

The skill body should remain identical across these three locations. If you change one copy, run `python scripts/sync_skill_paths.py` from the repository root.

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

2. If model-side palette judgment is useful, call `build_llm_palette_selection_prompt(...)`, reason over the candidate JSON, choose one palette, then validate the returned JSON with `apply_llm_palette_decision(...)`.

3. If no explicit model decision is needed, use the deterministic `auto_palette(...)` result.

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

Read these files when needed:

- `references/palette-workflow.md`: palette retrieval and decision rules.
- `references/api-usage.md`: Python API examples.
- `scientific_figure_skill/core.py`: importable implementation at repository root.
- `prompt/scientific_figure_prompt.md`: long-form user-facing prompt template at repository root.

## Expected output

For code-generation requests, return or create:

1. Brief design decision summary.
2. Complete runnable Python script.
3. Exact output filenames.
4. Any assumptions about data shape.
5. Suggested validation command.

For repository-modification requests, edit the relevant files and run `python -m pytest -q`.
