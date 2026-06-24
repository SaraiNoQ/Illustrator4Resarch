# Agent Instructions

This repository is an Agent Skills project for generating publication-ready scientific figures. It supports:

- Codex repo-scoped discovery through `.agents/skills/scientific-figure-making/`.
- Claude Code project discovery through `.claude/skills/scientific-figure-making/`.
- OpenCode repository-local use through this `AGENTS.md` file plus the canonical skill package.
- Global install through the standalone package at `skills/scientific-figure-making/`.

## Primary objective

Use this project when the user asks a coding agent to create, polish, or refactor Python/Matplotlib figures for papers, theses, reports, tables, or research slides. The skill name is `scientific-figure-making`.

## Design model

The skill has four independent design layers:

1. **Palette engine**: color palette, generated palette variants, semantic color roles, categorical/sequential/diverging/cyclic/print-aware data roles.
2. **Chart-style engine**: venue/form preset, grid, spines, line widths, bar edges, markers, legend framing, background, heatmap, hand-drawn, dark, and presentation effects.
3. **Table-style engine**: paper three-line tables, compact appendix tables, DataFrame-style zebra tables, dashboard tables, editorial tables, and print-safe tables.
4. **Font engine**: publication-safe font candidate registry, style-aware font scoring, and safe sans-serif correction for non-formal styles such as `cartoon_handdrawn`.

Do not reduce chart design to color selection. `Nature科研风格`, `IEEE Transactions`, `seaborn whitegrid`, `ggplot2 theme_minimal`, `Datawrapper editorial`, `Tableau dashboard`, and `卡通手绘` imply different chart forms even if the palette is unchanged. Font choice is also separate: a cute hand-drawn chart should not silently inherit Times New Roman. Table style is separate again: a paper table should usually be three-line/booktabs-like, not a heavy dashboard grid.

## Canonical files

- `skills/scientific-figure-making/SKILL.md`: canonical standalone skill package. Edit this first.
- `skills/scientific-figure-making/scripts/figure_design.py`: heuristic palette, chart-style, and table-style engine.
- `skills/scientific-figure-making/scripts/figure_fonts.py`: global-skill font selection helpers.
- `skills/scientific-figure-making/scripts/figure_toolkit.py`: plotting helpers and legacy compatibility.
- `skills/scientific-figure-making/scripts/preview_palette.py`: palette and style preview CLI.
- `skills/scientific-figure-making/references/api-usage.md`: API examples.
- `skills/scientific-figure-making/references/font-workflow.md`: publication-safe font registry and workflow.
- `skills/scientific-figure-making/references/palette-workflow.md`: palette heuristics and generated variants.
- `skills/scientific-figure-making/references/style-workflow.md`: chart-style presets and venue/form rules.
- `skills/scientific-figure-making/references/table-workflow.md`: table-style presets and rules.
- `.agents/skills/scientific-figure-making/SKILL.md`: Codex repo-scoped wrapper.
- `.claude/skills/scientific-figure-making/SKILL.md`: Claude Code project wrapper.
- `scripts/install_global_skill.py`: installs the skill into user-level global directories.
- `scripts/package_skill.py`: creates `dist/scientific-figure-making.zip`.
- `scripts/sync_skill_paths.py`: syncs the canonical skill into repo-scoped discovery paths.

## Global installation commands

Install for both Codex and Claude Code:

```bash
python scripts/install_global_skill.py --target both
```

Package as a shareable ZIP:

```bash
python scripts/package_skill.py
```

## Codex usage

```text
$scientific-figure-making
Create a publication-ready grouped bar chart.
Chart style: Nature-like compact journal style.
Palette: 简洁大气，色盲安全.
Export PNG and PDF.
```

When working inside this repository, Codex can also read the repo wrapper at `.agents/skills/scientific-figure-making/SKILL.md`.

## Claude Code usage

```text
/scientific-figure-making
请生成一张论文级 grouped bar。
图表风格：IEEE Transactions 紧凑风格。
配色要求：色盲安全，主方法突出。
导出 PNG 和 PDF。
```

When working inside this repository, Claude Code can also read the project wrapper at `.claude/skills/scientific-figure-making/SKILL.md`.

## OpenCode usage

Start OpenCode from the repository root and explicitly point it to the canonical skill package:

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md as the scientific figure skill.
Generate a publication-ready grouped bar chart.
Chart style: 二次元、可爱、手绘风格, but still suitable for an academic paper.
Palette: 清新自然，色盲安全，主方法突出，baseline 有对比。
Export PNG and PDF, then run the plotting script.
```

Use this repository-local workflow for OpenCode because different OpenCode setups may use different command/plugin conventions.

## Figure-generation workflow

1. Parse figure type, data shape, venue/chart style, palette preference, semantic roles, table style if applicable, and output paths.
2. Prefer `auto_figure_design(...)` from `scientific_figure_skill` inside the repo, or `figure_design.py` from the global skill path.
3. Use `FigureStyle(..., palette=design.palette.colors, chart_style=design.chart_style)` and `apply_publication_style(...)`.
4. Use `make_grouped_bar(...)`, `make_trend(...)`, `make_heatmap(...)`, `apply_table_style(...)`, or raw Matplotlib as needed.
5. Export PNG and PDF unless the user asks otherwise.
6. Run the generated plotting script.
7. If Python package logic changes, run `python -m pytest -q`.

## Quality rules

- Do not use random colors.
- Do not rely only on exact keyword matching.
- Prefer generated palette variants only when they improve readability or fit.
- Do not confuse palette with chart style.
- Do not confuse table style with chart style.
- Do not use seaborn unless explicitly requested; use seaborn-like Matplotlib presets instead.
- Prefer semantic color roles: proposed, baseline, secondary, ablation, neutral, highlight.
- Use the publication-safe font registry; do not use Times New Roman for cute, anime, hand-drawn, or informal chart styles.
- For heatmaps, choose sequential or diverging palettes according to the data semantics.
- For phase, angle, or periodic data, use cyclic palettes.
- For black-and-white print, use grayscale plus hatching or marker styles.
- For paper tables, prefer three-line/booktabs-like sparse rules.
- Always provide exact output paths.
