# Illustrator4Resarch

Publication-ready scientific figure helpers packaged as a portable Agent Skills project.

## What this repository is

`Illustrator4Resarch` lets coding agents such as Claude Code, Codex-style repository agents, and other skill-aware tools generate scientific Matplotlib figures with automatic palette selection.

The intended workflow is:

1. The user describes a rough visual style, such as `简洁大气`, `Nature 科研风格`, `IEEE 风格`, `色盲安全`, or `黑白打印`.
2. The toolkit retrieves candidate palettes from a curated local registry inspired by ColorBrewer-like qualitative/sequential/diverging schemes, Okabe-Ito/Tol-style colorblind-safe palettes, Matplotlib scientific colormap samples, and restrained Nature/IEEE-like publication palettes.
3. The toolkit builds an LLM selection prompt from those candidates.
4. The LLM chooses the final palette and semantic role mapping, or the deterministic fallback `auto_palette(...)` chooses the best candidate.
5. Matplotlib helpers render the final experimental figure.

## Skills-ready structure

```text
Illustrator4Resarch/
├── AGENTS.md
├── CLAUDE.md
├── .claude/
│   └── skills/
│       └── scientific-figure-making/
│           ├── SKILL.md
│           └── references/
│               ├── api-usage.md
│               └── palette-workflow.md
├── skills/
│   └── scientific-figure-making/
│       ├── SKILL.md
│       ├── references/
│       │   ├── api-usage.md
│       │   └── palette-workflow.md
│       ├── scripts/
│       │   └── preview_palette.py
│       └── examples/
│           └── minimal_request.md
├── scientific_figure_skill/
│   ├── __init__.py
│   └── core.py
├── prompt/
│   └── scientific_figure_prompt.md
├── examples/
│   └── auto_palette_demo.py
└── tests/
    └── test_palette_selector.py
```

Why both `.claude/skills/` and `skills/`?

- `.claude/skills/scientific-figure-making/` is the project-local Claude Code entrypoint. In Claude Code, invoke it as `/scientific-figure-making`.
- `skills/scientific-figure-making/` is the portable skill package for other agents or for copying into another workspace.
- `AGENTS.md` gives Codex-style and generic coding agents repository-level instructions.
- `CLAUDE.md` points Claude Code to `AGENTS.md` and the project-local skill path.

## Minimal Python usage

```python
from scientific_figure_skill import auto_palette, FigureStyle, apply_publication_style

selection = auto_palette(
    "简洁大气，Nature 科研风格，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=4,
)

style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

## Claude Code usage

Inside this repository:

```text
/scientific-figure-making 请画一张 Nature 科研风格的主实验 grouped bar，自动选择配色，导出 PNG 和 PDF。
```

To install the portable skill into your personal Claude Code skills directory, copy:

```bash
mkdir -p ~/.claude/skills/scientific-figure-making
cp -R skills/scientific-figure-making/* ~/.claude/skills/scientific-figure-making/
```

## Codex / generic coding-agent usage

Open the repository with the coding agent. The agent should read `AGENTS.md`, then use `skills/scientific-figure-making/SKILL.md` and the Python package when asked to generate scientific figures.

A direct prompt can be:

```text
Use the scientific-figure-making skill in this repository. Generate a paper-ready grouped bar chart from the following data. Style: 简洁大气, Nature 科研风格, 色盲安全. Export PNG and PDF.
```

## Palette preview

```bash
python skills/scientific-figure-making/scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

## Tests

```bash
python -m pytest -q
```

## Notes

The repository intentionally avoids runtime dependence on external palette websites or APIs. The palette registry is local and deterministic so coding agents can work in offline sandboxes.
