# Style intake

Use this reference whenever a figure request does not fully specify its visual
direction. Style intake is the first user-facing part of the workflow. It does
not replace scientific validation; it determines the visual contract before
formal rendering begins.

## 1. Prefer a designated reference image

If the user explicitly identifies an attached image as a visual reference,
inspect it before asking style questions. Recover only observable properties:

- venue or medium cues;
- chart type and mark grammar;
- background, grid, spines, ticks, legend, and annotation treatment;
- palette structure and semantic emphasis;
- serif, sans-serif, monospace, or display-font direction;
- aspect ratio, column width, margins, panels, and whitespace.

State what will be adapted rather than copied blindly. A reference may be
attractive but scientifically unsuitable for the new data; preserve its visual
language while correcting misleading chart choices, inaccessible colors, or
illegible sizing.

Do not infer an exact font family from pixels with false confidence. Describe
the category and use the closest available publication-safe fallback.

If an image is attached but its role is unclear, ask which one or more roles it
has:

1. a style reference;
2. the existing figure to refine;
3. a source of data or annotations.

When it is a table data source, follow `data-intake.md`; extracting its visible
style does not verify its transcribed numbers.

## 2. Audit five independent style dimensions

Mark each dimension `explicit`, `reference`, `delegated`, or `missing`.

| Dimension | What counts as resolved | What to ask when missing |
|---|---|---|
| Venue/use context | Named venue, paper/thesis/slides/poster, or explicit delegation | Intended venue or medium |
| Chart and grammar | Confirmed chart, usable reference grammar, or delegated recommendation | Confirm the recommended chart and axes/grid/annotation approach |
| Palette/emphasis | Named palette, semantic colors, reference palette, or delegation | Preferred color mood and how the proposed method should stand out |
| Typography | Font family/category, venue rule, reference direction, or delegation | Serif/sans direction and any mandatory typeface |
| Layout | Column width, aspect/panels/legend/content density from prompt or reference, or delegation | Single/double column, aspect, legend, panel, and density preference |

“I have not decided”, “not sure”, and “还没有决定” are unresolved requests for
guidance. “You decide”, “use your recommendation”, “其他按默认”, and “全部按推荐”
are explicit delegation.

## 3. Ask style before science in the same batch

When any dimension is missing, respond in this order:

```text
Style Brief
- Reference: none supplied
- Venue/use context: unresolved
- Recommended chart and grammar: grouped dot-interval plot; open axes; restrained x-grid
- Palette/emphasis: unresolved; recommend a colorblind-safe neutral palette with one proposed-method accent
- Typography: unresolved; recommend a clean sans-serif publication stack
- Layout: unresolved; recommend double-column landscape with a top legend
- Confirmed from input: Proposed is the semantic focus
- Still unresolved: venue, chart confirmation, palette, typography, layout

Style questions
1. Venue: Is this for a specific journal/conference, a thesis, or a general paper?
   Recommendation: general CS/ML double-column paper.
2. Chart and grammar: I recommend a grouped dot-interval plot because position
   shows close accuracy differences more honestly than truncated bars. Use this,
   grouped bars, or another form?
3. Palette: I recommend restrained neutral competitors with one blue-green
   accent for Proposed. Prefer that, monochrome, or another palette?
4. Typography: I recommend an available Arial/Helvetica-like sans-serif stack.
   Prefer sans-serif, serif, or a required venue font?
5. Layout: I recommend a double-column landscape figure with a top legend.
   Prefer single column, double column, or another aspect/panel arrangement?

Scientific interpretation
- ...

Scientific questions
1. Does `error` represent SD, SE, CI, or another quantity?
```

Ask one numbered item for every missing style dimension. Tailor recommendations
to the actual data and venue cues. Do not exceed three scientific questions in
the same batch.

## 4. Confirmation rules

The style gate closes when every dimension is resolved and the chart
recommendation is confirmed.

- Exact answers close individual dimensions.
- “Use all recommendations” closes every listed style dimension.
- A prompt that explicitly delegates all visual choices closes the style gate
  without a questionnaire.
- Uploading a designated reference closes only the dimensions that the reference
  actually demonstrates.
- Answering only scientific questions leaves unresolved style dimensions open.

Do not create a formal plotting script, final Figure Spec, or publication
PNG/PDF while the style gate is open. A temporary swatch or low-fidelity style
preview is allowed when labelled clearly and when it does not imply unresolved
scientific semantics.

Compact outer export padding is an operational quality default, not another
question the user must answer. Preserve deliberate breathing room inside the
composition, but crop blank canvas outside the outermost visible artist.

## 5. Record the source

Use one of these values in Figure Spec 1.2:

- `reference`: resolved primarily from designated reference images;
- `explicit_prompt`: specified directly in the request;
- `questionnaire`: resolved through style questions;
- `approved_recommendation`: explicitly delegated or approved as recommended.

When multiple sources contribute, record the source responsible for the
majority of the design and describe the remaining sources in `assumptions`.
