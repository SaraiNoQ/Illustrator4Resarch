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

from data_intake import validate_audit


SCHEMA_VERSION = "1.2"
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1", SCHEMA_VERSION}
MODES = {"guided", "direct", "refine", "multi_panel"}
METRIC_DIRECTIONS = {"higher", "lower", "mixed", "unknown"}
QUESTION_SEVERITIES = {"critical", "preference"}
CHART_SELECTION_STATUSES = {"recommended", "confirmed"}
STYLE_STATUSES = {"pending", "confirmed"}
DATA_VERIFICATION_STATUSES = {"pending", "verified"}
DATA_VERIFICATION_METHODS = {
    "deterministic_parse",
    "user_confirmed",
    "mixed",
}
STYLE_SOURCES = {
    "reference",
    "explicit_prompt",
    "questionnaire",
    "approved_recommendation",
}
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
            "normalized_sources": [],
            "intake_report": "",
            "verification_status": "pending",
            "verification_method": "",
            "structure": "",
            "metrics": [],
            "uncertainty": {"kind": "unknown", "source": None},
            "transformations": [],
        },
        "chart": {
            "type": "",
            "selection_status": "recommended",
            "x": "",
            "y": "",
            "series": "",
            "panels": [],
        },
        "design": {
            "style_status": "pending",
            "style_source": "",
            "reference_images": [],
            "venue": "general_publication",
            "column_width": "double",
            "chart_style": "publication_minimal",
            "palette_request": "colorblind-safe",
            "font_request": "available publication-safe sans-serif",
            "graphic_grammar": "clean academic axes and restrained grid",
            "layout_request": "double-column layout with a non-overlapping legend",
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


def validate_spec(
    spec: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> ValidationResult:
    """Validate scientific blockers and the portable Figure Spec structure."""
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    schema_version = spec.get("schema_version")
    if (
        not isinstance(schema_version, str)
        or schema_version not in SUPPORTED_SCHEMA_VERSIONS
    ):
        errors.append(
            ValidationIssue(
                "error",
                "schema_version",
                f"must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}",
            )
        )
    elif schema_version == "1.0":
        warnings.append(
            ValidationIssue(
                "warning",
                "schema_version",
                "legacy schema 1.0 has no explicit style-confirmation record; "
                "use schema 1.2 for new figures",
            )
        )
        warnings.append(
            ValidationIssue(
                "warning",
                "schema_version",
                "legacy schema 1.0 has no explicit data-verification record; "
                "use schema 1.2 for new figures",
            )
        )
    elif schema_version == "1.1":
        warnings.append(
            ValidationIssue(
                "warning",
                "schema_version",
                "legacy schema 1.1 has no explicit data-verification record; "
                "use schema 1.2 for new figures",
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
    if schema_version == SCHEMA_VERSION:
        normalized_sources = _string_list(
            data.get("normalized_sources"),
            "data.normalized_sources",
            errors,
            allow_empty=False,
        )
        intake_report = _nonempty_text(
            data.get("intake_report"),
            "data.intake_report",
            errors,
        )
        verification_status = _nonempty_text(
            data.get("verification_status"),
            "data.verification_status",
            errors,
        )
        if (
            verification_status
            and verification_status not in DATA_VERIFICATION_STATUSES
        ):
            errors.append(
                ValidationIssue(
                    "error",
                    "data.verification_status",
                    f"must be one of {sorted(DATA_VERIFICATION_STATUSES)}",
                )
            )
        elif verification_status == "pending":
            errors.append(
                ValidationIssue(
                    "error",
                    "data.verification_status",
                    "is pending; verify normalized data before formal rendering",
                )
            )

        verification_method = _nonempty_text(
            data.get("verification_method"),
            "data.verification_method",
            errors,
        )
        if (
            verification_method
            and verification_method not in DATA_VERIFICATION_METHODS
        ):
            errors.append(
                ValidationIssue(
                    "error",
                    "data.verification_method",
                    f"must be one of {sorted(DATA_VERIFICATION_METHODS)}",
                )
            )
        _string_list(
            data.get("transformations"),
            "data.transformations",
            errors,
            allow_empty=True,
        )

        if base_dir is not None:
            spec_dir = Path(base_dir)
            for index, raw_path in enumerate(normalized_sources):
                path = Path(raw_path)
                resolved = path if path.is_absolute() else spec_dir / path
                if not resolved.is_file():
                    errors.append(
                        ValidationIssue(
                            "error",
                            f"data.normalized_sources[{index}]",
                            f"file is missing: {resolved}",
                        )
                    )
            if intake_report:
                report_path = Path(intake_report)
                resolved_report = (
                    report_path
                    if report_path.is_absolute()
                    else spec_dir / report_path
                )
                if not resolved_report.is_file():
                    errors.append(
                        ValidationIssue(
                            "error",
                            "data.intake_report",
                            f"file is missing: {resolved_report}",
                        )
                    )
                else:
                    try:
                        audit = json.loads(
                            resolved_report.read_text(encoding="utf-8")
                        )
                        if not isinstance(audit, dict):
                            raise ValueError("audit root must be a JSON object")
                        for issue in validate_audit(audit, resolved_report):
                            errors.append(
                                ValidationIssue(
                                    "error",
                                    "data.intake_report",
                                    f"{issue['path']}: {issue['message']}",
                                )
                            )
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        errors.append(
                            ValidationIssue(
                                "error",
                                "data.intake_report",
                                str(exc),
                            )
                        )
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
    if schema_version == "1.1" or schema_version == SCHEMA_VERSION:
        selection_status = _nonempty_text(
            chart.get("selection_status"),
            "chart.selection_status",
            errors,
        )
        if (
            selection_status
            and selection_status not in CHART_SELECTION_STATUSES
        ):
            errors.append(
                ValidationIssue(
                    "error",
                    "chart.selection_status",
                    f"must be one of {sorted(CHART_SELECTION_STATUSES)}",
                )
            )
        elif selection_status == "recommended":
            errors.append(
                ValidationIssue(
                    "error",
                    "chart.selection_status",
                    "is only recommended; the user must confirm or delegate "
                    "the chart before formal rendering",
                )
            )
    if chart_type not in {"table", "schematic"}:
        _nonempty_text(chart.get("x"), "chart.x", errors)
        _nonempty_text(chart.get("y"), "chart.y", errors)
    panels = chart.get("panels", [])
    if not isinstance(panels, list):
        errors.append(ValidationIssue("error", "chart.panels", "must be a list"))

    design = _mapping(spec.get("design"), "design", errors)
    if schema_version == "1.1" or schema_version == SCHEMA_VERSION:
        style_status = _nonempty_text(
            design.get("style_status"),
            "design.style_status",
            errors,
        )
        if style_status and style_status not in STYLE_STATUSES:
            errors.append(
                ValidationIssue(
                    "error",
                    "design.style_status",
                    f"must be one of {sorted(STYLE_STATUSES)}",
                )
            )
        elif style_status == "pending":
            errors.append(
                ValidationIssue(
                    "error",
                    "design.style_status",
                    "is pending; resolve or explicitly delegate every style "
                    "dimension before formal rendering",
                )
            )

        style_source = _nonempty_text(
            design.get("style_source"),
            "design.style_source",
            errors,
        )
        if style_source and style_source not in STYLE_SOURCES:
            errors.append(
                ValidationIssue(
                    "error",
                    "design.style_source",
                    f"must be one of {sorted(STYLE_SOURCES)}",
                )
            )

        reference_images = _string_list(
            design.get("reference_images"),
            "design.reference_images",
            errors,
            allow_empty=True,
        )
        if style_source == "reference" and not reference_images:
            errors.append(
                ValidationIssue(
                    "error",
                    "design.reference_images",
                    "must identify at least one designated style reference "
                    "when design.style_source is 'reference'",
                )
            )

        for field in (
            "venue",
            "column_width",
            "chart_style",
            "palette_request",
            "font_request",
            "graphic_grammar",
            "layout_request",
        ):
            _nonempty_text(design.get(field), f"design.{field}", errors)

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
    if schema_version == "1.0" and not design.get("venue"):
        warnings.append(
            ValidationIssue(
                "warning",
                "design.venue",
                "is missing; use and document a general publication default",
            )
        )
    if schema_version == "1.0" and not design.get("column_width"):
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
    result = validate_spec(
        load_spec(args.spec),
        base_dir=Path(args.spec).parent,
    )
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
