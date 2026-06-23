# Codex Agent Instructions

This repository is a Codex-first Agent Skill project for generating publication-ready scientific figures.

## Primary objective

Use this project when the user asks a coding agent to create, polish, or refactor Python/Matplotlib figures for papers, theses, reports, or research slides. The canonical skill is `scientific-figure-making`.

## Canonical files

- `skills/scientific-figure-making/SKILL.md`: the skill entrypoint. Read this before generating a figure.
- `skills/scientific-figure-making/references/api-usage.md`: API examples for palette selection and rendering.
- `skills/scientific-figure-making/references/palette-workflow.md`: palette retrieval and decision rules.
- `skills/scientific-figure-making/examples/codex_prompts.md`: copyable Codex prompts.
- `scientific_figure_skill/core.py`: importable Python implementation.
- `prompt/scientific_figure_prompt.md`: reusable user-facing prompt template.
- `examples/auto_palette_demo.py`: smoke-test script.
- `tests/test_palette_selector.py`: regression tests.

Do not use `.claude/skills/` or `skill/`; those duplicate directories were intentionally removed. This repository now uses `skills/` as the only skill directory.

## How Codex should use this repository

When a user asks for a scientific figure, perform this workflow:

1. Read this file, then read `skills/scientific-figure-making/SKILL.md`.
2. Extract the figure type, data shape, method names, metric names, target style, semantic roles, output filenames, and required formats.
3. Use `scientific_figure_skill.auto_palette(...)` to convert the user's natural-language style request into a palette selection.
4. If the prompt requires model-side palette judgment, call `suggest_palettes(...)`, construct the palette decision prompt with `build_llm_palette_selection_prompt(...)`, choose one candidate, then validate the decision with `apply_llm_palette_decision(...)`.
5. Generate complete runnable Python code. Do not return pseudocode.
6. Save scripts under `scripts/` when creating a new figure for this repository, unless the user specifies another location.
7. Save figure outputs under `figures/`, unless the user specifies another location.
8. Export at least `.png` and `.pdf` for paper figures.
9. Run the generated plotting script.
10. If library code or tests changed, run `python -m pytest -q`.
11. Report the selected palette name, hex colors, semantic color-role mapping, output files, and validation commands.

## Minimal code pattern

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scientific_figure_skill import (
    auto_palette,
    FigureStyle,
    apply_publication_style,
    make_grouped_bar,
    finalize_figure,
)

selection = auto_palette(
    request="简洁大气，Nature科研风格，色盲安全",
    figure_type="grouped_bar",
    n_colors=4,
)

style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)

# Build figure here, then:
# finalize_figure(fig, "figures/main_comparison", formats=["png", "pdf"])
```

## Prompt template for Codex users

Users can paste this directly into Codex:

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

Task: generate a publication-ready scientific figure.
Figure type: <grouped_bar | ablation_bar | line | heatmap | scatter | multi_panel>.
Style: <简洁大气 / Nature科研风格 / IEEE风格 / 色盲安全 / 黑白打印 / 科技冷色>.
Semantic roles: <which method is proposed, baseline, ablation, neutral, highlight>.
Data: <paste structured data>.
Output: create scripts/<plot_name>.py and save figures/<plot_name>.png and figures/<plot_name>.pdf.
Validation: run the plotting script. If library code changed, run python -m pytest -q.
```

## Palette policy

- Method comparisons, grouped bars, and multi-line comparisons: use categorical palettes with clear separation.
- Heatmaps with magnitude-only scalar values: use sequential palettes such as `viridis_sample`, `cividis_sample`, or `blue_sequential`.
- Signed differences, residuals, or centered correlations: use diverging palettes such as `blue_orange_diverging`.
- Black-and-white print: use `print_gray` and add hatching, marker, or linestyle encodings.
- `proposed` / `ours`: dominant but non-neon color.
- `baseline`: contrast color or dark neutral.
- `ablation`: weaker variant; prefer softer color, alpha, hatch, or linestyle.
- `highlight`: use at most once.

## Coding conventions

- Keep the public API dependency-light: Python + Matplotlib + NumPy.
- Do not introduce seaborn, Plotly, Bokeh, or web dependencies unless the user explicitly asks.
- Keep color logic deterministic when no external LLM decision is supplied.
- Preserve backwards compatibility for `from scientific_figure_skill import *`.
- Do not use random colors.
- Do not hide important differences through careless axis scaling, but also do not force zero baselines when doing so destroys the visual signal for bounded metrics.

## Quality gate

Before committing non-documentation changes, run:

```bash
python -m pytest -q
```

For a smoke test of figure generation, run:

```bash
python examples/auto_palette_demo.py
```

For palette preview, run:

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```