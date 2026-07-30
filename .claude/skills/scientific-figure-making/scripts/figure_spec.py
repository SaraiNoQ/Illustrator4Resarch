#!/usr/bin/env python3
"""Create and validate portable Figure Spec JSON files.

The validator intentionally uses only the Python standard library so the
standalone skill can run before plotting dependencies are imported.
"""
from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
MODES = {"guided", "direct", "refine", "multi_panel"}
METRIC_DIRECTIONS = {"higher", "lower", "mixed", "unknown"}
QUESTION_SEVERITIES = {"critical", "preference"}
OUTPUT_FORMATS = {"png", "pdf", "svg", "eps"}
UNCERTAINTY_KINDS = {
    "none",
    "sd",
    "se",
    "ci",
    "range",
    "percentile",
    "raw_replicates",
    "unknown",
}


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [asdict(issue) for issue in self.errors],
            "warnings": [asdict(issue) for issue in self.warnings],
        }


def default_spec() -> dict[str, Any]:
    """Return an editable Figure Spec template."""
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "guided",
        "research_goal": {
            "question": "",
            "message": "",
            "metric_direction": "unknown",
        },
        "data": {
            "source": "",
            "structure": "",
            "metrics": [],
            "uncertainty": {"kind": "unknown", "source": None},
        },
        "chart": {
            "type": "",
            "x": "",
            "y": "",
            "series": "",
            "panels": [],
        },
        "design": {
            "venue": "general_publication",
            "column_width": "double",
            "chart_style": "publication_minimal",
            "palette_request": "colorblind-safe",
            "semantic_roles": {},
            "accessibility": [
                "colorblind_safe",
                "grayscale_distinguishable",
            ],
        },
        "output": {
            "stem": "figures/figure",
            "formats": ["png", "pdf"],
            "dpi": 300,
        },
        "assumptions": [],
        "open_questions": [],
        "acceptance_criteria": [],
    }


def load_spec(path: str | Path) -> dict[str, Any]:
    """Load a Figure Spec and require a JSON object at the root."""
    spec_path = Path(path)
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Figure Spec root must be a JSON object.")
    return payload


def _mapping(
    value: Any,
    path: str,
    errors: list[ValidationIssue],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(ValidationIssue("error", path, "must be an object"))
        return {}
    return value


def _nonempty_text(
    value: Any,
    path: str,
    errors: list[ValidationIssue],
) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(ValidationIssue("error", path, "must be a non-empty string"))
        return ""
    return value.strip()


def _string_list(
    value: Any,
    path: str,
    errors: list[ValidationIssue],
    *,
    allow_empty: bool,
) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(
            ValidationIssue("error", path, "must be a list of non-empty strings")
        )
        return []
    if not allow_empty and not value:
        errors.append(ValidationIssue("error", path, "must not be empty"))
    return [item.strip() for item in value]


def validate_spec(spec: Mapping[str, Any]) -> ValidationResult:
    """Validate scientific blockers and the portable Figure Spec structure."""
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    schema_version = spec.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        errors.append(
            ValidationIssue(
                "error",
                "schema_version",
                f"must equal {SCHEMA_VERSION!r}",
            )
        )

    mode = _nonempty_text(spec.get("mode"), "mode", errors)
    if mode and mode not in MODES:
        errors.append(
            ValidationIssue(
                "error",
                "mode",
                f"must be one of {sorted(MODES)}",
            )
        )

    goal = _mapping(spec.get("research_goal"), "research_goal", errors)
    _nonempty_text(goal.get("question"), "research_goal.question", errors)
    _nonempty_text(goal.get("message"), "research_goal.message", errors)
    metric_direction = _nonempty_text(
        goal.get("metric_direction"),
        "research_goal.metric_direction",
        errors,
    )
    if metric_direction and metric_direction not in METRIC_DIRECTIONS:
        errors.append(
            ValidationIssue(
                "error",
                "research_goal.metric_direction",
                f"must be one of {sorted(METRIC_DIRECTIONS)}",
            )
        )
    elif metric_direction == "unknown":
        warnings.append(
            ValidationIssue(
                "warning",
                "research_goal.metric_direction",
                "is unknown; confirm it when direction affects interpretation",
            )
        )

    data = _mapping(spec.get("data"), "data", errors)
    _nonempty_text(data.get("source"), "data.source", errors)
    _nonempty_text(data.get("structure"), "data.structure", errors)
    _string_list(data.get("metrics"), "data.metrics", errors, allow_empty=False)
    uncertainty = _mapping(data.get("uncertainty"), "data.uncertainty", errors)
    uncertainty_kind = _nonempty_text(
        uncertainty.get("kind"),
        "data.uncertainty.kind",
        errors,
    )
    if uncertainty_kind and uncertainty_kind not in UNCERTAINTY_KINDS:
        errors.append(
            ValidationIssue(
                "error",
                "data.uncertainty.kind",
                f"must be one of {sorted(UNCERTAINTY_KINDS)}",
            )
        )
    elif uncertainty_kind == "unknown":
        warnings.append(
            ValidationIssue(
                "warning",
                "data.uncertainty.kind",
                "is unknown; do not render error bars until it is resolved",
            )
        )

    chart = _mapping(spec.get("chart"), "chart", errors)
    chart_type = _nonempty_text(chart.get("type"), "chart.type", errors)
    if chart_type not in {"table", "schematic"}:
        _nonempty_text(chart.get("x"), "chart.x", errors)
        _nonempty_text(chart.get("y"), "chart.y", errors)
    panels = chart.get("panels", [])
    if not isinstance(panels, list):
        errors.append(ValidationIssue("error", "chart.panels", "must be a list"))

    design = _mapping(spec.get("design"), "design", errors)
    if not isinstance(design.get("semantic_roles", {}), Mapping):
        errors.append(
            ValidationIssue("error", "design.semantic_roles", "must be an object")
        )
    accessibility = design.get("accessibility", [])
    if not isinstance(accessibility, list) or any(
        not isinstance(item, str) for item in accessibility
    ):
        errors.append(
            ValidationIssue(
                "error",
                "design.accessibility",
                "must be a list of strings",
            )
        )
    if not design.get("venue"):
        warnings.append(
            ValidationIssue(
                "warning",
                "design.venue",
                "is missing; use and document a general publication default",
            )
        )
    if not design.get("column_width"):
        warnings.append(
            ValidationIssue(
                "warning",
                "design.column_width",
                "is missing; final-size legibility cannot be assessed precisely",
            )
        )

    output = _mapping(spec.get("output"), "output", errors)
    stem = _nonempty_text(output.get("stem"), "output.stem", errors)
    if stem and Path(stem).suffix:
        errors.append(
            ValidationIssue(
                "error",
                "output.stem",
                "must not include a file extension",
            )
        )
    formats = _string_list(
        output.get("formats"),
        "output.formats",
        errors,
        allow_empty=False,
    )
    unknown_formats = sorted(set(formats) - OUTPUT_FORMATS)
    if unknown_formats:
        errors.append(
            ValidationIssue(
                "error",
                "output.formats",
                f"contains unsupported formats: {unknown_formats}",
            )
        )
    dpi = output.get("dpi")
    if not isinstance(dpi, (int, float)) or isinstance(dpi, bool) or dpi <= 0:
        errors.append(
            ValidationIssue("error", "output.dpi", "must be a positive number")
        )
    elif dpi < 300 and "png" in formats:
        warnings.append(
            ValidationIssue(
                "warning",
                "output.dpi",
                "is below the common 300 DPI publication default",
            )
        )

    _string_list(
        spec.get("assumptions"),
        "assumptions",
        errors,
        allow_empty=True,
    )
    acceptance = _string_list(
        spec.get("acceptance_criteria"),
        "acceptance_criteria",
        errors,
        allow_empty=True,
    )
    if not acceptance:
        warnings.append(
            ValidationIssue(
                "warning",
                "acceptance_criteria",
                "is empty; add image- or code-checkable completion criteria",
            )
        )

    open_questions = spec.get("open_questions")
    if not isinstance(open_questions, list):
        errors.append(
            ValidationIssue("error", "open_questions", "must be a list")
        )
    else:
        for index, question in enumerate(open_questions):
            path = f"open_questions[{index}]"
            if not isinstance(question, Mapping):
                errors.append(
                    ValidationIssue(
                        "error",
                        path,
                        "must be an object with question, reason, and severity",
                    )
                )
                continue
            _nonempty_text(question.get("question"), f"{path}.question", errors)
            _nonempty_text(question.get("reason"), f"{path}.reason", errors)
            severity = _nonempty_text(
                question.get("severity"),
                f"{path}.severity",
                errors,
            )
            if severity and severity not in QUESTION_SEVERITIES:
                errors.append(
                    ValidationIssue(
                        "error",
                        f"{path}.severity",
                        f"must be one of {sorted(QUESTION_SEVERITIES)}",
                    )
                )
            elif severity == "critical":
                errors.append(
                    ValidationIssue(
                        "error",
                        path,
                        "contains an unresolved critical scientific question",
                    )
                )
            elif severity == "preference":
                warnings.append(
                    ValidationIssue(
                        "warning",
                        path,
                        "contains an unresolved preference; a documented default may proceed",
                    )
                )

    return ValidationResult(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _print_human(result: ValidationResult) -> None:
    status = "VALID" if result.valid else "INVALID"
    print(f"Figure Spec: {status}")
    for issue in (*result.errors, *result.warnings):
        print(f"- {issue.level.upper()} {issue.path}: {issue.message}")
    if not result.errors and not result.warnings:
        print("- No validation issues.")


def _command_init(args: argparse.Namespace) -> int:
    output = Path(args.output)
    if output.exists() and not args.force:
        raise FileExistsError(
            f"Refusing to overwrite existing file without --force: {output}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(default_spec(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote Figure Spec template: {output}")
    return 0


def _command_validate(args: argparse.Namespace) -> int:
    result = validate_spec(load_spec(args.spec))
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        _print_human(result)
    return 0 if result.valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or validate a scientific Figure Spec JSON file."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="write a template")
    init_parser.add_argument("--output", required=True, help="template output path")
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing file",
    )
    init_parser.set_defaults(handler=_command_init)

    validate_parser = subparsers.add_parser("validate", help="validate a spec")
    validate_parser.add_argument("spec", help="Figure Spec JSON path")
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable validation",
    )
    validate_parser.set_defaults(handler=_command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Figure Spec error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
