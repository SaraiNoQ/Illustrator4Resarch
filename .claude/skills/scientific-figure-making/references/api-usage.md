# API usage

Import the public API:

```python
from scientific_figure_skill import (
    auto_palette,
    suggest_palettes,
    build_llm_palette_selection_prompt,
    apply_llm_palette_decision,
    FigureStyle,
    apply_publication_style,
    make_grouped_bar,
    finalize_figure,
)
```

## Deterministic palette selection

```python
selection = auto_palette(
    request="简洁大气，Nature科研风格，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=4,
)
```

## LLM-assisted palette selection

```python
candidates = suggest_palettes(
    request="色盲安全，简洁，适合论文主实验",
    figure_type="grouped_bar",
    n_colors=5,
)

prompt = build_llm_palette_selection_prompt(
    request="色盲安全，简洁，适合论文主实验",
    figure_type="grouped_bar",
    candidates=candidates,
    n_colors=5,
)

# Send prompt to an LLM. The LLM should return strict JSON.
decision = {
    "selected_palette": "okabe_ito",
    "reason": "Colorblind-safe categorical separation for multiple methods.",
    "color_roles": {
        "proposed": "#0072B2",
        "baseline": "#D55E00",
        "secondary": "#009E73",
        "ablation": "#CC79A7",
        "neutral": "#999999",
        "highlight": "#E69F00"
    }
}

selection = apply_llm_palette_decision(decision, candidates)
```

## Rendering

```python
style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

Use `make_grouped_bar(...)` for grouped comparison bars, then call:

```python
finalize_figure(fig, "figures/main_comparison", formats=["png", "pdf"])
```
