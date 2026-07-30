# Figure Spec

For substantive figure-generation tasks, store the confirmed plan as JSON next
to the output. The spec is a reproducibility and validation artifact; it is not
a form the user must fill out.

New figures use schema 1.1. Schema 1.0 remains readable for compatibility, but
validation warns that it lacks an explicit style-confirmation record.

## Schema 1.1

```json
{
  "schema_version": "1.1",
  "mode": "guided",
  "research_goal": {
    "question": "Which method performs best across datasets?",
    "message": "The proposed method is consistently strongest.",
    "metric_direction": "higher"
  },
  "data": {
    "source": "results.csv",
    "structure": "method_by_dataset",
    "metrics": ["Accuracy (%)"],
    "uncertainty": {
      "kind": "sd",
      "source": "error column confirmed by the user"
    }
  },
  "chart": {
    "type": "grouped_dot_interval",
    "selection_status": "confirmed",
    "x": "Accuracy (%)",
    "y": "dataset",
    "series": "method",
    "panels": []
  },
  "design": {
    "style_status": "confirmed",
    "style_source": "questionnaire",
    "reference_images": [],
    "venue": "general_cs_ml_paper",
    "column_width": "double",
    "chart_style": "publication_minimal",
    "palette_request": "neutral competitors with a blue-green Proposed accent",
    "font_request": "available Arial/Helvetica-like sans-serif",
    "graphic_grammar": "open axes, restrained x-grid, distinct markers",
    "layout_request": "double-column landscape with top legend",
    "semantic_roles": {
      "Proposed": "proposed"
    },
    "accessibility": [
      "colorblind_safe",
      "grayscale_distinguishable"
    ]
  },
  "output": {
    "stem": "figures/main_comparison",
    "formats": ["png", "pdf"],
    "dpi": 300
  },
  "assumptions": [
    "The user approved the recommended publication-minimal style."
  ],
  "open_questions": [],
  "acceptance_criteria": [
    "All values are represented exactly once.",
    "Labels remain legible at confirmed double-column width."
  ]
}
```

## Confirmation fields

- `chart.selection_status` is `recommended` or `confirmed`.
- `design.style_status` is `pending` or `confirmed`.
- `design.style_source` is `reference`, `explicit_prompt`, `questionnaire`, or
  `approved_recommendation`.
- `design.reference_images` lists designated style-reference paths. It must be
  non-empty when `style_source` is `reference`.
- `font_request`, `graphic_grammar`, and `layout_request` record the resolved
  intent, not only the renderer's implementation details.

A schema 1.1 spec is invalid while style is pending or chart selection is only
recommended. Generate the formal spec after the user confirms or delegates the
choices; a pre-confirmation draft may be saved separately but must not validate
as render-ready.

## General rules

- Use `metric_direction` values `higher`, `lower`, `mixed`, or `unknown`.
- Use `mode` values `guided`, `direct`, `refine`, or `multi_panel`.
- Represent unresolved questions as objects with `question`, `reason`, and
  `severity`. `severity` is `critical` or `preference`.
- A critical scientific question blocks valid rendering.
- A preference question cannot override a pending schema 1.1 style gate.
- `data.source` may name a file or use `embedded`; do not duplicate large data
  arrays when a source file exists.
- `chart.x`, `chart.y`, and `chart.series` describe semantic mappings.
- `output.stem` has no extension. Formats are added during export.
- Include actual output DPI.
- Record material defaults and delegated decisions in `assumptions`.
- Acceptance criteria should be checkable in the final image or code.

## Commands

Create a schema 1.1 template:

```bash
python scripts/figure_spec.py init --output figures/main.spec.json
```

Validate before formal rendering:

```bash
python scripts/figure_spec.py validate figures/main.spec.json
```

Request machine-readable validation:

```bash
python scripts/figure_spec.py validate figures/main.spec.json --json
```

The script exits non-zero when errors exist. Warnings identify compatibility or
publication metadata issues that do not make a confirmed figure invalid.
