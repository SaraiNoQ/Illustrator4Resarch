# Requirement workflow

Use this workflow when a user has not supplied a complete plotting
specification. The purpose is to reduce user effort without guessing scientific
meaning.

## Information classes

### Critical

Missing or ambiguous critical information can change the scientific meaning of
the figure. Ask before rendering unless the answer is directly recoverable from
the supplied files.

- What each metric measures and whether higher or lower is better.
- Units, normalization, aggregation, and denominator.
- Whether values are individual observations, means, medians, or something else.
- What uncertainty columns represent: standard deviation, standard error,
  confidence interval, range, or raw replicates.
- Which rows or columns correspond to methods, datasets, metrics, or conditions.
- Whether values from different scales may be compared directly.
- Whether a requested transformation or axis limit would alter interpretation.

Never invent these values or silently select an interpretation.

### Defaultable

These choices usually affect presentation rather than meaning. Choose a
publication-safe default and record it in `assumptions`.

- General venue style when no venue is named.
- Colorblind-safe categorical palette.
- Single-column or double-column size when the surrounding context implies one.
- PNG and PDF output at 300 DPI.
- Frameless legend, restrained grid, and safe font fallback.
- Legend placement, marker shape, hatch, whitespace, and annotation density.

### Optional

Do not block on decorative preferences.

- Warm versus cool mood.
- Exact accent color.
- Rounded versus square marker.
- Hand-drawn, dark, or novelty treatment unless explicitly requested.

## Mode selection

Choose the mode from the request:

- `guided`: data or a broad goal is present, but the figure design is incomplete.
- `direct`: chart, mappings, scientific semantics, and constraints are already
  clear.
- `refine`: an existing image or plotting script is the primary input.
- `multi_panel`: the request contains multiple related messages that cannot be
  shown honestly in one axes.

The user does not need to name the mode.

## Figure Brief

Before coding, create a compact brief:

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

In direct mode, keep this to a few lines and continue immediately. In guided
mode, use it to expose the interpretation before implementation.

## Question policy

Ask only questions whose answers can materially change the chart or its
scientific interpretation.

1. Batch related questions together.
2. Ask no more than three at a time.
3. Explain in one sentence why each answer matters.
4. Offer a recommended answer when a safe choice exists.
5. Do not ask the user to choose between chart types without first recommending
   one.
6. Do not repeat a question answered by the data, manuscript, filenames, or
   earlier conversation.

Example:

```text
Before I render, I need two scientific details:
1. Are the ± values standard deviations or standard errors? This changes the
   error-bar meaning and caption.
2. Is lower latency better while higher accuracy is better? If so, I recommend
   a latency-versus-accuracy scatter plot with a Pareto frontier.
```

## Proceeding without a reply

If only defaultable or optional information is missing, proceed and list the
assumptions. If critical information is missing, do not fabricate it. Produce a
draft plan or code scaffold only when useful, clearly marking it as blocked from
scientifically valid rendering.

## Refinement mode

When an existing script or image is provided:

1. Recover the data and mapping from the script or companion files.
2. Inspect the current rendered image before changing code.
3. Separate correctness problems from aesthetic problems.
4. Preserve intentional choices that are already effective.
5. Change the smallest set of parameters or plotting structures needed.
6. Re-render and compare against the original.

If only an image is available, do not reconstruct exact source values from pixel
positions. Ask for the data or script when numeric fidelity matters.
