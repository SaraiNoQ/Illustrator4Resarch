# Illustrator4Resarch

Publication-ready scientific figure helpers with automatic palette selection.

Workflow:

1. The user describes a rough style, such as `简洁大气`, `Nature 科研风格`, `IEEE 风格`, `色盲安全`, or `黑白打印`.
2. The toolkit retrieves candidate palettes from a local curated registry inspired by ColorBrewer-like palettes, Okabe-Ito/Tol-style colorblind-safe palettes, Matplotlib scientific colormap samples, and restrained Nature/IEEE-like publication palettes.
3. The toolkit builds an LLM selection prompt from those candidates.
4. The LLM chooses the final palette and semantic role mapping.
5. Matplotlib helpers render the final experimental figure.

## Minimal usage

```python
from scientific_figure_skill import auto_palette, FigureStyle, apply_publication_style

selection = auto_palette("简洁大气，Nature 科研风格，适合多方法柱状图", figure_type="grouped_bar", n_colors=4)
style = FigureStyle(palette=selection.colors, color_roles=selection.color_roles)
apply_publication_style(style)
```

Run tests:

```bash
python -m pytest -q
```
