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
请根据下面的数据生成论文主实验 grouped bar。
图表风格：Nature-like journal style，紧凑、简洁、无重网格。
配色要求：色盲安全，主方法突出。
导出 PNG 和 PDF。
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

1. Parse the user's figure type, data shape, target venue/chart style, palette preference, semantic roles, and output paths.
2. Treat palette and chart style as separate decisions.
3. Use `auto_figure_design(...)` from `scientific_figure_skill` when working inside this repository.
4. If the skill is globally installed outside this repository, use `scripts/figure_design.py` for design decisions and `scripts/figure_toolkit.py` for plotting helpers.
5. Generate complete runnable Python/Matplotlib code.
6. Export at least PNG and PDF.
7. Run the plotting script and report exact output paths.

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
