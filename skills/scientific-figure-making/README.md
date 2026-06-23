# scientific-figure-making

A global-installable Agent Skill for publication-ready Python/Matplotlib scientific figures with automatic palette selection.

## Install globally for Codex

```bash
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.agents/skills/scientific-figure-making
```

## Install globally for Claude Code

```bash
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.claude/skills/scientific-figure-making
rm -rf ~/.claude/skills/scientific-figure-making/agents
```

## Use

Codex:

```text
$scientific-figure-making
Create a paper-ready grouped bar chart. Style: Nature科研风格，简洁大气，色盲安全. Export PNG and PDF.
```

Claude Code:

```text
/scientific-figure-making
Create a paper-ready grouped bar chart. Style: Nature科研风格，简洁大气，色盲安全. Export PNG and PDF.
```

## Preview palette selection

```bash
python scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

## Standalone helper

The skill contains `scripts/figure_toolkit.py`, so it can work even when the `Illustrator4Resarch` Python package is not importable. Generated plotting scripts can either import from the global skill path or copy this helper into the target project.