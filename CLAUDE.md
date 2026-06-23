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
风格：简洁大气，Nature科研风格，色盲安全。
要求：自动选择 palette，导出 PNG 和 PDF。
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

1. Parse the user's figure type, data shape, target style, semantic roles, and output paths.
2. Use automatic palette selection from `scientific_figure_skill` when working inside this repository.
3. If the skill is globally installed outside this repository, use `scripts/figure_toolkit.py` bundled inside the skill folder.
4. Generate complete runnable Python/Matplotlib code.
5. Export at least PNG and PDF.
6. Run the plotting script and report exact output paths.

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
