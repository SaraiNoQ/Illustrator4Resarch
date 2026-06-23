# Illustrator4Resarch

Agent Skill for generating publication-ready scientific figures with automatic palette selection. The repository now supports three usage modes:

1. **Global skill install** for Codex and Claude Code.
2. **Repository-scoped discovery** through `.agents/skills/` and `.claude/skills/`.
3. **Reusable Python package** through `scientific_figure_skill/`.

## What this repository is

`Illustrator4Resarch` lets coding agents generate Python/Matplotlib scientific figures from natural-language figure requirements. Palette selection is offline and deterministic by default: candidate palettes are retrieved from a curated local registry, then either selected by the agent/LLM or by the built-in `auto_palette(...)` fallback.

The intended workflow is:

1. The user describes a rough visual style, such as `简洁大气`, `Nature 科研风格`, `IEEE 风格`, `色盲安全`, or `黑白打印`.
2. The toolkit retrieves candidate palettes from the local registry.
3. The agent chooses the final palette and semantic role mapping, or calls `auto_palette(...)` to make a deterministic choice.
4. Matplotlib helpers render the final experimental figure.
5. The generated script exports at least PNG and PDF.

## Repository structure

```text
Illustrator4Resarch/
├── AGENTS.md                              # General/Codex agent instructions
├── CLAUDE.md                              # Claude Code project notes
├── .agents/skills/scientific-figure-making/   # Codex repo-scoped discovery wrapper
├── .claude/skills/scientific-figure-making/   # Claude Code project discovery wrapper
├── skills/scientific-figure-making/           # Standalone global-installable skill package
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── api-usage.md
│   │   ├── global-installation.md
│   │   └── palette-workflow.md
│   ├── scripts/
│   │   ├── figure_toolkit.py
│   │   └── preview_palette.py
│   └── examples/
├── scientific_figure_skill/                # Importable Python implementation for repository development
├── examples/
├── scripts/
│   ├── install_global_skill.py
│   ├── package_skill.py
│   └── sync_skill_paths.py
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

Manual install paths:

```bash
# Codex user-level skill
mkdir -p ~/.agents/skills
cp -R skills/scientific-figure-making ~/.agents/skills/scientific-figure-making

# Claude Code personal skill
mkdir -p ~/.claude/skills
cp -R skills/scientific-figure-making ~/.claude/skills/scientific-figure-making
rm -rf ~/.claude/skills/scientific-figure-making/agents
```

After a new global install, restart Codex or Claude Code if the skill directory did not exist when the session started.

## Package for sharing

Create a zip archive similar to official skill packages:

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
Style: 简洁大气，Nature 科研风格，色盲安全。
Semantic roles: Fed-SOLO is proposed; FedAvg-LoRA is baseline; Local LoRA is neutral.
Output: create scripts/plot_main_comparison.py and save figures/main_comparison.png and figures/main_comparison.pdf.
Validation: run the plotting script. If library code is changed, run python -m pytest -q.

Data:
Datasets: GSM8K, MATH, HotpotQA, WebShop
Metric: Accuracy / Success Rate (%)
Fed-SOLO: 72.4, 41.8, 68.2, 58.0
FedAvg-LoRA: 68.1, 38.7, 64.5, 54.2
Local LoRA: 63.0, 34.9, 61.3, 49.8
FedReFT: 66.2, 37.1, 63.8, 52.5
```

## Use in Claude Code after global install

```text
/scientific-figure-making
请根据下面的数据画一张论文主实验 grouped bar。
风格：简洁大气，Nature科研风格，色盲安全。
Fed-SOLO 是 proposed，FedAvg-LoRA 是 baseline。
导出 figures/main_comparison.png 和 figures/main_comparison.pdf。
```

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

## Palette preview

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

Global install examples:

```bash
python ~/.agents/skills/scientific-figure-making/scripts/preview_palette.py "Nature科研风格" --figure-type grouped_bar
python ~/.claude/skills/scientific-figure-making/scripts/preview_palette.py "Nature科研风格" --figure-type grouped_bar
```

## Minimal Python usage inside this repository

```python
from scientific_figure_skill import auto_palette, FigureStyle, apply_publication_style

selection = auto_palette(
    "简洁大气，Nature 科研风格，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=4,
)

style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

## Minimal Python usage from a global skill install

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.agents/skills/scientific-figure-making/scripts").expanduser()))

from figure_toolkit import auto_palette, FigureStyle, apply_publication_style
```

For Claude Code global installs, replace `~/.agents/skills` with `~/.claude/skills`.

## Tests

```bash
python -m pytest -q
python examples/auto_palette_demo.py
python skills/scientific-figure-making/scripts/preview_palette.py "Nature科研风格" --figure-type grouped_bar
```

## Notes

The repository intentionally avoids runtime dependence on external palette websites or APIs. The palette registry is local and deterministic so coding agents can work in offline sandboxes.