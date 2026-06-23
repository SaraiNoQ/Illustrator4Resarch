---
name: scientific-figure-making
description: Use this skill for publication-ready Matplotlib research figures with automatic palette retrieval and LLM-assisted palette selection.
---

# Scientific figure making

Workflow:

1. Parse figure type: grouped bar, ablation, trend line, heatmap, scatter, multi-panel.
2. Parse user style words: `简洁大气`, `Nature 科研风格`, `IEEE 风格`, `柔和`, `高对比`, `色盲安全`, `黑白打印`.
3. Call `suggest_palettes()` to retrieve candidate palettes from the local registry.
4. Call `build_llm_palette_selection_prompt()` to let the LLM select the best palette.
5. If no external LLM decision is available, use `auto_palette()` as deterministic fallback.
6. Apply the selected palette through `FigureStyle(palette=selection.colors, color_roles=selection.color_roles)`.
7. Generate complete runnable Python/Matplotlib code and export PNG + PDF.

Rules:

- Categorical method comparisons: prefer clear inter-series separation and colorblind safety.
- Heatmaps/scalar fields: prefer sequential palettes.
- Signed differences/residuals: prefer diverging palettes.
- Nature style: prefer muted, elegant, high-impact palettes.
- IEEE style: prefer restrained blue-gray engineering palettes.
- Print-first: prefer grayscale/print-safe palettes plus hatch/marker encodings.

Output contract:

1. Explain the selected palette in 3-5 sentences.
2. Show palette name, hex colors, and semantic role mapping.
3. Provide complete runnable Python code.
4. Save PNG and PDF outputs.
5. Do not use seaborn unless explicitly requested.
