# Figure Spec

For substantive figure-generation tasks, store the resolved plan as JSON next
to the output. The spec is a reproducibility and validation artifact; it is not
a form the user must fill out.

## Schema

```json
{
  "schema_version": "1.0",
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
      "kind": "none",
      "source": null
    }
  },
  "chart": {
    "type": "grouped_bar",
    "x": "dataset",
    "y": "Accuracy (%)",
    "series": "method",
    "panels": []
  },
  "design": {
    "venue": "general_publication",
    "column_width": "double",
    "chart_style": "publication_minimal",
    "palette_request": "colorblind-safe",
    "semantic_roles": {
      "My Method": "proposed"
    },
    "accessibility": ["colorblind_safe", "grayscale_distinguishable"]
  },
  "output": {
    "stem": "figures/main_comparison",
    "formats": ["png", "pdf"],
    "dpi": 300
  },
  "assumptions": [
    "No uncertainty was supplied, so no error bars are shown."
  ],
  "open_questions": [],
  "acceptance_criteria": [
    "All method and dataset values are represented once.",
    "Labels remain legible at double-column width."
  ]
}
```

## Rules

- Use `metric_direction` values `higher`, `lower`, `mixed`, or `unknown`.
- Use `mode` values `guided`, `direct`, `refine`, or `multi_panel`.
- Represent unresolved questions as objects with `question`, `reason`, and
  `severity`. `severity` is `critical` or `preference`.
- A critical open question blocks scientifically valid rendering.
- `data.source` may name a file or use `embedded`; do not duplicate large data
  arrays in the spec when a source file already exists.
- `chart.x`, `chart.y`, and `chart.series` describe semantic mappings, not
  arbitrary column letters.
- `output.stem` has no extension. Formats are added during export.
- Include the actual output DPI, not only the intended DPI.
- Record every material default in `assumptions`.
- Acceptance criteria should be checkable in the final image or code.

## Commands

Create a starting template:

```bash
python scripts/figure_spec.py init --output figures/main.spec.json
```

Validate before rendering:

```bash
python scripts/figure_spec.py validate figures/main.spec.json
```

Request machine-readable validation:

```bash
python scripts/figure_spec.py validate figures/main.spec.json --json
```

The script exits non-zero when errors exist. Warnings identify recommended
publication metadata that may safely use documented defaults.
