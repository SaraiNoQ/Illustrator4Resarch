---
name: scientific-figure-making
description: "Use this skill whenever the user wants to create, polish, or refactor publication-ready scientific figures in Python/Matplotlib. Triggers include: scientific figure, paper plot, Nature or IEEE style chart, grouped bar, ablation figure, trend curve, convergence plot, heatmap, scatter plot, color palette, colorblind-safe palette, chart style preset, seaborn-like chart, hand-drawn chart, black-and-white print figure, or research-slide visualization. Do not use for general decorative graphic design unrelated to research visualization."
compatibility: "Agent Skills package for Codex, Claude Code, and compatible agents. Requires Python 3 with matplotlib and numpy for executable plotting helpers."
metadata:
  version: "0.5.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  package_type: "global-installable-agent-skill"
  primary_language: "python"
argument-hint: "<figure request, data, venue/style, palette preference, chart style, output paths>"
allowed-tools: "Read Grep Glob Bash(python *) Bash(python3 *)"
---

# Scientific figure making

Use this skill to create or refine publication-ready scientific figures. The objective is accurate, readable, reproducible research visualization, not decorative graphic design.

The current design system has two independent layers:

1. **Palette engine**: selects colors and semantic color roles.
2. **Chart-style engine**: selects plotting form, including grid, spines, linewidths, fonts, legend framing, bar edges, markers, sketch effect, and dark/light background.

Do not confuse these two layers. A Nature-like chart style can use a colorblind palette; an IEEE-style chart can use a warm palette if the user explicitly asks for it.

## Package contents

The skill root contains:

```text
scientific-figure-making/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── api-usage.md
│   ├── global-installation.md
│   ├── palette-workflow.md
│   └── style-workflow.md
├── scripts/
│   ├── figure_design.py      # Heuristic palette + chart-style engine
│   ├── figure_toolkit.py     # Plotting helpers and legacy compatibility
│   └── preview_palette.py    # Palette/style preview CLI
└── examples/
```

When this skill is installed globally outside the Illustrator4Resarch repository, prefer `scripts/figure_design.py` for design decisions and `scripts/figure_toolkit.py` for plotting helpers. When working inside the repository, use the importable package `scientific_figure_skill`.

## Inputs to extract

From the user request, identify:

1. Figure type: grouped bar, ablation bar, trend line, convergence plot, multi-panel comparison, heatmap, scatter plot, schematic, or other.
2. Data structure: method × metric, method × dataset, round × score, matrix, embedding coordinates, or custom.
3. Target venue/style: examples include `Nature科研风格`, `IEEE Transactions`, `NeurIPS/ICML`, `ACM`, `Matplotlib 默认学术风`, `seaborn whitegrid`, `卡通手绘`, `答辩展示`, `深色海报`.
4. Palette requirements: examples include `简洁大气`, `色盲安全`, `黑白打印`, `冷色科技`, `柔和高级`, `暖色叙事`.
5. Number of visually distinct colors needed.
6. Semantic roles: proposed/ours, baseline, secondary comparator, ablation, neutral reference, highlight, uncertainty band.
7. Output path and formats.

## Required workflow

### 1. Prefer one-call design

Inside this repository:

```python
from scientific_figure_skill import auto_figure_design, FigureStyle, apply_publication_style

design = auto_figure_design(
    request="Nature科研风格，简洁大气，色盲安全，适合多方法柱状图",
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

Globally installed skill:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.agents/skills/scientific-figure-making/scripts").expanduser()))
# For Claude Code use: ~/.claude/skills/scientific-figure-making/scripts

from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_toolkit import make_grouped_bar, finalize_figure
```

### 2. Palette-only selection

Use this when the chart form is already fixed:

```python
from scientific_figure_skill import auto_palette
selection = auto_palette("清透克制但没有明确预设关键词", figure_type="grouped_bar", n_colors=5)
```

Palette selection must not be a pure keyword lookup. Use the heuristic engine, which combines request profile inference, objective palette quality metrics, generated variants, and deterministic fallback.

### 3. Chart-style-only selection

Use this when the user asks for a venue or plotting-form style:

```python
from scientific_figure_skill import resolve_chart_style
preset = resolve_chart_style("IEEE Transactions 风格，多方法柱状图", figure_type="grouped_bar")
```

Supported chart-style presets include:

- `publication_minimal`
- `nature_journal`
- `ieee_transactions`
- `acm_conference`
- `neurips_ml`
- `seaborn_whitegrid`
- `seaborn_ticks`
- `boxed_classic`
- `thesis_clean`
- `presentation_large`
- `cartoon_handdrawn`
- `dark_presentation`

### 4. Optional model-side judgment

If the agent needs final judgment, construct two strict JSON prompts:

```python
palette_prompt = design.palette.llm_prompt
chart_style_prompt = design.llm_prompt
```

The model should decide based on scientific readability first, aesthetics second.

## Palette decision rules

- Method comparison / grouped bars / line comparisons: prefer categorical palettes with strong separation and colorblind safety.
- Heatmaps with magnitude-only values: prefer monotone-luminance sequential palettes.
- Signed differences, residuals, centered correlations: prefer diverging palettes.
- Black-and-white print: prefer grayscale palette plus hatching/markers.
- Unknown style phrases should not fail selection; fall back to objective quality scoring.
- `proposed` or `ours`: dominant but non-neon color.
- `baseline`: contrast color or neutral dark gray.
- `ablation`: visually weaker variant, often softer or hatched.
- `highlight`: use once only.

## Chart-style decision rules

- Formal paper figures: prefer `publication_minimal`, `nature_journal`, `ieee_transactions`, `acm_conference`, or `neurips_ml`.
- Nature/Science/Cell-like requests: use compact, minimal-grid high-impact journal form.
- IEEE/engineering requests: use compact, conservative, print-safe form.
- Seaborn requests: use Matplotlib rcParams that imitate whitegrid/ticks without importing seaborn unless explicitly requested.
- Hand-drawn/cartoon requests: use `cartoon_handdrawn` only for explanatory slides or informal conceptual figures.
- Dark backgrounds: use only for slides/posters, not formal paper submissions unless requested.

## Supporting references

Read these files when needed:

- `references/global-installation.md`: installing this skill globally for Codex or Claude Code.
- `references/palette-workflow.md`: heuristic palette selection, generated variants, and fallback rules.
- `references/style-workflow.md`: chart-style presets and venue/form decision rules.
- `references/api-usage.md`: Python API examples.
- `scripts/figure_design.py`: standalone design engine bundled with this skill.
- `scripts/figure_toolkit.py`: plotting helper implementation.
- `scripts/preview_palette.py`: preview palette and chart-style candidates from a natural-language request.

## Expected output

For code-generation requests, return or create:

1. Brief design decision summary.
2. Complete runnable Python script.
3. Exact output filenames.
4. Any assumptions about data shape.
5. Suggested validation command.

For repository-modification requests, edit the relevant files and run `python -m pytest -q` if the Python package or tests are changed.
