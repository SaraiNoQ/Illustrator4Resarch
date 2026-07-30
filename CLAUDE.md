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
results.csv 包含论文主实验结果，请你推荐最合适的图表。
Ours 是本文方法；视觉方向尚未确定，请先逐项询问投稿场景、图形语法、配色、字体和版式。
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
2. Classify inputs, normalize primary tables to CSV, and record a provenance audit.
3. Inspect designated reference images before asking visual questions.
4. Create a Style Brief and ask every unresolved venue, chart/grammar, palette, typography, and layout question first.
5. Report data intake and append up to three data/scientific questions after the style section.
6. Treat explicit “you decide/use all recommendations” language as style delegation; do not treat “not decided” as delegation.
7. Block formal code, Figure Spec, PNG, and PDF until data, style/chart, and scientific meaning are verified.
8. Record the confirmed contract in Figure Spec 1.2.
9. Use `auto_figure_design(...)` from `scientific_figure_skill` inside this repository.
10. Outside the repository, use the standalone scripts bundled with the skill.
11. Generate complete runnable Python/Matplotlib code that reads verified normalized data and exports tightly bounded PNG/PDF with small non-clipping padding.
12. Validate data/spec/exports, including outer-whitespace warnings, generate an original/grayscale review image, and read the actual image.
13. Revise composition, grouping, hierarchy, legibility, and accessibility defects before reporting exact artifact paths, assumptions, and QA status.

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
