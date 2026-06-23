---
name: scientific-figure-making
description: "Use this skill whenever the user wants to create, polish, or refactor publication-ready scientific figures in Python/Matplotlib. Triggers include scientific figure, paper plot, Nature or IEEE style chart, grouped bar, ablation figure, trend curve, heatmap, scatter plot, color palette, colorblind-safe palette, black-and-white print figure, or research-slide visualization."
compatibility: "Codex repo-scoped wrapper for the global-installable scientific-figure-making skill. Requires Python 3 with matplotlib and numpy for plotting helpers."
metadata:
  version: "0.4.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  source_skill_path: "skills/scientific-figure-making"
argument-hint: "<figure request, data, style, palette preference, output paths>"
allowed-tools: "Read Grep Glob Bash(python *) Bash(python3 *)"
---

# Scientific figure making

This is the Codex repo-scoped discovery wrapper. For the complete standalone skill package, read:

```text
skills/scientific-figure-making/SKILL.md
```

Use the skill to create or refine publication-ready Python/Matplotlib scientific figures with automatic palette selection.

## Workflow

1. Read `skills/scientific-figure-making/SKILL.md` for the full instructions.
2. Use `skills/scientific-figure-making/scripts/figure_toolkit.py` when a self-contained helper is needed.
3. Use `scientific_figure_skill/` when working inside this repository and importing the maintained package is more convenient.
4. Export at least PNG and PDF.
5. If code in this repository changes, run `python -m pytest -q`.

## Useful files

- `skills/scientific-figure-making/references/global-installation.md`
- `skills/scientific-figure-making/references/api-usage.md`
- `skills/scientific-figure-making/references/palette-workflow.md`
- `skills/scientific-figure-making/scripts/preview_palette.py`
