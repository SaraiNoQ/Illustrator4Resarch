# Global installation

This skill can be installed globally so it is available to agents outside the Illustrator4Resarch repository.

## Codex user-level install

Codex reads user-level skills from:

```text
$HOME/.agents/skills
```

Install manually:

```bash
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.agents/skills/scientific-figure-making
```

After installation, Codex can use the skill from any repository. A direct invocation can use:

```text
$scientific-figure-making
Create a publication-ready grouped bar chart. Style: 简洁大气，Nature科研风格，色盲安全. Export PNG and PDF.
```

## Claude Code personal install

Claude Code reads personal skills from:

```text
~/.claude/skills/<skill-name>/SKILL.md
```

Install manually:

```bash
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.claude/skills/scientific-figure-making
rm -rf ~/.claude/skills/scientific-figure-making/agents
```

Then invoke the skill from any project:

```text
/scientific-figure-making
请生成一张论文主实验 grouped bar，风格简洁大气、Nature科研风格、色盲安全，导出 PNG 和 PDF。
```

If Claude Code was already running before the skill directory existed, restart the session. If only `SKILL.md` changed while the directory was already watched, Claude Code should detect the change automatically.

## Hermes install

The installer supports Hermes with this default skill root:

```text
~/.hermes/skills
```

Install manually:

```bash
mkdir -p ~/.hermes/skills
rm -rf ~/.hermes/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.hermes/skills/scientific-figure-making
```

If your Hermes deployment scans a different directory, use that directory instead of `~/.hermes/skills`, or set `HERMES_SKILLS_DIR` when using the one-command installer.

Example prompt:

```text
Use the scientific-figure-making skill from ~/.hermes/skills/scientific-figure-making/SKILL.md.
Create a publication-ready grouped bar chart. Style: Datawrapper-like clean editorial style. Export PNG and PDF.
```

## One-command install from this repository

From the repository root:

```bash
python scripts/install_global_skill.py --target all
```

Available targets:

```bash
python scripts/install_global_skill.py --target codex
python scripts/install_global_skill.py --target claude
python scripts/install_global_skill.py --target hermes
python scripts/install_global_skill.py --target both   # Codex + Claude Code
python scripts/install_global_skill.py --target all    # Codex + Claude Code + Hermes
```

Override runtime-specific skill roots when needed:

```bash
CODEX_SKILLS_DIR=/custom/codex/skills python scripts/install_global_skill.py --target codex
CLAUDE_SKILLS_DIR=/custom/claude/skills python scripts/install_global_skill.py --target claude
HERMES_SKILLS_DIR=/custom/hermes/skills python scripts/install_global_skill.py --target hermes
```

The installer removes any existing target directory before copying the current canonical skill package, so repeated installs are safe.

## Package as ZIP

To produce a shareable skill archive:

```bash
python scripts/package_skill.py
```

The archive is written to:

```text
dist/scientific-figure-making.zip
```

## What must remain inside the skill folder

The globally installed folder must contain at least:

```text
scientific-figure-making/
├── SKILL.md
├── references/
│   ├── api-usage.md
│   ├── global-installation.md
│   └── palette-workflow.md
└── scripts/
    ├── figure_toolkit.py
    └── preview_palette.py
```

`agents/openai.yaml` is useful for Codex UI metadata but not required for Claude Code or Hermes.
