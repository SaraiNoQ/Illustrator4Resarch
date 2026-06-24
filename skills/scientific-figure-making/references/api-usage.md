# API usage

This skill supports two execution modes and two independent design layers:

1. **Palette engine**: color choice, semantic color roles, generated palette variants.
2. **Chart-style engine**: fonts, grid, spines, line widths, bar edges, legend behavior, and special forms such as seaborn-like or hand-drawn styles.

Do not collapse these two layers into one. A Nature-like chart style can still use a colorblind palette; an IEEE-style chart can still use a warm palette if the user asks for it.

## Mode A: inside the Illustrator4Resarch repository

When the agent is working inside this repository, import the maintained package:

```python
from scientific_figure_skill import (
    auto_palette,
    suggest_palettes,
    auto_figure_design,
    resolve_chart_style,
    build_llm_palette_selection_prompt,
    build_llm_chart_style_prompt,
    apply_llm_palette_decision,
    FigureStyle,
    apply_publication_style,
    make_grouped_bar,
    finalize_figure,
)
```

## Mode B: globally installed standalone skill

When the skill has been copied to a global agent directory, use the bundled standalone design engine plus plotting helpers.

For Claude Code personal install:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.claude/skills/scientific-figure-making/scripts").expanduser()))

from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_toolkit import make_grouped_bar, finalize_figure
```

For Codex user install:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.agents/skills/scientific-figure-making/scripts").expanduser()))

from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_toolkit import make_grouped_bar, finalize_figure
```

## One-call automatic design

```python
design = auto_figure_design(
    request="简洁大气，Nature科研风格，色盲安全，适合多方法柱状图",
    figure_type="grouped_bar",
    n_colors=4,
)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
)
apply_publication_style(style)
```

`auto_figure_design(...)` returns:

- `design.palette`: selected palette, generated colors if needed, semantic roles, candidate list, LLM prompt.
- `design.chart_style`: selected chart-style preset such as `nature_journal`, `ieee_transactions`, `seaborn_whitegrid`, or `cartoon_handdrawn`.
- `design.reason`: concise explanation of the palette/style decision.

## Deterministic palette selection only

```python
selection = auto_palette(
    request="清透克制但没有明确预设关键词",
    figure_type="grouped_bar",
    n_colors=5,
)
```

The fallback does not fail when words are unseen. It infers a request profile, evaluates candidate palettes by objective quality metrics, generates variants when useful, and chooses the best-scoring candidate.

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
```

Send `prompt` to an LLM. The LLM should return strict JSON with `selected_palette`, `reason`, and `color_roles`. Validate the JSON with `apply_llm_palette_decision(...)`.

## Chart-style selection only

```python
preset = resolve_chart_style(
    request="IEEE Transactions 风格，多方法柱状图",
    figure_type="grouped_bar",
)
```

Available presets include:

- `publication_minimal`
- `nature_journal`
- `ieee_transactions`
- `acm_conference`
- `neurips_ml`
- `seaborn_whitegrid`
- `seaborn_ticks`
- `boxed_classic`
- `thesis_clean`
- `presentation_large`
- `cartoon_handdrawn`
- `dark_presentation`

LLM-assisted chart-style selection:

```python
prompt = build_llm_chart_style_prompt(
    request="卡通手绘风格，用于解释机制，不是正式论文主图",
    figure_type="schematic",
)
```

## Rendering

```python
fig, ax = plt.subplots(figsize=(10, 4))
make_grouped_bar(
    ax,
    categories=datasets,
    series=values,
    labels=methods,
    ylabel="Accuracy (%)",
    palette=design.palette.colors,
    annotate=True,
)
ax.legend(ncol=2)
finalize_figure(fig, "figures/main_comparison", formats=["png", "pdf"])
```

## Preview CLI

```bash
python scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

The preview now prints both palette candidates and the selected chart-style preset.
