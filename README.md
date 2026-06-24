# Illustrator4Resarch

Agent Skill for generating publication-ready scientific figures with automatic palette and chart-style design. The repository supports three usage modes:

1. **Global skill install** for Codex and Claude Code.
2. **Repository-scoped discovery** through `.agents/skills/` and `.claude/skills/`.
3. **Reusable Python package** through `scientific_figure_skill/`.

## What this repository is

`Illustrator4Resarch` lets coding agents generate Python/Matplotlib scientific figures from natural-language figure requirements.

The design system now has two independent layers:

1. **Palette engine**: chooses colors and semantic color roles.
2. **Chart-style engine**: chooses plotting form, including font scale, grids, spines, line widths, bar edges, markers, legend framing, and special styles such as seaborn-like or hand-drawn charts.

Palette selection is no longer a brittle keyword-only mapping. The new engine infers a request profile, evaluates palette quality metrics, generates variants such as muted/high-contrast/cool/warm/grayscale versions, and uses a deterministic fallback when the user's wording does not match predefined keywords.

## Repository structure

```text
Illustrator4Resarch/
├── AGENTS.md
├── CLAUDE.md
├── .agents/skills/scientific-figure-making/   # Codex repo-scoped wrapper
├── .claude/skills/scientific-figure-making/   # Claude Code project wrapper
├── skills/scientific-figure-making/           # Standalone global-installable skill package
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── api-usage.md
│   │   ├── global-installation.md
│   │   ├── palette-workflow.md
│   │   └── style-workflow.md
│   ├── scripts/
│   │   ├── figure_design.py
│   │   ├── figure_toolkit.py
│   │   └── preview_palette.py
│   └── examples/
├── scientific_figure_skill/                   # Importable Python implementation for repository development
├── examples/
├── scripts/
└── tests/
```

The canonical standalone skill package is:

```text
skills/scientific-figure-making/
```

This folder is designed to be copied directly to global agent skill directories.

## Global install

Install for both Codex and Claude Code:

```bash
git clone https://github.com/SaraiNoQ/Illustrator4Resarch.git
cd Illustrator4Resarch
python scripts/install_global_skill.py --target both
```

Install only for Codex:

```bash
python scripts/install_global_skill.py --target codex
```

Install only for Claude Code:

```bash
python scripts/install_global_skill.py --target claude
```

## Package for sharing

```bash
python scripts/package_skill.py
```

Output:

```text
dist/scientific-figure-making.zip
```

## Use in Codex after global install

```text
$scientific-figure-making
Task: create a paper-ready grouped bar chart.
Venue/style: Nature-like journal style, compact and clean.
Palette: 简洁大气，色盲安全。
Semantic roles: Fed-SOLO is proposed; FedAvg-LoRA is baseline; Local LoRA is neutral.
Output: create scripts/plot_main_comparison.py and save figures/main_comparison.png and figures/main_comparison.pdf.
Validation: run the plotting script. If library code is changed, run python -m pytest -q.
```

## Use in Claude Code after global install

```text
/scientific-figure-making
请根据下面的数据画一张论文主实验 grouped bar。
图表风格：Nature-like journal style，简洁、紧凑、无重网格。
配色要求：色盲安全，主方法突出，baseline 有对比。
导出 figures/main_comparison.png 和 figures/main_comparison.pdf。
```

## Minimal Python usage inside this repository

```python
from scientific_figure_skill import auto_figure_design, FigureStyle, apply_publication_style

design = auto_figure_design(
    "IEEE Transactions 风格，色盲安全，多方法柱状图",
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

## Preview design selection

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

The preview prints both palette candidates and the selected chart-style preset.

## Available chart-style presets

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

## Repository-scoped use

When working inside this repository, Codex can discover:

```text
.agents/skills/scientific-figure-making/SKILL.md
```

Claude Code can discover:

```text
.claude/skills/scientific-figure-making/SKILL.md
```

Both discovery wrappers point back to the canonical package at `skills/scientific-figure-making/`.
