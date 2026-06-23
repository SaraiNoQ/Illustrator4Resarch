# Illustrator4Resarch

Codex-first Agent Skill for generating publication-ready scientific figures with automatic palette selection.

## What this repository is

`Illustrator4Resarch` lets Codex-style coding agents generate Python/Matplotlib scientific figures from natural-language figure requirements. The repository keeps the implementation offline and deterministic: palette candidates are retrieved from a curated local registry, then either selected by the coding agent/LLM or by the built-in `auto_palette(...)` fallback.

The intended workflow is:

1. The user describes a rough visual style, such as `简洁大气`, `Nature 科研风格`, `IEEE 风格`, `色盲安全`, or `黑白打印`.
2. The toolkit retrieves candidate palettes from the local registry.
3. Codex chooses the final palette and semantic role mapping, or calls `auto_palette(...)` to make a deterministic choice.
4. Matplotlib helpers render the final experimental figure.
5. The generated script exports at least PNG and PDF.

## Canonical repository structure

```text
Illustrator4Resarch/
├── AGENTS.md
├── README.md
├── skills/
│   └── scientific-figure-making/
│       ├── SKILL.md
│       ├── references/
│       │   ├── api-usage.md
│       │   └── palette-workflow.md
│       ├── scripts/
│       │   └── preview_palette.py
│       └── examples/
│           ├── minimal_request.md
│           └── codex_prompts.md
├── scientific_figure_skill/
│   ├── __init__.py
│   └── core.py
├── prompt/
│   └── scientific_figure_prompt.md
├── examples/
│   └── auto_palette_demo.py
└── tests/
    └── test_palette_selector.py
```

The canonical skill entrypoint is:

```text
skills/scientific-figure-making/SKILL.md
```

The Claude-specific `.claude/` duplicate and the old single `skill/` duplicate have been removed. For Codex, `AGENTS.md` is the primary instruction file; `skills/scientific-figure-making/SKILL.md` is the reusable skill specification; `scientific_figure_skill/core.py` is the executable implementation.

## Quick start in Codex

Clone the repository and open it in Codex:

```bash
git clone https://github.com/SaraiNoQ/Illustrator4Resarch.git
cd Illustrator4Resarch
```

Then give Codex this instruction:

```text
Read AGENTS.md first. Use the skill at skills/scientific-figure-making/SKILL.md.
I want to generate a publication-ready scientific figure. Follow the repository workflow, use auto_palette for automatic palette selection unless a better LLM palette decision is needed, write complete runnable Python code, export PNG and PDF, and run the validation commands.
```

## Direct Codex prompt: generate one figure

Paste this into Codex and replace the data block:

```text
Read AGENTS.md and use skills/scientific-figure-making/SKILL.md.

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

## Direct Codex prompt: preview palette only

```text
Read AGENTS.md. Use the palette selector from scientific_figure_skill.
For the request "简洁大气，Nature科研风格，适合多方法柱状图", preview the top candidate palettes, explain why the selected palette is suitable, and show the hex colors and semantic roles.
```

Equivalent command:

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

## Direct Codex prompt: integrate into another project

Use this when your target paper/project repository already exists:

```text
Use https://github.com/SaraiNoQ/Illustrator4Resarch as the reference skill repository.
In the current project, add a reusable plotting script that follows Illustrator4Resarch's scientific-figure-making skill.
Do not copy unnecessary folders. Import or vendor only the minimal helper code needed from scientific_figure_skill if the current project does not already depend on it.
Generate the requested figure, save outputs under figures/, and report exact changed files and validation commands.
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
```

For a smoke test of figure generation:

```bash
python examples/auto_palette_demo.py
```

## Notes

The repository intentionally avoids runtime dependence on external palette websites or APIs. The palette registry is local and deterministic so coding agents can work in offline sandboxes.