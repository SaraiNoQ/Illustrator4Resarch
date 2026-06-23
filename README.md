# Illustrator4Resarch

Agent Skill for generating publication-ready scientific figures with automatic palette selection. The repository supports both Codex and Claude Code, while keeping the Python plotting implementation reusable outside any specific agent.

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
├── AGENTS.md                              # Codex/general coding-agent instructions
├── CLAUDE.md                              # Claude Code project memory and usage notes
├── .agents/
│   └── skills/
│       └── scientific-figure-making/       # Codex repo-scoped discovery path
│           ├── SKILL.md
│           ├── agents/openai.yaml
│           ├── references/
│           └── scripts/
├── .claude/
│   └── skills/
│       └── scientific-figure-making/       # Claude Code project-scoped discovery path
│           ├── SKILL.md
│           ├── references/
│           └── scripts/
├── skills/
│   └── scientific-figure-making/           # Portable source copy of the skill
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/
│       ├── scripts/
│       └── examples/
├── scientific_figure_skill/                # Importable Python implementation
├── prompt/
├── examples/
├── scripts/
│   └── sync_skill_paths.py
└── tests/
```

The three skill copies have different purposes:

- `.agents/skills/scientific-figure-making/` is the Codex auto-discovery copy.
- `.claude/skills/scientific-figure-making/` is the Claude Code project skill copy.
- `skills/scientific-figure-making/` is the portable source copy for manual installation, sharing, and synchronization.

When editing the skill, modify `skills/scientific-figure-making/` first, then run:

```bash
python scripts/sync_skill_paths.py
```

## Quick start in Codex

Clone the repository and open it in Codex:

```bash
git clone https://github.com/SaraiNoQ/Illustrator4Resarch.git
cd Illustrator4Resarch
```

Then give Codex this instruction:

```text
Read AGENTS.md. Use the repo-scoped skill at .agents/skills/scientific-figure-making/SKILL.md.
Create a publication-ready scientific figure. Use auto_palette for automatic palette selection unless a better model-side palette decision is needed. Write complete runnable Python code, export PNG and PDF, and run the validation commands.
```

Codex can also be prompted directly with the skill name when available:

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

## Quick start in Claude Code

Open the repository in Claude Code:

```bash
git clone https://github.com/SaraiNoQ/Illustrator4Resarch.git
cd Illustrator4Resarch
claude
```

Then invoke the project skill explicitly:

```text
/scientific-figure-making
请根据下面的数据画一张论文主实验 grouped bar。
风格：简洁大气，Nature科研风格，色盲安全。
Fed-SOLO 是 proposed，FedAvg-LoRA 是 baseline。
导出 figures/main_comparison.png 和 figures/main_comparison.pdf。
```

If Claude Code does not list the skill, restart the Claude Code session after cloning or after changing `.claude/skills/`.

## Palette preview

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

The same script also works from the Codex and Claude discovery copies:

```bash
python .agents/skills/scientific-figure-making/scripts/preview_palette.py "Nature科研风格" --figure-type grouped_bar
python .claude/skills/scientific-figure-making/scripts/preview_palette.py "Nature科研风格" --figure-type grouped_bar
```

## Minimal Python usage

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

## Tests

```bash
python -m pytest -q
python examples/auto_palette_demo.py
```

## Notes

The repository intentionally avoids runtime dependence on external palette websites or APIs. The palette registry is local and deterministic so coding agents can work in offline sandboxes.
