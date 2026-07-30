---
name: scientific-figure-making
description: "Create, plan, refine, and visually validate publication-ready scientific figures in Python/Matplotlib. Use this skill whenever the user provides experiment data, a results table/CSV, a manuscript claim, an existing plot or plotting script, a visual reference, or asks for a paper/thesis/research-slide figure—even when chart type, style, palette, typography, dimensions, or scientific semantics are incomplete. It leads with a reference-first Style Brief, asks unresolved style questions before scientific clarifications in the same batch, recommends an honest chart for confirmation, blocks formal rendering until style and scientific meaning are resolved, and delivers reproducible PNG/PDF/code/spec/QA artifacts. Also triggers for grouped bars, ablations, trends, convergence, heatmaps, scatter/Pareto plots, multi-panel figures, table styling, Nature/IEEE/ACM/NeurIPS styles, colorblind or print-safe design, and figure polishing. Do not use for decorative graphics unrelated to research data or scientific communication."
compatibility: "Agent Skills package for Codex, Claude Code, Hermes, and compatible agents. Requires Python 3.9+ with matplotlib and numpy. Visual completion also requires an available image-reading/viewing tool."
metadata:
  version: "0.7.0"
  source_repository: "SaraiNoQ/Illustrator4Resarch"
  package_type: "global-installable-agent-skill"
  primary_language: "python"
argument-hint: "<raw data/files, research goal, incomplete or complete style request, reference image, existing figure/script, venue and output constraints if known>"
allowed-tools: "Read Write Edit Grep Glob Bash"
---

# Scientific figure making

Act as a scientific-figure director, not only a plotting-code generator. Own the
path from incomplete research input to an intentionally styled, checked, and
reproducible figure.

The objective is a figure whose visual language has been chosen by or explicitly
delegated by the user, whose scientific meaning is honest, and whose actual
exported image has been inspected. A successful Python exit code alone is not
completion.

## Core principles

1. **Style intent is the first user-facing contract.** When style is incomplete,
   surface it before scientific clarifications instead of silently applying a
   generic academic default.
2. **Reference first.** Inspect a designated reference image before asking about
   aesthetics. Recover what is visible and ask only about remaining gaps or
   conflicts.
3. **Recommend, then confirm.** Infer an honest chart from the data and message,
   explain the recommendation, and ask the user to confirm it unless they
   explicitly delegated the choice.
4. **Scientific meaning remains non-negotiable.** Never invent uncertainty,
   significance, units, sample sizes, missing measurements, or conclusions.
5. **Separate design layers.** Venue, chart grammar, palette, typography, and
   layout are related but independently confirmable choices.
6. **Inspect the exported result.** Run deterministic checks and visually read
   the original plus grayscale preview.
7. **Revise with purpose.** Fix correctness, legibility, hierarchy,
   accessibility, and polish problems without changing verified data.

Style-first describes conversation order, not careless analysis order. Read
enough of the data internally to recommend a suitable chart, but present style
questions before scientific questions.

## Select the operating mode

Infer the mode without asking the user to name it:

- `guided`: data or a broad goal is present, but style or semantics are
  incomplete.
- `direct`: scientific semantics, visual design, mappings, constraints, and
  outputs are explicit or the user has delegated unresolved choices.
- `refine`: an existing figure or plotting script is the primary input; its
  intentional design becomes a reference unless the user asks to replace it.
- `multi_panel`: multiple linked messages or incompatible scales need panels.

Read `references/style-intake.md` and `references/requirement-workflow.md` for
guided, reference-driven, and refinement tasks.

## Complete workflow

Follow these stages in order. Compress narration for a direct request, but do
not skip confirmation gates, rendering, or QA.

### 1. Inspect inputs and recover context

Read supplied data, scripts, images, captions, manuscript text, and related
files. Identify internally:

- research question, intended message, methods, datasets, metrics, and ordering;
- metric direction, units, aggregation, and uncertainty semantics;
- baseline, proposed method, ablations, and desired comparisons;
- any designated visual reference and which properties it demonstrates;
- venue, medium, target dimensions, outputs, and accessibility constraints;
- existing choices worth preserving in refinement mode.

Do not ask for information recoverable from the inputs. If an image is
designated as a style reference, inspect it with an image-reading tool before
asking style questions.

### 2. Audit style completeness

Resolve these five dimensions independently:

1. venue or use context;
2. chart type and graphic grammar;
3. palette and semantic emphasis;
4. typography direction;
5. layout, column width, aspect, legend, and panel arrangement.

Classify each dimension as:

- `explicit`: stated in the request;
- `reference`: recoverable from a designated reference image;
- `delegated`: the user explicitly said “you decide”, “use your recommendation”,
  “全部按推荐”, or equivalent;
- `missing`: none of the above.

“I have not decided” or “I am unsure” means `missing`, not delegated.

If a reference is attached and explicitly designated, summarize its observable
style and adapt it to the current data. Do not ask again about information the
reference already supplies. If an attached image is not clearly designated as
a reference, ask what role it should play.

### 3. Create the first-turn briefs

When any style dimension is missing, the first user-facing response must follow
this order:

```text
Style Brief
- Reference:
- Venue/use context:
- Recommended chart and graphic grammar:
- Palette and semantic emphasis:
- Typography:
- Layout:
- Confirmed from input:
- Still unresolved:

Style questions
1. ...

Scientific interpretation
- Research question:
- Intended message:
- Data structure:
- Metric direction and uncertainty:
- Assumptions:

Scientific questions
1. ...
```

For every missing style dimension, ask a separate numbered question. Give one
task-specific recommendation plus concise alternatives. The user may answer
with exact preferences, upload a reference, or approve all recommendations.

After the style section, append at most three scientific questions whose answers
affect interpretation. Keep both sections in the same response so the user can
answer once, but never place an `error`, unit, or uncertainty question ahead of
the style section.

If style is already explicit, reference-derived, or delegated, omit redundant
style questions, state the resolved Style Brief, and ask only remaining
scientific questions.

### 4. Enforce both confirmation gates

Do not create a formal plotting script, final Figure Spec, or publication
PNG/PDF while either gate remains open:

- **Style gate:** all five style dimensions and the recommended chart are
  confirmed, reference-derived, or explicitly delegated.
- **Scientific gate:** no unresolved ambiguity can change the data mapping or
  interpretation.

The user answering only a scientific question does not close the style gate.
Re-present only the unresolved style items and remain blocked.

Explicit delegation closes the corresponding style gaps. “Use all your
recommendations” closes the entire style gate. Safe temporary swatches or
low-fidelity style previews are allowed only when clearly labelled as previews,
not final figures.

### 5. Create the confirmed Figure Brief and Figure Spec

After both gates close, state the compact final contract:

```text
Confirmed Figure Brief
- Research question and intended message:
- Data structure and scientific semantics:
- Confirmed chart:
- Confirmed visual system:
- Venue and final size:
- Accessibility:
- Outputs:
- Assumptions:
```

Read `references/chart-selection.md` when the chart recommendation needs deeper
justification. Avoid dual axes, unjustified truncated bar axes, rainbow
heatmaps, and mean-only summaries when raw distributions are available.

For substantive tasks, create `<output-stem>.spec.json` following
`references/figure-spec.md`, then validate it:

```bash
python <skill-root>/scripts/figure_spec.py validate <figure.spec.json>
```

New specs use schema 1.1. A pending style status, an unconfirmed chart, or an
unresolved critical scientific question makes the spec invalid.

### 6. Resolve the confirmed design system

Use the deterministic engines with the confirmed style request rather than
inventing or silently substituting styling.

Inside the Illustrator4Resarch repository:

```python
from scientific_figure_skill import (
    FigureStyle,
    apply_publication_style,
    auto_figure_design,
    select_font_family,
)

design = auto_figure_design(
    request=confirmed_style_request,
    figure_type=confirmed_figure_type,
    n_colors=n_series,
    data_role=data_role,
    venue=confirmed_venue,
)
font_family = select_font_family(
    request=confirmed_style_request,
    chart_style=confirmed_chart_style_name,
    venue=confirmed_venue,
)
style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=confirmed_chart_style_name,
    font_family=font_family,
)
apply_publication_style(style)
```

From a global installation, add `<skill-root>/scripts` to `sys.path`, then use
`figure_design.py`, `figure_fonts.py`, and `figure_toolkit.py`.

Design safeguards:

- categorical comparisons: colorblind-safe separation plus markers, hatches,
  or linestyles when needed;
- magnitude heatmaps: perceptually ordered sequential color;
- signed differences: zero-centered diverging color;
- phase/angle: cyclic color;
- black-and-white print: grayscale plus non-color encoding;
- paper tables: sparse three-line/booktabs-like rules;
- unavailable requested fonts: choose and disclose the closest safe fallback;
- dark or novelty styles: use for paper only when confirmed by the user.

### 7. Generate reproducible code and render

Create a complete Python script rather than a notebook-only fragment. Keep data
loading and transformations explicit. Preserve source precision and document
sorting, filtering, aggregation, or normalization.

Defaults after style confirmation unless overridden:

- script under `scripts/`;
- outputs under `figures/`;
- PNG and PDF;
- 300 DPI or the venue requirement;
- exact output paths;
- deterministic ordering and styling.

Run the script from a clean process. Fix runtime warnings that affect the result,
especially missing fonts, clipped layout, invalid values, and unsupported
glyphs.

### 8. Run deterministic and visual QA

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

Use the runtime image-reading tool to inspect the review image. Check data
mapping, collisions, clipping, final-size legibility, visual hierarchy,
uncertainty, grayscale differentiation, reference fidelity, and multi-panel
consistency.

Programmatic QA cannot replace visual inspection. If no image-reading tool is
available, say visual QA remains incomplete and ask the user to review the
preview; do not claim the figure passed visual review.

### 9. Revise and rerender

Turn observations into a concrete issue list:

- correctness;
- style fidelity;
- legibility;
- hierarchy;
- accessibility;
- polish.

Fix correctness and structure first, then style fidelity and legibility, then
accessibility and polish. Normally use up to three render-review passes. Do not
alter verified data while fixing appearance.

### 10. Deliver the complete handoff

Report:

1. Confirmed style source and chart rationale.
2. Exact paths to script, PNG, PDF, Figure Spec, QA report, and review preview.
3. Data transformations and assumptions.
4. Deterministic QA result.
5. Visual-review passes and issues fixed.
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

Inspect the current image before editing. Treat its effective intentional style
as reference-derived, identify which aspects the user wants changed, preserve
verified data, and make the smallest useful change set. Re-render and compare.
Do not reverse-engineer exact numeric data from pixels when source fidelity
matters.

## Tables and non-standard figures

Use the same Style Brief → scientific clarification → confirmed Figure Brief →
Spec → Render → Inspect → Revise loop for tables and multi-panel figures. Raw
Matplotlib is appropriate when bundled helpers do not fit.

## Reference routing

- `references/style-intake.md`: reference-first style audit and question format.
- `references/requirement-workflow.md`: question ordering, gates, defaults, modes.
- `references/chart-selection.md`: recommend chart form from the scientific task.
- `references/figure-spec.md`: schema 1.1 contract and validation.
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
`python scripts/package_skill.py`. Keep repo-scoped discovery copies
synchronized with the canonical package.
