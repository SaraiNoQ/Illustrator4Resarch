# scientific-figure-making

A global-installable Agent Skill for publication-ready Python/Matplotlib scientific figures with automatic palette and chart-style selection.

This skill separates two concepts:

- **Palette**: color choice and semantic color roles.
- **Chart style**: plot grammar, including fonts, grids, spines, linewidths, bar edges, markers, legends, and optional hand-drawn/dark/presentation forms.

## Install globally for Codex

```bash
mkdir -p ~/.agents/skills
rm -rf ~/.agents/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.agents/skills/scientific-figure-making
```

## Install globally for Claude Code

```bash
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/scientific-figure-making
cp -R skills/scientific-figure-making ~/.claude/skills/scientific-figure-making
rm -rf ~/.claude/skills/scientific-figure-making/agents
```

## Use

Codex:

```text
$scientific-figure-making
Create a paper-ready grouped bar chart.
Chart style: Nature-like compact journal style.
Palette: 简洁大气，色盲安全.
Export PNG and PDF.
```

Claude Code:

```text
/scientific-figure-making
Create a paper-ready grouped bar chart.
Chart style: IEEE Transactions compact style.
Palette: 色盲安全，主方法突出.
Export PNG and PDF.
```

## Python usage from a global install

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.agents/skills/scientific-figure-making/scripts").expanduser()))
# Claude Code path: ~/.claude/skills/scientific-figure-making/scripts

from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_toolkit import make_grouped_bar, finalize_figure

design = auto_figure_design(
    "Nature科研风格，简洁大气，色盲安全，多方法柱状图",
    figure_type="grouped_bar",
    n_colors=5,
)
style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
)
apply_publication_style(style)
```

## Preview design selection

```bash
python scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

The preview prints both palette candidates and the selected chart-style preset.

## Key files

- `SKILL.md`: agent-facing instructions.
- `scripts/figure_design.py`: heuristic palette and chart-style engine.
- `scripts/figure_toolkit.py`: plotting helpers and legacy compatibility.
- `references/palette-workflow.md`: palette heuristics and generated variants.
- `references/style-workflow.md`: chart-style presets and venue/form rules.
- `references/api-usage.md`: Python API examples.
