# Illustrator4Resarch

<p align="center">
  <strong>Agent skill for publication-ready scientific figures.</strong><br />
  Turn natural-language research plotting requests into clean, reproducible Matplotlib figures.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" />
  <img alt="Matplotlib" src="https://img.shields.io/badge/Matplotlib-ready-11557C" />
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-scientific--figure--making-7C3AED" />
  <img alt="Codex" src="https://img.shields.io/badge/Codex-supported-111827" />
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-supported-D97706" />
  <img alt="OpenCode" src="https://img.shields.io/badge/OpenCode-supported-2563EB" />
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#agent-workflows">Agent Workflows</a> ·
  <a href="#what-it-does">What it does</a> ·
  <a href="#python-api">Python API</a> ·
  <a href="#repository-layout">Repository Layout</a>
</p>

---

## What it does

`Illustrator4Resarch` is a reusable agent skill for creating, polishing, and refactoring Python/Matplotlib figures for papers, theses, reports, and research slides.

It is designed for the workflow researchers actually use: describe the chart, data, venue/style preference, palette constraints, highlighted method, output paths, and validation requirements; the agent then produces a plotting script plus exported `.png` and `.pdf` figures.

| Layer | Responsibility | Examples |
| --- | --- | --- |
| Palette engine | Selects colorblind-safe palettes and semantic roles | proposed method, baseline, ablation, neutral, highlight |
| Chart-style engine | Selects plotting form and publication aesthetics | Nature-like, IEEE Transactions, NeurIPS, seaborn-like, thesis clean |
| Font engine | Selects publication-safe font stacks from a controlled registry | Arial/Helvetica for formal styles; Trebuchet/Verdana-like sans fonts for cute hand-drawn styles |
| Plotting helpers | Provides reusable Matplotlib wrappers | grouped bar, trend curve, heatmap, scatter-style figures |

The important design choice is that **palette, chart style, and font selection are separate decisions**. A “cute hand-drawn anime style” figure should not silently inherit Times New Roman just because the manuscript uses a formal paper template.

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/SaraiNoQ/Illustrator4Resarch.git
cd Illustrator4Resarch
python -m pip install -e .
```

### 2. Install the global skill for Codex or Claude Code

Install for both tools:

```bash
python scripts/install_global_skill.py --target both
```

Install for Codex only:

```bash
python scripts/install_global_skill.py --target codex
```

Install for Claude Code only:

```bash
python scripts/install_global_skill.py --target claude
```

The installer is idempotent. If the target skill directory already exists, it removes the old installation first and then copies the current canonical skill package.

### 3. Use it immediately

Use this test request after installation:

```text
请根据下面的数据画一张论文主实验 grouped bar。
图表风格：二次元、可爱、手绘风格。
配色要求：清新自然，色盲安全，主方法突出，baseline 有对比。
导出 figures/main_comparison.png 和 figures/main_comparison.pdf。
实验数据如下
Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy / Success Rate (%)
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5
```

For this style, the font engine should choose a publication-safe non-serif stack instead of Times New Roman.

## Agent Workflows

### Claude Code

After global installation:

```text
/scientific-figure-making
请生成一张论文级 grouped bar。
图表风格：Nature-like journal style，简洁、紧凑、无重网格。
配色要求：色盲安全，主方法突出，baseline 有对比。
导出 figures/main_comparison.png 和 figures/main_comparison.pdf。
```

Inside this repository, Claude Code can also discover the project wrapper at:

```text
.claude/skills/scientific-figure-making/SKILL.md
```

### Codex

After global installation:

```text
$scientific-figure-making
Task: create a paper-ready grouped bar chart.
Venue/style: IEEE Transactions compact style.
Palette: colorblind-safe, proposed method highlighted, baselines visually distinct.
Output: create scripts/plot_main_comparison.py and save figures/main_comparison.png and figures/main_comparison.pdf.
Validation: run the plotting script. If library code is changed, run python -m pytest -q.
```

Inside this repository, Codex can also discover the repo-scoped wrapper at:

```text
.agents/skills/scientific-figure-making/SKILL.md
```

### OpenCode

OpenCode can use the repository-scoped workflow without a separate global skill install. Start OpenCode from the repository root, then point it to the canonical skill package:

```bash
opencode
```

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md as the figure-generation skill.
Create a publication-ready grouped bar chart from the data below.
Chart style: 二次元、可爱、手绘风格, but still suitable for an academic paper.
Palette: fresh, natural, colorblind-safe; highlight the proposed method.
Output: figures/main_comparison.png and figures/main_comparison.pdf.
Validation: run the plotting script and fix any rendering issues.
```

The OpenCode path is intentionally repository-local: it relies on `AGENTS.md` plus the canonical skill folder, so it works even when different OpenCode setups use different command/plugin conventions.

## Python API

Use the importable package when developing inside this repository:

```python
from scientific_figure_skill import (
    FigureStyle,
    apply_publication_style,
    auto_figure_design,
    select_font_family,
)

request = "二次元、可爱、手绘风格，色盲安全，多方法 grouped bar"

design = auto_figure_design(
    request,
    figure_type="grouped_bar",
    n_colors=4,
)

font_family = select_font_family(
    request=request,
    chart_style=design.chart_style,
)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
    font_family=font_family,
)

apply_publication_style(style)
```

Preview design selection from the standalone skill package:

```bash
python skills/scientific-figure-making/scripts/preview_palette.py \
  "简洁大气，Nature科研风格" \
  --figure-type grouped_bar \
  --n-colors 5
```

The preview prints the selected palette, chart-style preset, and related design metadata.

## Available Chart-Style Presets

| Preset | Typical use |
| --- | --- |
| `publication_minimal` | General clean paper figure |
| `nature_journal` | Compact, refined journal style |
| `ieee_transactions` | Dense engineering paper figure |
| `acm_conference` | Conference-ready CS figure |
| `neurips_ml` | ML paper figure with clean grid discipline |
| `seaborn_whitegrid` | Seaborn-like whitegrid without depending on seaborn |
| `seaborn_ticks` | Seaborn-like ticks style |
| `boxed_classic` | Traditional boxed axes |
| `thesis_clean` | Thesis/report figure |
| `presentation_large` | Slides and talks |
| `cartoon_handdrawn` | Cute, hand-drawn, anime-inspired academic chart |
| `dark_presentation` | Dark background presentation figure |

## Repository Layout

```text
Illustrator4Resarch/
├── AGENTS.md
├── CLAUDE.md
├── .agents/skills/scientific-figure-making/   # Codex repo-scoped wrapper
├── .claude/skills/scientific-figure-making/   # Claude Code project wrapper
├── skills/scientific-figure-making/           # Canonical standalone skill package
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── api-usage.md
│   │   ├── font-workflow.md
│   │   ├── global-installation.md
│   │   ├── palette-workflow.md
│   │   └── style-workflow.md
│   ├── scripts/
│   │   ├── figure_design.py
│   │   ├── figure_fonts.py
│   │   ├── figure_toolkit.py
│   │   └── preview_palette.py
│   └── examples/
├── scientific_figure_skill/                   # Importable Python implementation
├── examples/
├── scripts/
└── tests/
```

The canonical standalone skill package is:

```text
skills/scientific-figure-making/
```

This folder is copied into global agent skill directories by `scripts/install_global_skill.py` and can also be packaged as a ZIP:

```bash
python scripts/package_skill.py
```

Output:

```text
dist/scientific-figure-making.zip
```

## Development

Run the test suite:

```bash
python -m pytest -q
```

Recommended checks after changing skill logic:

```bash
python -m pytest -q tests/test_font_selection.py
python -m pytest -q tests/test_install_global_skill.py
python -m pytest -q
```

Core quality rules:

- Do not use random colors.
- Do not confuse palette choice with chart-style choice.
- Use controlled, publication-safe font families.
- Export vector-friendly PDF and high-resolution PNG unless the user asks otherwise.
- Run the generated plotting script and fix rendering issues before returning the final figure.
