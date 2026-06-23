# Claude Code Instructions

This repository provides a project skill for Claude Code:

```text
.claude/skills/scientific-figure-making/SKILL.md
```

Use `/scientific-figure-making` when the user asks to create, polish, or refactor publication-ready scientific figures.

## How to call the skill in Claude Code

```text
/scientific-figure-making
请根据下面的数据生成论文主实验 grouped bar。
风格：简洁大气，Nature科研风格，色盲安全。
要求：自动选择 palette，导出 PNG 和 PDF。
```

Claude Code can also invoke the skill implicitly when the user asks for paper figures, experimental plots, Nature/IEEE-style charts, ablation figures, trend curves, heatmaps, or research-slide figures.

## Required workflow

1. Read `.claude/skills/scientific-figure-making/SKILL.md`.
2. Use `scientific_figure_skill.auto_palette(...)` unless the user explicitly provides colors.
3. Generate complete runnable Python/Matplotlib code.
4. Export at least PNG and PDF for paper figures.
5. Run the generated script.
6. If library code or tests changed, run `python -m pytest -q`.

## Synchronization rule

The portable source skill is:

```text
skills/scientific-figure-making/
```

After editing the portable skill, synchronize both Codex and Claude Code discovery paths:

```bash
python scripts/sync_skill_paths.py
```

Do not delete `.agents/skills/` or `.claude/skills/`; they are required for Codex and Claude Code discovery respectively.
