# Palette workflow

This skill now treats palette selection as a heuristic retrieval, scoring, generation, and optional model-selection problem. It is no longer a fixed keyword-to-palette table.

## Pipeline

1. The user describes the desired visual feeling in natural language.
2. `infer_palette_intent(...)` converts the request into a lightweight profile: data kind, mood, temperature, contrast, colorblind preference, print preference, density, and venue hint.
3. The engine evaluates palette candidates with objective quality metrics:
   - minimum pairwise color distance;
   - luminance range;
   - hue spread;
   - mean saturation;
   - monotone luminance for sequential palettes.
4. The engine generates candidate variants when useful:
   - muted publication variants;
   - high-contrast dense-comparison variants;
   - cool or warm variants;
   - grayscale print variants.
5. `suggest_palettes(...)` ranks base and generated candidates by request fit plus quality metrics.
6. `build_llm_palette_selection_prompt(...)` exposes the profile, quality metrics, and candidate metadata to the model for final judgment.
7. `auto_palette(...)` remains the deterministic fallback when no explicit model-side decision is used.

## Why this is better than fixed keywords

The old approach mainly matched words such as `Nature`, `IEEE`, `色盲安全`, or `热力图` to predefined tags. If the user said something not in the table, ranking degraded into a brittle fallback.

The new approach still uses known cues when available, but it also scores the actual color sets. Unknown phrases no longer make the system fail; they simply lower semantic confidence, so objective palette quality and figure type dominate the selection.

Example:

```python
selection = auto_palette(
    request="清透克莱因式克制氛围但没有预设关键词",
    figure_type="grouped_bar",
    n_colors=5,
)
```

This returns a valid palette because the system falls back to color-quality scoring instead of requiring an exact keyword.

## Palette quality metrics

For categorical method comparison, prefer:

- sufficient number of colors;
- large minimum pairwise distance;
- enough hue spread;
- enough luminance range for black-and-white robustness;
- moderate saturation rather than neon colors.

For sequential heatmaps, prefer:

- monotone luminance;
- strong endpoint contrast;
- perceptually ordered progression.

For diverging heatmaps, prefer:

- strong contrast between both ends;
- a visually neutral midpoint;
- no red/green-only distinction.

## Generated variants

Generated variants are named with suffixes such as:

- `_muted`: lower saturation and slightly lighter colors for refined journal panels;
- `_contrast`: stronger separation for dense multi-method plots;
- `_cool`: blue/teal-shifted palette for technical or engineering figures;
- `_warm`: red/orange/gold-shifted palette for review or narrative figures;
- `_gray_generated`: monotone grayscale fallback for print.

Generated palettes are not random. They are deterministic transformations of curated base palettes and are still scored before selection.

## Recommended palette families

- `nature_modern`: muted high-impact journal style for multi-method comparisons.
- `nature_soft`: softer style for elegant paper panels and slides.
- `ieee_clean`: restrained engineering palette.
- `minimal_blue_gray`: conservative blue-gray palette for serious technical figures.
- `okabe_ito`: strong colorblind-safe categorical palette.
- `tol_bright`: bright but still research-appropriate categorical palette.
- `brewer_set2`: soft qualitative palette.
- `viridis_sample`: perceptually ordered sequential heatmaps.
- `cividis_sample`: color-vision-deficiency optimized sequential palette.
- `blue_orange_diverging`: signed differences and residual heatmaps.
- `print_gray`: grayscale-first palette for print.
- `warm_muted`: muted warm palette for review/narrative figures.

## Anti-patterns

- Do not choose palettes only because they look fashionable.
- Do not use rainbow palettes for continuous scientific values.
- Do not use low-contrast pastel palettes for dense multi-method comparisons.
- Do not use red/green as the only distinction between important methods.
- Do not overuse highlight colors.
- Do not confuse palette with chart style. Palette controls color; chart style controls form.
