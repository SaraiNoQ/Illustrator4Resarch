# Guided scientific-figure workflow v0.6

## Objective

Upgrade `scientific-figure-making` from a style-selection toolbox into a guided,
end-to-end scientific-figure workflow. A researcher should be able to provide
raw experiment data and an incomplete request without first writing a perfect
prompt. The skill should determine what is safe to infer, ask only questions
that affect scientific meaning, propose a figure plan, render the figure,
inspect the result, revise it, and deliver reproducible artifacts.

The existing palette, chart-style, table-style, and font engines remain the
design backend. Version 0.6 adds an orchestration and quality-assurance layer
around them.

## Success criteria

A completed v0.6 task should:

1. Accept incomplete requests such as "use `results.csv` to make the main paper
   figure".
2. Extract or infer the research goal, comparison structure, metric direction,
   uncertainty semantics, intended emphasis, venue constraints, and outputs.
3. Distinguish blockers from preferences. Ask at most three high-impact
   questions in one batch, while defaulting ordinary aesthetic choices.
4. Produce a concise Figure Brief before implementation.
5. Materialize a machine-checkable Figure Spec for substantive tasks.
6. Select the chart form from the scientific message, not only from chart-name
   keywords.
7. Render the script and inspect the actual image, rather than treating a
   successful Python exit code as completion.
8. Run deterministic export checks and a visual-review checklist.
9. Revise recoverable defects automatically and preserve unresolved scientific
   assumptions in the handoff.
10. Export runnable source, PNG, PDF by default, Figure Spec, and a QA report.

## Non-goals

- Replacing Matplotlib with a new rendering engine.
- Building a GUI or a long questionnaire.
- Automatically inventing missing measurements, error bars, significance
  values, labels, or scientific conclusions.
- Encoding subjective figure quality entirely as brittle numeric thresholds.
- Adding more style presets before the guided workflow is validated.

## Architecture

```text
raw request + files
        |
        v
mode and intent triage
        |
        v
Figure Brief ---- critical ambiguity? ----> batched questions
        |                                      |
        +------------------<-------------------+
        |
        v
Figure Spec (JSON)
        |
        v
chart/palette/style/table/font engines
        |
        v
reproducible plotting script
        |
        v
PNG/PDF render
        |
        +--> deterministic QA
        |
        +--> original + grayscale preview
        |
        +--> model visual inspection
        |
        v
issue list -> targeted revision -> rerender (normally up to 3 passes)
        |
        v
artifacts + assumptions + QA handoff
```

## Workstreams

### 1. Agent orchestration

Rewrite the canonical `SKILL.md` as the portable source of truth.

- Add guided, direct, refinement, and multi-panel modes.
- Add a critical/defaultable/optional information policy.
- Define the Figure Brief format.
- Define the question budget and recommended-answer behavior.
- Make planning, rendering, image inspection, and revision required stages.
- Define stopping rules and the final handoff format.
- Route detailed rules to references so `SKILL.md` stays concise.

Acceptance:

- An agent can follow the complete workflow from the canonical file alone.
- An incomplete but scientifically safe request does not stall on aesthetic
  questions.
- An ambiguous metric or uncertainty definition does not silently proceed.

### 2. Figure Brief and Figure Spec

Add `references/requirement-workflow.md` and `references/figure-spec.md`.
Implement `scripts/figure_spec.py` using the Python standard library.

- Provide a reusable JSON template.
- Validate required top-level sections and enum-like values.
- Treat unresolved critical questions as errors.
- Treat missing recommended publication metadata as warnings.
- Support human-readable and JSON CLI output.

Acceptance:

- `figure_spec.py init` writes a usable template.
- `figure_spec.py validate` returns non-zero for blockers and zero for a valid
  spec.
- No new runtime dependency is required.

### 3. Message-driven chart selection

Add `references/chart-selection.md`.

- Map comparison, trend, distribution, relationship, composition, trade-off,
  ranking, matrix, and ablation goals to appropriate chart families.
- Document misleading alternatives and escalation cases.
- Cover multi-panel decomposition and scale/unit conflicts.
- Keep explicit user choices unless they would materially distort the data.

Acceptance:

- The skill explains the chosen chart in the Figure Brief.
- It does not place incompatible units on one axis by default.
- It does not use bars merely because method names are categorical.

### 4. Render QA

Add `references/visual-qa.md`.
Implement `scripts/validate_figure.py` and `scripts/render_preview.py`.

Deterministic checks:

- Expected files exist and are non-empty.
- PNG header, dimensions, and encoded DPI are readable.
- Raster output is not blank or nearly uniform.
- Tonal contrast is sufficient for inspection.
- Content does not obviously touch every crop boundary.
- PDF starts with a valid PDF signature.
- Requested formats in the Figure Spec are present.

Visual checks:

- Label, tick, annotation, and legend collisions.
- Font readability at target column width.
- Correct visual hierarchy and semantic emphasis.
- Appropriate uncertainty rendering.
- Grayscale and color-independent differentiation.
- Multi-panel alignment, whitespace, and density.
- Whether the intended scientific claim is visible without exaggeration.

Acceptance:

- Deterministic QA writes a JSON report and returns non-zero on errors.
- Preview generation creates original and grayscale views.
- The skill explicitly opens/reads the preview with an available image tool.
- Lack of an image-reading tool is reported as incomplete visual QA.

### 5. Documentation and discovery copies

- Update the repository README and AGENTS workflow.
- Replace the fill-in-the-blanks prompt with an incomplete-request-friendly
  prompt.
- Add guided, direct, and refinement examples.
- Update Codex metadata, version numbers, and design-layer metadata.
- Synchronize the canonical package to `.agents/skills/` and
  `.claude/skills/`.

Acceptance:

- All runtime copies contain the same v0.6 workflow.
- Installation and ZIP packaging include the new references, scripts, examples,
  and evals.

### 6. Automated tests

Add unit tests for:

- Valid and invalid Figure Specs.
- Critical unresolved questions.
- Defaultable omissions producing warnings.
- PNG dimension/DPI inspection.
- Blank-image rejection.
- Valid PDF signature checks.
- QA report serialization and CLI exit behavior.
- Preview generation.

Run the existing palette/style/font/install tests to prevent regressions.

Acceptance:

- `python -m pytest -q` passes.
- New utilities work from the standalone skill directory without importing the
  repository package.

### 7. Skill evaluations

Add `evals/evals.json` with realistic incomplete requests:

1. Raw main-results data with no chart type or style.
2. Mean and standard-deviation data with ambiguous uncertainty semantics.
3. An existing crowded plotting script that needs refinement.
4. A latency-versus-accuracy trade-off requiring a scatter/Pareto design.
5. A multi-metric request with incompatible units.

Evaluation combines:

- Objective assertions: no invented data, required artifacts, runnable script,
  explicit assumptions, successful deterministic QA.
- Human review: chart choice, hierarchy, legibility, publication fit, and user
  burden.
- Old-skill versus v0.6 comparison for at least one representative case.

### 8. Packaging and rollout

- Run `scripts/sync_skill_paths.py`.
- Run `scripts/package_skill.py`.
- Inspect ZIP contents.
- Test an isolated global installation target.
- Sync the development branch back to `/root/Illustrator4Resarch`.
- Re-run tests on the server.

Acceptance:

- `dist/scientific-figure-making.zip` contains the complete v0.6 skill.
- Server worktree is clean except for intentional v0.6 changes.
- Branch remains `codex/guided-figure-workflow-v1` until review.

## Artifact contract

For a substantive figure named `main_comparison`, the default deliverables are:

```text
scripts/plot_main_comparison.py
figures/main_comparison.png
figures/main_comparison.pdf
figures/main_comparison.spec.json
figures/main_comparison.qa.json
figures/main_comparison.review.png
```

The final response reports:

- design decision and chart rationale;
- exact artifact paths;
- assumptions and unresolved limitations;
- deterministic QA result;
- visual QA iterations and remaining concerns.

## Scientific safety rules

- Never invent uncertainty, significance, sample size, units, or missing values.
- Never silently change the meaning, aggregation, order, or sign of data.
- Never truncate axes in a way that exaggerates differences without disclosing
  and justifying the choice.
- Do not infer causal claims from correlational data.
- Prefer direct labels or accessible secondary encodings when color alone is
  insufficient.
- Stop and ask when an answer changes the scientific interpretation; proceed
  with documented defaults when it only changes presentation.

## Release gate

Version 0.6 is ready for review when:

- canonical and discovery skill copies are synchronized;
- all tests pass locally and on the server;
- the package archive is generated;
- at least one incomplete-request A/B evaluation is available for human review;
- known limitations are documented.
