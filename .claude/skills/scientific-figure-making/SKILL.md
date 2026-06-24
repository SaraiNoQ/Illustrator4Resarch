---
name: scientific-figure-making
description: "Use this skill whenever the user wants to create, polish, or refactor publication-ready scientific figures in Python/Matplotlib. Triggers include scientific figure, paper plot, Nature or IEEE style chart, grouped bar, ablation figure, trend curve, heatmap, scatter plot, color palette, chart style preset, seaborn-like chart, hand-drawn chart, colorblind-safe palette, or research-slide visualization."
compatibility: "Claude Code project-scoped wrapper for the global-installable scientific-figure-making skill. Requires Python 3 with matplotlib and numpy for plotting helpers."
metadata:
  version: "0.5.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  source_skill_path: "skills/scientific-figure-making"
argument-hint: "<figure request, data, venue/style, palette preference, chart style, output paths>"
allowed-tools: "Read Grep Glob Bash(python *) Bash(python3 *)"
---

# Scientific figure making

This is the Claude Code project discovery wrapper. For the complete standalone skill package, read:

```text
skills/scientific-figure-making/SKILL.md
```

That canonical package contains the heuristic palette engine, chart-style preset engine, references, and standalone Python scripts.
