# Font workflow

The font engine is a separate layer from palette and chart style. It prevents a generated Matplotlib script from falling back to a visually wrong font, such as Times New Roman in a cartoon/anime/hand-drawn plot.

## Design rule

Use only publication-safe font stacks. For playful visual styles, choose a readable sans-serif stack from the safe registry rather than a decorative novelty font.

Built-in registry keys:

- `arial`: default journal/conference sans-serif stack.
- `helvetica`: compact Nature/Science-like sans-serif stack.
- `source_sans`: modern ML-conference/report sans-serif stack.
- `noto_sans`: Unicode/CJK-capable sans-serif fallback stack.
- `trebuchet_sans`: rounded/humanist sans-serif stack for hand-drawn, cartoon, anime, or cute chart styles.
- `verdana`: wide readable sans-serif stack for slides or dense labels.
- `cmu_sans`: LaTeX-compatible sans-serif stack.
- `times`: traditional serif stack, allowed for conservative formal styles but not for cartoon/anime/hand-drawn requests.
- `stix`: math-friendly serif stack.

## Heuristic behavior

Requests containing `二次元`, `可爱`, `手绘`, `卡通`, `anime`, `kawaii`, `cartoon`, `handdrawn`, or `xkcd` are forced toward a sans-serif candidate. The preferred candidate is usually `trebuchet_sans`:

```python
("Trebuchet MS", "Verdana", "Arial", "Helvetica", "DejaVu Sans", "sans-serif")
```

Formal venue cues such as `Nature`, `IEEE`, `ACM`, `NeurIPS`, `ICML`, or `ICLR` are scored toward Arial/Helvetica/Source Sans style stacks.

## Repository package usage

```python
from scientific_figure_skill import auto_figure_design, FigureStyle, apply_publication_style

request = "二次元、可爱、手绘风格 grouped bar，色盲安全"
design = auto_figure_design(request, figure_type="grouped_bar", n_colors=4)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
)
apply_publication_style(style)
```

For `cartoon_handdrawn`, repository mode automatically replaces default or Times-like font stacks with the selected sans-serif stack.

## Explicit font selection

```python
from scientific_figure_skill import select_font_family

font_family = select_font_family(
    request="二次元、可爱、手绘风格",
    chart_style="cartoon_handdrawn",
)

# Use in a manually constructed style:
style = FigureStyle(font_family=font_family, chart_style="cartoon_handdrawn")
```

## Standalone global skill usage

A globally installed skill can use `scripts/figure_fonts.py`:

```python
from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_fonts import select_font_family

request = "二次元、可爱、手绘风格 grouped bar"
design = auto_figure_design(request, figure_type="grouped_bar", n_colors=4)
font_family = select_font_family(request, chart_style=design.chart_style)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
    font_family=font_family,
)
apply_publication_style(style)
```

## LLM-side judgment

When an LLM needs to make the final decision, call `build_llm_font_selection_prompt(...)`. The prompt instructs the model to choose only from the registry and to avoid serif fonts for cartoon/anime/hand-drawn requests.
