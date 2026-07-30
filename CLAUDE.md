# Claude Code Instructions

This repository provides a Claude Code-compatible skill named `scientific-figure-making`.

## Personal/global install

Install the skill so it is available in all Claude Code projects:

```bash
python scripts/install_global_skill.py --target claude
```

This writes:

```text
~/.claude/skills/scientific-figure-making/SKILL.md
```

After a first-time install, restart Claude Code if the skill directory did not exist before the session started.

Invoke globally:

```text
/scientific-figure-making
results.csv 包含论文主实验结果，请你决定最合适的图表和投稿级设计。
Ours 是本文方法；普通视觉要求使用合理默认值。
生成 PNG/PDF 后检查实际图片并修复问题。
```

## Project-scoped use

Inside this repository, Claude Code can also discover the project wrapper:

```text
.claude/skills/scientific-figure-making/SKILL.md
```

That wrapper points to the complete standalone package:

```text
skills/scientific-figure-making/SKILL.md
```

## What Claude should do when the skill is used

1. Accept incomplete requests and infer guided, direct, refinement, or multi-panel mode.
2. Inspect inputs and create a Figure Brief before coding.
3. Ask only about ambiguities that change scientific meaning; use documented defaults for presentation.
4. Choose the chart from the research message and record a Figure Spec.
5. Treat palette, chart style, table style, font, layout, and semantic roles as separate decisions.
6. Use `auto_figure_design(...)` from `scientific_figure_skill` inside this repository.
7. Outside the repository, use the standalone scripts bundled with the skill.
8. Generate complete runnable Python/Matplotlib code and export PNG/PDF.
9. Validate exports, generate an original/grayscale review image, and read the actual image.
10. Revise visible defects and report exact artifact paths, assumptions, and QA status.

## Style behavior

Use these built-in chart-style presets when appropriate:

- `publication_minimal` for vague paper-style requests.
- `nature_journal` for Nature/Science/Cell-like journal panels.
- `ieee_transactions` for IEEE/engineering figures.
- `acm_conference` for CS conference layouts.
- `neurips_ml` for NeurIPS/ICML/ICLR-style ML plots.
- `seaborn_whitegrid` or `seaborn_ticks` for seaborn-like statistical plots.
- `cartoon_handdrawn` only for explanatory slides or informal figures.
- `dark_presentation` only for slides/posters unless explicitly requested.

## Maintenance

When editing skill behavior, change the canonical package first:

```text
skills/scientific-figure-making/
```

Then run:

```bash
python scripts/sync_skill_paths.py
python scripts/install_global_skill.py --target claude
```
