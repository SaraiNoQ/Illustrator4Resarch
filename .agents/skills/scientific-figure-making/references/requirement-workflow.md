# Requirement workflow

Use this workflow when a user has not supplied a complete plotting
specification. The purpose is to reduce user effort without silently choosing
the visual direction or guessing scientific meaning.

Read `data-intake.md` for nontrivial input files and `style-intake.md` before
applying this policy to a guided request.

## Information classes

### Style-required

These visual decisions form the user-facing design contract. They block formal
rendering unless they are explicit, reference-derived, or delegated:

- venue or use context;
- chart type and graphic grammar;
- palette and semantic emphasis;
- typography direction;
- layout, column width, aspect, legend, and panels.

Recommend an answer for every missing dimension. “I have not decided” is a
request for guided choices, not permission to use a hidden default. “You decide”
or “use all recommendations” is explicit delegation and closes the relevant
style gaps.

### Data-fidelity critical

These items decide whether plotted cells faithfully match their sources:

- source roles and which source is authoritative;
- deterministic parse versus visual/manual/runtime transcription;
- irregular rows, blank or duplicate headers, complex TeX, and unreadable cells;
- source conflicts and changes detected by hashes;
- normalized CSV paths and recorded transformations.

Clean deterministic text parsing may close this gate automatically. Screenshot,
manual, complex-TeX, or ambiguous runtime extraction requires review of the
normalized table and explicit user confirmation. Confirming visual style does
not confirm transcribed data.

### Scientifically critical

Missing or ambiguous critical information can change the scientific meaning of
the figure. Ask before rendering unless the answer is recoverable from supplied
files.

- What each metric measures and whether higher or lower is better.
- Units, normalization, aggregation, and denominator.
- Whether values are individual observations, means, medians, or something else.
- What uncertainty columns represent: standard deviation, standard error,
  confidence interval, range, or raw replicates.
- Which rows or columns correspond to methods, datasets, metrics, or conditions.
- Whether values from different scales may be compared directly.
- Whether a requested transformation or axis limit would alter interpretation.

Never invent these values or silently select an interpretation.

### Output-defaultable

These operational choices may use documented defaults after the style gate is
closed:

- PNG and PDF when no format is requested;
- 300 DPI or the confirmed venue requirement;
- deterministic output paths;
- content-aware tight export bounds with small non-clipping padding;
- safe installed-font fallback when the confirmed typeface is unavailable;
- accessibility redundancy that preserves the confirmed visual direction.

### Optional

Do not block on decoration outside the requested design contract:

- exact cap width or marker size after the graphic grammar is confirmed;
- sub-point internal spacing adjustments after outer bounds are compact;
- tiny annotation offsets discovered during visual QA.

## Mode selection

- `guided`: data or a broad goal is present, but visual design or semantics are
  incomplete.
- `direct`: chart, visual design, scientific semantics, and constraints are
  clear or explicitly delegated.
- `refine`: an existing image or plotting script is the primary input.
- `multi_panel`: multiple related messages cannot be shown honestly in one axes.

The user does not need to name the mode.

## First-turn response

For an incomplete guided request, use this exact section order:

```text
Style Brief
Style questions
Scientific interpretation
Scientific questions
```

The style section may contain up to five numbered questions, one for each
unresolved style dimension. In `Scientific interpretation`, report source
roles, extraction method, normalized table shape/preview, data-verification
status, and parsing warnings before the scientific meaning. Follow it with at
most three data/scientific questions. Keep them in one response so the user can
answer in one batch.

Every question must:

1. explain why the answer matters;
2. provide a task-specific recommendation;
3. offer concise alternatives or accept a free-form/reference response;
4. avoid repeating information recoverable from context.

Do not ask the user to invent a chart from scratch. Recommend the scientifically
appropriate chart and ask for confirmation. Do not place transcription,
source-authority, uncertainty, or unit questions before unresolved style
questions.

## Confirmation state

Use three independent gates:

- `data_status=pending` until normalized data and its provenance are verified;
- `style_status=pending` until all five style dimensions and the chart are
  confirmed, reference-derived, or delegated;
- scientific status remains blocked while any critical ambiguity is unresolved.

If the user answers only one section, preserve the other unresolved questions.
Formal code generation and final rendering begin only when all three gates are
closed.

## Proceeding without a reply

Do not silently convert unanswered style questions into defaults. A Style Brief,
swatch sheet, or clearly labelled low-fidelity preview may be useful, but it is
not a final figure. Do not render unconfirmed transcription, scientifically
ambiguous error bars, or unexplained transformations.

Explicit delegation is a reply: “按推荐”, “你来决定”, or equivalent authorizes
the stated recommendations and should not trigger another style questionnaire.

## Refinement mode

When an existing script or image is provided:

1. Inspect the current rendered image before changing code.
2. Treat effective intentional styling as reference-derived.
3. Ask which visual properties should change only when the request is ambiguous.
4. Recover data and mappings from the script or companion files.
5. Separate correctness problems from style-fidelity and legibility problems.
6. Preserve effective choices and change the smallest useful parameter set.
7. Re-render and compare against the original.

If only a chart image is available, do not reconstruct exact source values from
pixel positions. Ask for the data or script when numeric fidelity matters. A
table screenshot may be transcribed, but its normalized table remains pending
until the user confirms it.
