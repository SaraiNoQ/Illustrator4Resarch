# Agent Instructions

This repository is a portable Agent Skills project for generating publication-ready scientific figures.

## Purpose

Use this project when an agent is asked to create, polish, or refactor Python/Matplotlib figures for papers, theses, reports, or research slides. The central skill is `scientific-figure-making`.

## Canonical structure

- `.claude/skills/scientific-figure-making/SKILL.md`: project-local Claude Code skill entrypoint.
- `skills/scientific-figure-making/SKILL.md`: portable/open skill package entrypoint for agents that consume a generic `skills/` directory.
- `scientific_figure_skill/core.py`: importable Python implementation.
- `prompt/scientific_figure_prompt.md`: reusable user-facing prompt template.
- `examples/`: runnable examples.
- `tests/`: regression tests.

## Default workflow for Codex, Claude Code, and other coding agents

When the user asks for a scientific figure:

1. Inspect the requested figure type, data shape, target venue/style, and output format.
2. Use `scientific_figure_skill.auto_palette(...)` to convert the user's natural-language style request into a palette selection.
3. Prefer scientific readability over decorative palettes. For method comparisons, use categorical palettes; for scalar heatmaps, use sequential palettes; for signed differences, use diverging palettes.
4. Use `FigureStyle`, `apply_publication_style`, and the plotting helpers in `scientific_figure_skill.core`.
5. Generate complete runnable Python code, not pseudocode.
6. Save outputs to `figures/` unless the user specifies another location.
7. Export at least PNG and PDF for paper figures.
8. Run `python -m pytest -q` after changing library code or tests.

## Coding conventions

- Keep the public API dependency-light: Python + Matplotlib + NumPy.
- Do not introduce seaborn, Plotly, Bokeh, or web dependencies unless the user explicitly asks.
- Keep color logic deterministic when no external LLM decision is supplied.
- Preserve backwards compatibility for `from scientific_figure_skill import *`.
- Use semantic color roles: `proposed`, `baseline`, `secondary`, `ablation`, `neutral`, `highlight`, `uncertainty`.

## Quality gate

Before committing non-documentation changes, run:

```bash
python -m pytest -q
```

For a smoke test of figure generation, run:

```bash
python examples/auto_palette_demo.py
```
