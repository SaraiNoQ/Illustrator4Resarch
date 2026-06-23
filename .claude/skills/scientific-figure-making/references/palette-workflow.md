# Palette workflow

This skill treats palette selection as a retrieval-and-decision problem.

## Pipeline

1. The user describes the desired style in natural language.
2. `request_to_tags(...)` maps style words such as `简洁`, `Nature`, `IEEE`, `色盲安全`, `黑白打印`, `热力图`, and `差异` to retrieval tags.
3. `suggest_palettes(...)` retrieves ranked candidates from `PALETTE_REGISTRY`.
4. `build_llm_palette_selection_prompt(...)` creates a strict JSON prompt for model-side final selection.
5. `apply_llm_palette_decision(...)` validates the selected palette and role mapping.
6. If no model decision is available, `auto_palette(...)` deterministically chooses the highest-scoring candidate.

## Recommended palette families

- `nature_modern`: muted, high-impact journal style for multi-method comparisons.
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

## Selection heuristics

- `Nature科研风格 + grouped_bar`: start with `nature_modern` or `nature_soft`.
- `IEEE + engineering + clean`: start with `ieee_clean` or `minimal_blue_gray`.
- `色盲安全 + 多方法`: start with `okabe_ito` or `tol_bright`.
- `热力图 + 连续`: start with `viridis_sample`, `cividis_sample`, or `blue_sequential`.
- `正负差异 + heatmap`: start with `blue_orange_diverging`.
- `黑白打印`: start with `print_gray` and use hatching/markers.

## Anti-patterns

- Do not choose palettes only because they look fashionable.
- Do not use rainbow palettes for continuous scientific values.
- Do not use low-contrast pastel palettes for dense multi-method comparisons.
- Do not use red/green as the only distinction between important methods.
- Do not overuse highlight colors.
