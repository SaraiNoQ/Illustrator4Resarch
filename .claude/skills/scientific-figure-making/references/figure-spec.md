# Figure Spec

For substantive figure-generation tasks, store the confirmed plan as JSON next
to the output. The spec is a reproducibility and validation artifact; it is not
a form the user must fill out.

New figures use schema 1.2. Schema 1.0 and 1.1 remain readable for compatibility.
Validation warns that 1.0 lacks style confirmation and that both legacy versions
lack an explicit data-verification record.

## Schema 1.2

```json
{
  "schema_version": "1.2",
  "mode": "guided",
  "research_goal": {
    "question": "Which method performs best across datasets?",
    "message": "The proposed method is consistently strongest.",
    "metric_direction": "higher"
  },
  "data": {
    "source": "results.tex",
    "normalized_sources": [
      "main_comparison.data.csv"
    ],
    "intake_report": "main_comparison.data-audit.json",
    "verification_status": "verified",
    "verification_method": "deterministic_parse",
    "structure": "method_by_dataset",
    "metrics": ["Accuracy (%)"],
    "uncertainty": {
      "kind": "sd",
      "source": "error column confirmed by the user"
    },
    "transformations": [
      "Converted the verified wide source table to long records in the plotting script."
    ]
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
    "Labels remain legible at confirmed double-column width.",
    "Outer export margins are compact without clipping any artist."
  ]
}
```

## Data and confirmation fields

- `chart.selection_status` is `recommended` or `confirmed`.
- `design.style_status` is `pending` or `confirmed`.
- `design.style_source` is `reference`, `explicit_prompt`, `questionnaire`, or
  `approved_recommendation`.
- `design.reference_images` lists designated style-reference paths. It must be
  non-empty when `style_source` is `reference`.
- `font_request`, `graphic_grammar`, and `layout_request` record the resolved
  intent, not only the renderer's implementation details.
- `data.normalized_sources` lists the verified CSV tables used by the plotting
  script. Paths are resolved relative to the Figure Spec during validation.
- `data.intake_report` points to the validated source/normalized provenance
  report.
- `data.verification_status` is `pending` or `verified`.
- `data.verification_method` is `deterministic_parse`, `user_confirmed`, or
  `mixed`.
- `data.transformations` records wide/long reshaping, filtering, sorting,
  aggregation, normalization, or unit conversion.

A schema 1.2 spec is invalid while data or style is pending, chart selection is
only recommended, normalized files or the intake report are missing/invalid, or
a critical scientific question remains. Generate the formal spec after all
three gates close; a pre-confirmation draft may be saved separately but must not
validate as render-ready.

## General rules

- Use `metric_direction` values `higher`, `lower`, `mixed`, or `unknown`.
- Use `mode` values `guided`, `direct`, `refine`, or `multi_panel`.
- Represent unresolved questions as objects with `question`, `reason`, and
  `severity`. `severity` is `critical` or `preference`.
- A critical scientific question blocks valid rendering.
- A preference question cannot override a pending schema 1.2 data or style gate.
- `data.source` identifies the original authoritative input or uses `embedded`;
  `normalized_sources` identifies what the plotting script actually reads.
- Validate `data.intake_report` before the Figure Spec. Do not duplicate large
  data arrays in the spec.
- `chart.x`, `chart.y`, and `chart.series` describe semantic mappings.
- `output.stem` has no extension. Formats are added during export.
- Include actual output DPI.
- Record material defaults and delegated decisions in `assumptions`.
- Acceptance criteria should be checkable in the final image or code.
- Record intentional large outer margins in `design.layout_request`; otherwise
  unresolved `outer_whitespace` warnings should trigger a tighter re-export.

## Commands

Create a schema 1.2 template:

```bash
python scripts/figure_spec.py init --output figures/main.spec.json
```

Validate data provenance and then the spec before formal rendering:

```bash
python scripts/data_intake.py validate figures/main.data-audit.json
python scripts/figure_spec.py validate figures/main.spec.json
```

Request machine-readable validation:

```bash
python scripts/figure_spec.py validate figures/main.spec.json --json
```

The script exits non-zero when errors exist. Warnings identify compatibility or
publication metadata issues that do not make a confirmed figure invalid.
