# Palette workflow

Palette selection is a heuristic retrieval, scoring, generation, and optional model-selection problem. It is not a fixed keyword-to-color table.

## Pipeline

1. The user describes the desired visual feeling in natural language.
2. `infer_palette_intent(...)` converts the request into a lightweight profile: data kind, mood, temperature, contrast, colorblind preference, print preference, density, and venue hint.
3. The engine evaluates palette candidates with objective quality metrics: minimum pairwise distance, luminance range, hue spread, mean saturation, and monotone luminance.
4. The engine generates deterministic variants when useful.
5. `suggest_palettes(...)` ranks base and generated candidates by request fit plus quality metrics.
6. `build_llm_palette_selection_prompt(...)` exposes intent, quality metrics, and candidate metadata to the model for final judgment.
7. `auto_palette(...)` remains the deterministic fallback when no explicit model-side decision is used.

## Data roles

- Categorical: method comparison, grouped bars, line charts, ablations.
- Sequential: heatmaps, magnitudes, counts, monotone ordered values.
- Diverging: signed differences, residuals, deltas, correlations centered around zero.
- Cyclic: phase, angle, direction, periodic values.
- Grayscale: black-and-white print or strict journal constraints.

## Recommended palette families

### Categorical

- `okabe_ito`, `tol_bright`, `tol_vibrant`, `tol_muted`.
- `seaborn_deep`, `seaborn_muted`, `seaborn_colorblind`.
- `tableau_10`, `observable_10`.
- `brewer_set2`, `brewer_dark2`, `brewer_paired`, `brewer_set3`.
- `nature_modern`, `nature_soft`, `ieee_clean`, `minimal_blue_gray`.
- `datawrapper_neutral`, `economist_modern`, `financial_times_warm`.
- `kawaii_pastel`, `earth_tone`, `ocean_science`, `nordic_calm`, `solarized_accent`.

### Sequential

- `viridis_sample`, `viridis_extended`, `cividis_sample`.
- `magma_extended`, `plasma_extended`, `inferno_extended`.
- `blue_sequential`, `blue_green_sequential`, `orange_red_sequential`.

### Diverging

- `blue_orange_diverging`, `red_blue_diverging`, `purple_green_diverging`.
- `brown_teal_diverging`, `coolwarm_soft`.

### Cyclic and print

- `twilight_cyclic` for phase, angle, and periodic variables.
- `print_gray` and generated `_gray_generated` variants for print-first figures.

## Generated variants

Generated variants are deterministic transformations of curated base palettes:

- `_muted`: lower saturation and slightly lighter colors for refined journal panels.
- `_contrast`: stronger separation for dense multi-method plots.
- `_cool`: blue/teal-shifted palette for technical or engineering figures.
- `_warm`: red/orange/gold-shifted palette for narrative or review figures.
- `_pastel`: softer playful palette for cute explanatory figures.
- `_gray_generated`: monotone grayscale fallback for print.

## Rules

- For categorical method comparison, prefer enough colors, hue separation, luminance separation, and moderate saturation.
- For sequential heatmaps, prefer monotone lightness and strong endpoint contrast.
- For diverging heatmaps, prefer a neutral midpoint and avoid red/green-only distinction.
- For cyclic variables, use a closed-loop palette rather than a sequential ramp.
- Do not choose palettes only because they look fashionable.
- Do not use rainbow palettes for continuous scientific values.
- Do not overuse highlight colors.
- Do not confuse palette with chart style.
