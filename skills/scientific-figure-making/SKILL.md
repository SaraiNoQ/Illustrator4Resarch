---
name: scientific-figure-making
description: "Use this skill whenever the user wants to create, polish, or refactor publication-ready scientific figures in Python/Matplotlib. Triggers include: scientific figure, paper plot, Nature or IEEE style chart, grouped bar, ablation figure, trend curve, convergence plot, heatmap, scatter plot, color palette, colorblind-safe palette, black-and-white print figure, or research-slide visualization. Do not use for general decorative graphic design unrelated to research visualization."
compatibility: "Agent Skills package for Codex, Claude Code, and compatible agents. Requires Python 3 with matplotlib and numpy for executable plotting helpers."
metadata:
  version: "0.4.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  package_type: "global-installable-agent-skill"
  primary_language: "python"
argument-hint: "<figure request, data, style, palette preference, output paths>"
allowed-tools: "Read Grep Glob Bash(python *) Bash(python3 *)"
---

# Scientific figure making

Use this skill to create or refine publication-ready scientific figures. The objective is accurate, readable, reproducible research visualization, not decorative graphic design.

This skill is designed as a standalone Agent Skills package. It can live in a project repository, in the Codex user skill directory, or in the Claude Code personal skill directory.

## Package contents

The skill root contains:

```text
scientific-figure-making/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml              # Optional Codex UI metadata
├── references/
│   ├── api-usage.md
│   ├── global-installation.md
│   └── palette-workflow.md
├── scripts/
│   ├── figure_toolkit.py        # Standalone helper implementation
│   └── preview_palette.py       # Palette preview CLI
└── examples/
    └── codex_prompts.md
```

When this skill is installed globally outside the Illustrator4Resarch repository, prefer the standalone helper at `scripts/figure_toolkit.py`. When working inside the repository, the importable package `scientific_figure_skill` is also available.

## Inputs to extract

From the user request, identify:

1. Figure type: grouped bar, ablation bar, trend line, convergence plot, multi-panel comparison, heatmap, scatter plot, schematic, or other.
2. Data structure: method × metric, method × dataset, round × score, matrix, embedding coordinates, or custom.
3. Target style: examples include `简洁大气`, `Nature科研风格`, `IEEE风格`, `色盲安全`, `黑白打印`, `科技冷色`, `柔和高级`.
4. Number of visually distinct colors needed.
5. Semantic roles: proposed/ours, baseline, secondary comparator, ablation, neutral reference, highlight, uncertainty band.
6. Output path and formats.

## Required workflow

1. Convert the user's natural-language style request into palette candidates. If inside this repository, use:

```python
from scientific_figure_skill import auto_palette

selection = auto_palette(
    request="Nature科研风格，简洁大气，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=5,
)
```

If the skill is installed globally and the repository package is not available, use the standalone helper:

```python
import sys
from pathlib import Path

# Replace this with the actual skill scripts directory if writing a generated script outside the skill folder.
sys.path.insert(0, str(Path("~/.claude/skills/scientific-figure-making/scripts").expanduser()))
# For Codex global installs, use: ~/.agents/skills/scientific-figure-making/scripts

from figure_toolkit import auto_palette

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
from figure_toolkit import FigureStyle, apply_publication_style

style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

5. Use helper functions such as `make_grouped_bar(...)`, `make_trend(...)`, and `make_heatmap(...)`, or write raw Matplotlib code following the same visual rules.

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

- `references/global-installation.md`: installing this skill globally for Codex or Claude Code.
- `references/palette-workflow.md`: palette retrieval and decision rules.
- `references/api-usage.md`: Python API examples.
- `scripts/figure_toolkit.py`: standalone implementation bundled with this skill.
- `scripts/preview_palette.py`: preview palette candidates from a natural-language style request.

## Expected output

For code-generation requests, return or create:

1. Brief design decision summary.
2. Complete runnable Python script.
3. Exact output filenames.
4. Any assumptions about data shape.
5. Suggested validation command.

For repository-modification requests, edit the relevant files and run `python -m pytest -q` if the Python package or tests are changed.