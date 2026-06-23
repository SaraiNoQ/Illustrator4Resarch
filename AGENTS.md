# Agent Instructions

This repository is an Agent Skills project for generating publication-ready scientific figures. It supports:

- Codex repo-scoped discovery through `.agents/skills/scientific-figure-making/`.
- Claude Code project discovery through `.claude/skills/scientific-figure-making/`.
- Global install through the standalone package at `skills/scientific-figure-making/`.

## Primary objective

Use this project when the user asks a coding agent to create, polish, or refactor Python/Matplotlib figures for papers, theses, reports, or research slides. The skill name is `scientific-figure-making`.

## Canonical files

- `skills/scientific-figure-making/SKILL.md`: canonical standalone skill package. Edit this first.
- `skills/scientific-figure-making/scripts/figure_toolkit.py`: standalone helper for global installs.
- `skills/scientific-figure-making/scripts/preview_palette.py`: palette preview CLI.
- `skills/scientific-figure-making/references/global-installation.md`: install instructions.
- `skills/scientific-figure-making/references/api-usage.md`: API examples.
- `skills/scientific-figure-making/references/palette-workflow.md`: palette decision rules.
- `.agents/skills/scientific-figure-making/SKILL.md`: Codex repo-scoped wrapper.
- `.claude/skills/scientific-figure-making/SKILL.md`: Claude Code project wrapper.
- `scripts/install_global_skill.py`: installs the skill into user-level global directories.
- `scripts/package_skill.py`: creates `dist/scientific-figure-making.zip`.
- `scripts/sync_skill_paths.py`: syncs the canonical skill into repo-scoped discovery paths.

## Global installation commands

Install for both Codex and Claude Code:

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

Package as a shareable ZIP:

```bash
python scripts/package_skill.py
```

## Codex usage

Codex user-level global path:

```text
~/.agents/skills/scientific-figure-making/SKILL.md
```

Direct invocation example:

```text
$scientific-figure-making
Create a publication-ready grouped bar chart. Style: 简洁大气，Nature科研风格，色盲安全. Export PNG and PDF.
```

When working inside this repository, Codex can also read the repo wrapper at `.agents/skills/scientific-figure-making/SKILL.md`.

## Claude Code usage

Claude Code personal global path:

```text
~/.claude/skills/scientific-figure-making/SKILL.md
```

Direct invocation example:

```text
/scientific-figure-making
请生成一张论文级 grouped bar，风格简洁大气、Nature科研风格、色盲安全，导出 PNG 和 PDF。
```

When working inside this repository, Claude Code can also read the project wrapper at `.claude/skills/scientific-figure-making/SKILL.md`.

## Figure-generation workflow

1. Parse figure type, data shape, target style, semantic roles, and output paths.
2. Use `auto_palette(...)` from `scientific_figure_skill` when working inside the repo, or from `skills/scientific-figure-making/scripts/figure_toolkit.py` for standalone/global usage.
3. Build a Matplotlib script with publication styling.
4. Export PNG and PDF unless the user asks otherwise.
5. Run the generated plotting script.
6. If Python package logic changes, run `python -m pytest -q`.

## Quality rules

- Do not use random colors.
- Do not use seaborn unless explicitly requested.
- Prefer semantic color roles: proposed, baseline, secondary, ablation, neutral, highlight.
- For heatmaps, choose sequential or diverging palettes according to the data semantics.
- For black-and-white print, use grayscale plus hatching or marker styles.
- Always provide exact output paths.