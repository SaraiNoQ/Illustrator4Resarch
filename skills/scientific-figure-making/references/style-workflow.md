# Chart style workflow

Palette, chart style, table style, and font choice are separate design layers.

- Palette controls color and semantic color roles.
- Chart style controls plot grammar: grids, spines, line widths, markers, legend, background, and sketch effects.
- Table style controls header emphasis, row rules, zebra rows, and cell density.
- Font choice is handled by the font engine.

## Pipeline

1. Parse the request for venue, ecosystem, output medium, and figure type cues.
2. Call `resolve_chart_style(...)` for chart grammar.
3. Call `auto_palette(...)` or `auto_figure_design(...)` separately for colors.
4. For tables, call `resolve_table_style(...)` or use `design.table_style`.
5. Apply chart form with `apply_publication_style(...)`.
6. Apply table form with `apply_table_style(...)` when using Matplotlib tables.

## Chart-style families

### Paper and venue styles

- `publication_minimal`: safe general academic default.
- `nature_journal`: compact high-impact journal panel.
- `science_compact`: very compact Science/Cell-like panel.
- `ieee_transactions`: engineering-paper style with restrained y-grid.
- `acm_conference`: compact CS conference figure.
- `neurips_ml`: modern ML conference style.

### Seaborn-like styles

- `seaborn_whitegrid`: white background with light grid.
- `seaborn_darkgrid`: pale panel with white grid.
- `seaborn_ticks`: tick-focused style with little grid emphasis.

### ggplot2-like styles

- `ggplot_gray`: gray panel with white grid.
- `ggplot_bw`: boxed black-and-white panel.
- `ggplot_minimal`: minimal non-data ink with light grid.
- `ggplot_classic`: axis-line-only statistical figure.

### Web, editorial, and dashboard styles

- `datawrapper_clean`: newsroom/editorial chart grammar.
- `observable_modern`: D3/Observable-like web chart grammar.
- `tableau_dashboard`: screen-readable dashboard grammar.
- `economist_magazine`: magazine-like editorial chart.
- `financial_times_report`: warm editorial report style.

### Presentation and explanatory styles

- `thesis_clean`: larger report/thesis figure.
- `presentation_large`: talk and defense figure.
- `poster_infographic`: poster-scale figure.
- `annotation_focus`: explanatory chart with annotation-friendly spacing.

### Specialized styles

- `scientific_heatmap`: heatmap/matrix-first style.
- `monochrome_print`: black-and-white print style.
- `dense_appendix`: compact supplement style.
- `soft_pastel_journal`: soft friendly academic style without sketch jitter.
- `cartoon_handdrawn`: readable hand-drawn style with subtle sketching.
- `dark_presentation`: dark slide style.
- `cyber_dark`: dark technical demo style.

## Decision rules

- Main-paper results: prefer `publication_minimal`, `nature_journal`, `science_compact`, `ieee_transactions`, `acm_conference`, or `neurips_ml`.
- Statistical exploration: allow Seaborn-like or ggplot2-like presets.
- Newsroom/report charts: allow Datawrapper/Economist/Financial-Times-like presets.
- Dashboard output: use `tableau_dashboard`.
- Heatmaps: prefer `scientific_heatmap` and sequential/diverging palettes.
- Print: use `monochrome_print` plus marker or hatch redundancy.
- Cute or anime-like requests: use `cartoon_handdrawn` only when explicitly requested; otherwise prefer `soft_pastel_journal`.
- Dark backgrounds are for slides, demos, and posters, not normal paper submission.
