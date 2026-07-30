# scientific-figure-making v0.7

A global-installable Agent Skill that turns raw experiment data, visual references, and incomplete requests into intentionally styled, scientifically honest, visually inspected, publication-ready Python/Matplotlib figures.

Version 0.7 uses a style-first confirmation gate. If style is incomplete, it first inspects any designated reference image, creates a Style Brief, and asks separately about unresolved venue, chart grammar, palette, typography, and layout. Scientific questions such as the meaning of `error` follow in the same response. Formal rendering starts only after both style and scientific semantics are confirmed or explicitly delegated.

This skill separates four concepts:

- **Palette**: color choice and semantic color roles.
- **Chart style**: plot grammar, including grids, spines, linewidths, bar edges, markers, legends, backgrounds, and optional hand-drawn/dark/presentation forms.
- **Table style**: table grammar, including paper-style three-line tables, zebra rows, header fills, sparse rules, and compact appendix tables.
- **Font**: publication-safe font stack selection, including non-serif stacks for cartoon/anime/cute/hand-drawn styles.

These engines sit inside a confirmed guided workflow:

```text
inputs/reference -> Style Brief -> style questions -> scientific questions
                 -> confirmed Figure Brief -> Figure Spec 1.1
                 -> design engines -> script/render -> deterministic + visual QA
                 -> targeted revision -> reproducible handoff
```

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
results.csv contains my main experiment. Make the strongest honest paper figure.
Ours is the proposed method. I have not chosen the visual style yet, so ask me
about every unresolved style dimension and recommend an answer for each.
Render, validate, inspect the real image, and revise visible defects.
```

Claude Code:

```text
/scientific-figure-making
请读取 results.csv，完成论文主实验图。
Ours 是本文方法；我还没有决定图类型、配色、字体和版式，请先给出 Style Brief 并逐项询问。
生成后检查真实图片并修复问题。
```

Hand-drawn/anime-style request:

```text
/scientific-figure-making
请根据数据画一张 grouped bar。
图表风格：二次元、可爱、手绘风格。
配色要求：清新自然，色盲安全，主方法突出。
字体要求：使用期刊可接受的非衬线字体，不要 Times New Roman。
导出 PNG 和 PDF。
```

## Style coverage

Chart-style families now include:

- paper and venue styles: `publication_minimal`, `nature_journal`, `science_compact`, `ieee_transactions`, `acm_conference`, `neurips_ml`;
- Seaborn-like styles: `seaborn_whitegrid`, `seaborn_darkgrid`, `seaborn_ticks`;
- ggplot2-like styles: `ggplot_gray`, `ggplot_bw`, `ggplot_minimal`, `ggplot_classic`;
- web/editorial/dashboard styles: `datawrapper_clean`, `observable_modern`, `tableau_dashboard`, `economist_magazine`, `financial_times_report`;
- presentation and specialized styles: `thesis_clean`, `presentation_large`, `poster_infographic`, `annotation_focus`, `scientific_heatmap`, `monochrome_print`, `dense_appendix`, `soft_pastel_journal`, `cartoon_handdrawn`, `dark_presentation`, `cyber_dark`.

Palette families now include categorical, sequential, diverging, cyclic, and grayscale/print-first palettes. The engine can also generate deterministic `_muted`, `_contrast`, `_cool`, `_warm`, `_pastel`, and `_gray_generated` variants.

Table-style presets include `academic_three_line`, `journal_compact_table`, `dataframe_zebra`, `dashboard_table`, `editorial_table`, `minimal_table`, `dark_table`, `pastel_table`, and `monochrome_print_table`.

## Python usage from a global install

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/.agents/skills/scientific-figure-making/scripts").expanduser()))
# Claude Code path: ~/.claude/skills/scientific-figure-making/scripts

from figure_design import auto_figure_design, FigureStyle, apply_publication_style
from figure_fonts import select_font_family
from figure_toolkit import make_grouped_bar, finalize_figure

request = "二次元、可爱、手绘风格，色盲安全，多方法柱状图"
design = auto_figure_design(request, figure_type="grouped_bar", n_colors=5)
font_family = select_font_family(request, chart_style=design.chart_style)

style = FigureStyle(
    palette=design.palette.colors,
    color_roles=design.palette.color_roles,
    chart_style=design.chart_style,
    font_family=font_family,
)
apply_publication_style(style)
```

Inside the repository package, `cartoon_handdrawn` automatically replaces Times-like/default font stacks with a safe sans-serif stack.

## Preview design selection

```bash
python scripts/preview_palette.py "简洁大气，Nature科研风格" --figure-type grouped_bar --n-colors 5
```

The preview prints palette candidates, the selected chart-style preset, and design metadata.

## Guided workflow utilities

Create and validate a schema 1.1 Figure Spec. The initial template is
intentionally invalid until style and chart confirmation are recorded:

```bash
python scripts/figure_spec.py init --output figures/main.spec.json
python scripts/figure_spec.py validate figures/main.spec.json
```

Validate exports and create a visual-review sheet:

```bash
python scripts/validate_figure.py \
  --spec figures/main.spec.json \
  --report figures/main.qa.json

python scripts/render_preview.py \
  figures/main.png \
  --output figures/main.review.png \
  --grayscale
```

Passing deterministic QA is not visual approval. The agent must open/read the review image and inspect correctness, collisions, legibility, hierarchy, and grayscale differentiation.

## Key files

- `SKILL.md`: agent-facing instructions.
- `references/style-intake.md`: reference-first style audit and question order.
- `references/requirement-workflow.md`: style/science gates and question policy.
- `references/chart-selection.md`: chart choice driven by the scientific message.
- `references/figure-spec.md`: reproducible Figure Spec contract.
- `references/visual-qa.md`: render, inspect, revise workflow.
- `scripts/figure_design.py`: heuristic palette, chart-style, and table-style engine.
- `scripts/figure_fonts.py`: publication-safe font stack selector for standalone global scripts.
- `scripts/figure_spec.py`: standard-library Figure Spec validator.
- `scripts/figure_toolkit.py`: plotting helpers and legacy compatibility.
- `scripts/validate_figure.py`: deterministic export checks and QA report.
- `scripts/render_preview.py`: original/grayscale visual-review sheet.
- `references/palette-workflow.md`: palette heuristics and generated variants.
- `references/style-workflow.md`: chart-style presets and venue/form rules.
- `references/table-workflow.md`: table-style presets and rules.
- `references/font-workflow.md`: font registry and selection rules.
- `references/api-usage.md`: Python API examples.
