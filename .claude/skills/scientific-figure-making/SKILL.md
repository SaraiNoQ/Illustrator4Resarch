---
name: scientific-figure-making
description: "Create, plan, refine, and visually validate publication-ready scientific figures in Python/Matplotlib. Use this skill whenever the user provides experiment data, a results table/CSV, a manuscript claim, an existing plot or plotting script, or asks for a paper/thesis/research-slide figure—even when they do not know the chart type, style, palette, dimensions, or complete requirements. It guides incomplete requests through a Figure Brief, asks only scientifically consequential questions, chooses an honest chart, renders and inspects the real image, revises defects, and delivers reproducible PNG/PDF/code/spec/QA artifacts. Also triggers for grouped bars, ablations, trends, convergence, heatmaps, scatter/Pareto plots, multi-panel figures, table styling, Nature/IEEE/ACM/NeurIPS styles, colorblind or print-safe design, and figure polishing. Do not use for decorative graphics unrelated to research data or scientific communication."
compatibility: "Agent Skills package for Codex, Claude Code, Hermes, and compatible agents. Requires Python 3.9+ with matplotlib and numpy. Visual completion also requires an available image-reading/viewing tool."
metadata:
  version: "0.6.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  package_type: "global-installable-agent-skill"
  primary_language: "python"
argument-hint: "<raw data/files, research goal, incomplete or complete figure request, existing figure/script, venue and output constraints if known>"
allowed-tools: "Read Write Edit Grep Glob Bash"
---

# Scientific figure making

Act as a scientific-figure director, not only a plotting-code generator. Own the
path from incomplete research input to a checked, reproducible figure. Reduce
the user's specification burden while protecting scientific meaning.

The objective is an accurate, readable, publication-ready visualization whose
actual exported image has been inspected. A successful Python exit code alone
is not completion.

## Core principles

1. **Scientific meaning comes first.** Never invent uncertainty, significance,
   units, sample sizes, missing measurements, or conclusions.
2. **Ask about meaning, default presentation.** Stop for ambiguity that changes
   interpretation; choose and record safe defaults for ordinary aesthetic
   choices.
3. **Choose the chart from the message.** Infer what the reader should compare
   before selecting bars, lines, heatmaps, scatter plots, or panels.
4. **Separate design layers.** Palette, chart style, table style, font, layout,
   and semantic emphasis are related but independent decisions.
5. **Inspect the exported result.** Run deterministic checks and visually read
   the original plus grayscale preview.
6. **Revise with purpose.** Fix observed correctness, legibility, hierarchy, and
   accessibility problems; avoid arbitrary style churn.

## Select the operating mode

Infer the mode without asking the user to name it:

- `guided`: raw data or a broad goal is present but the design is incomplete.
- `direct`: scientific semantics, mappings, constraints, and outputs are clear.
- `refine`: an existing figure or plotting script is the primary input.
- `multi_panel`: multiple linked messages or incompatible scales need panels.

Read `references/requirement-workflow.md` for incomplete requests and refinement
tasks.

## Complete workflow

Follow these stages in order. Compress the narration for a simple direct request,
but do not skip rendering or QA.

### 1. Inspect inputs and recover context

Read the supplied data, script, image, caption, manuscript paragraph, or related
files. Identify:

- research question and intended message;
- observations, methods, datasets, metrics, units, and ordering;
- whether higher or lower is better;
- aggregation and uncertainty semantics;
- desired comparisons, baselines, proposed method, and ablations;
- target venue, paper column width, slide/poster context, and formats;
- existing choices worth preserving in refinement mode.

Do not ask for information already recoverable from the inputs.

### 2. Create a Figure Brief

Before coding, state:

```text
Figure Brief
- Research question:
- Intended message:
- Data structure:
- Metric direction and uncertainty:
- Recommended chart:
- Why this chart:
- Visual emphasis:
- Venue/size:
- Accessibility:
- Outputs:
- Assumptions:
- Questions:
```

In direct mode this may be only a few lines. In guided mode it is the design
contract that relieves the user from writing a perfect prompt.

### 3. Resolve only critical ambiguity

Classify missing information:

- **Critical:** changes scientific meaning. Ask before valid rendering.
- **Defaultable:** affects presentation. Choose a publication-safe default and
  record it.
- **Optional:** decorative preference. Do not block.

Batch at most three high-impact questions. Explain briefly why each matters and
recommend an answer when safe. If only defaultable information is absent,
continue without waiting.

Examples of blockers include unknown metric direction, ambiguous units, unknown
meaning of `±`, uncertain row/column mapping, or a requested transformation that
could distort the conclusion.

### 4. Choose the chart and materialize a Figure Spec

Read `references/chart-selection.md` when the chart is not already justified.
Prefer the form that makes the intended comparison accurate and easy to see.
Avoid dual axes, unjustified truncated bar axes, rainbow heatmaps, and
mean-only summaries when raw distributions are available.

For substantive tasks, create `<output-stem>.spec.json` following
`references/figure-spec.md`. Validate it before rendering:

```bash
python <skill-root>/scripts/figure_spec.py validate <figure.spec.json>
```

Unresolved critical questions make the spec invalid. Warnings may proceed only
when their defaults are documented in `assumptions`.

### 5. Resolve the design system

Use the existing deterministic engines instead of inventing random styling.

Inside the Illustrator4Resarch repository:

```python
from scientific_figure_skill import (
    FigureStyle,
    apply_publication_style,
    auto_figure_design,
    select_font_family,
)

design = auto_figure_design(
    request=request,
    figure_type=figure_type,
    n_colors=n_series,
    data_role=data_role,
    venue=venue,
)
font_family = select_font_family(
    request=request,
    chart_style=design.chart_style,
    venue=venue,
)
style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
    font_family=font_family,
)
apply_publication_style(style)
```

From a global installation, add `<skill-root>/scripts` to `sys.path`, then use
`figure_design.py`, `figure_fonts.py`, and `figure_toolkit.py`.

Design rules:

- categorical comparisons: colorblind-safe separation plus marker, hatch, or
  linestyle when needed;
- magnitude heatmaps: perceptually ordered sequential color;
- signed differences: zero-centered diverging color;
- phase/angle: cyclic color;
- black-and-white print: grayscale plus non-color encoding;
- paper tables: sparse three-line/booktabs-like rules;
- informal/hand-drawn styles: readable publication-safe sans-serif fonts, not
  Times New Roman by accident;
- dark or novelty styles: slides/posters only unless explicitly requested.

Read the existing palette, style, table, and font references only when those
decisions need deeper guidance.

### 6. Generate reproducible code and render

Create a complete Python script rather than a notebook-only fragment. Keep data
loading and transformations explicit. Preserve source precision and document
sorting, filtering, aggregation, or normalization.

Defaults unless the user requests otherwise:

- script under `scripts/`;
- outputs under `figures/`;
- PNG and PDF;
- 300 DPI or the venue requirement;
- exact output paths;
- deterministic ordering and styling.

Run the script from a clean process. Fix runtime warnings that affect the result,
especially missing fonts, clipped layout, invalid values, and unsupported glyphs.

### 7. Run deterministic and visual QA

Read `references/visual-qa.md`. Run:

```bash
python <skill-root>/scripts/validate_figure.py \
  --spec <figure.spec.json> \
  --report <figure.qa.json>

python <skill-root>/scripts/render_preview.py \
  <figure.png> \
  --output <figure.review.png> \
  --grayscale
```

Then use the runtime's image-reading or viewing tool to inspect the review image.
Check correctness, collisions, clipping, final-size legibility, hierarchy,
uncertainty, grayscale differentiation, density, and multi-panel consistency.

Programmatic QA cannot replace visual inspection. If no image-reading tool is
available, say visual QA remains incomplete and ask the user to review the
preview; do not claim the figure passed visual review.

### 8. Revise and rerender

Turn observations into a concrete issue list:

- correctness;
- legibility;
- hierarchy;
- accessibility;
- polish.

Fix correctness and structure first, then legibility and accessibility, then
polish. Normally use up to three render-review passes. Continue when a clear
safe fix remains; stop and ask when the remaining choice depends on scientific
intent.

Do not alter verified data while fixing appearance.

### 9. Deliver the complete handoff

Report:

1. Chart choice and design rationale.
2. Exact paths to script, PNG, PDF, Figure Spec, QA report, and review preview.
3. Data transformations and assumptions.
4. Deterministic QA result.
5. Number of visual-review passes and issues fixed.
6. Remaining limitations or questions.
7. Reproduction command.

For a substantive `main_comparison` task, prefer:

```text
scripts/plot_main_comparison.py
figures/main_comparison.png
figures/main_comparison.pdf
figures/main_comparison.spec.json
figures/main_comparison.qa.json
figures/main_comparison.review.png
```

## Refining an existing figure

Inspect the current image before editing. Recover data and mappings from the
script or source files, distinguish correctness problems from aesthetic
problems, preserve effective intentional choices, and make the smallest useful
change set. Re-render and compare. Do not reverse-engineer exact numeric data
from pixels when source fidelity matters.

## Tables and non-standard figures

Use the same Brief → Spec → Render → Inspect → Revise loop for tables and
multi-panel figures. Raw Matplotlib is appropriate when bundled helpers do not
fit. For conceptual schematics without quantitative mappings, still make the
message, assumptions, and visual inspection explicit.

## Reference routing

- `references/requirement-workflow.md`: guided questions, defaults, and modes.
- `references/chart-selection.md`: choose chart form from the scientific task.
- `references/figure-spec.md`: JSON contract and validation.
- `references/visual-qa.md`: deterministic and visual review loop.
- `references/palette-workflow.md`: palette inference and generated variants.
- `references/style-workflow.md`: venue and chart-style presets.
- `references/table-workflow.md`: table grammar.
- `references/font-workflow.md`: publication-safe font selection.
- `references/api-usage.md`: Python API examples.
- `references/global-installation.md`: installation paths.

## Repository modification

When modifying Illustrator4Resarch itself, edit the canonical skill first, run
`python scripts/sync_skill_paths.py`, run `python -m pytest -q`, and package with
`python scripts/package_skill.py`. Keep repo-scoped discovery copies synchronized
with the canonical package.
