#!/usr/bin/env python3
"""Normalize tabular research inputs and validate their provenance.

The core extractor intentionally uses only the Python standard library. Image,
PDF, and spreadsheet extraction stays with runtime tools; ``register`` records
those results without pretending that an external transcription is verified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


AUDIT_SCHEMA_VERSION = "1.0"
SUPPORTED_FORMATS = {
    "csv",
    "tsv",
    "json",
    "markdown",
    "latex",
    "text",
    "image",
    "pdf",
    "spreadsheet",
    "other",
}
SOURCE_ROLES = {
    "primary_data",
    "context_metadata",
    "style_reference",
    "existing_figure",
}
EXTRACTION_METHODS = {
    "stdlib_parser",
    "vision_transcription",
    "runtime_extractor",
    "direct_transcription",
}
VERIFICATION_STATUSES = {"pending", "verified"}
VERIFICATION_METHODS = {
    "deterministic_parse",
    "user_confirmed",
    "mixed",
}
CONTENT_KINDS = {"table", "chart", "records", "reference"}


class IntakeError(ValueError):
    """Raised when an input cannot be normalized without guessing."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _warning(code: str, message: str, *, blocking: bool = False) -> dict[str, str]:
    return {
        "severity": "blocking" if blocking else "warning",
        "code": code,
        "message": message,
    }


def _cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        raise IntakeError("nested JSON values are not supported in table cells")
    return str(value).strip()


def _rectangularize(
    rows: list[list[Any]],
    warnings: list[dict[str, str]],
) -> list[list[str]]:
    cleaned = [[_cell_text(cell) for cell in row] for row in rows]
    blank_count = sum(not any(row) for row in cleaned)
    cleaned = [row for row in cleaned if any(row)]
    if blank_count:
        warnings.append(
            _warning("blank_rows", f"ignored {blank_count} completely blank row(s)")
        )
    if not cleaned:
        raise IntakeError("input contains no table rows")

    width = max(len(row) for row in cleaned)
    if width == 0:
        raise IntakeError("input contains no table columns")
    widths = {len(row) for row in cleaned}
    if len(widths) != 1:
        warnings.append(
            _warning(
                "irregular_rows",
                f"row widths differ ({sorted(widths)}); padded missing cells",
                blocking=True,
            )
        )
    for row in cleaned:
        row.extend([""] * (width - len(row)))

    header = cleaned[0]
    if any(not cell for cell in header):
        warnings.append(
            _warning(
                "blank_header",
                "one or more header cells are blank",
                blocking=True,
            )
        )
    nonempty_headers = [cell for cell in header if cell]
    if len(nonempty_headers) != len(set(nonempty_headers)):
        warnings.append(
            _warning(
                "duplicate_header",
                "duplicate header names make semantic mapping ambiguous",
                blocking=True,
            )
        )
    return cleaned


def _parse_delimited(
    text: str,
    *,
    default_delimiter: str | None = None,
) -> list[list[str]]:
    sample = text[:8192]
    delimiter = default_delimiter
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except csv.Error:
        if delimiter is None:
            raise IntakeError("plain text must use comma, semicolon, or tab delimiters")
    return list(csv.reader(text.splitlines(), delimiter=delimiter))


def _parse_json(text: str) -> list[list[Any]]:
    payload = json.loads(text)
    if isinstance(payload, list) and payload and all(
        isinstance(item, dict) for item in payload
    ):
        headers: list[str] = []
        for record in payload:
            for key in record:
                key_text = str(key)
                if key_text not in headers:
                    headers.append(key_text)
        return [headers, *[[record.get(key) for key in headers] for record in payload]]

    if isinstance(payload, dict) and payload and all(
        isinstance(value, list) for value in payload.values()
    ):
        lengths = {len(value) for value in payload.values()}
        if len(lengths) != 1:
            raise IntakeError("JSON column arrays must have equal lengths")
        headers = [str(key) for key in payload]
        return [
            headers,
            *[
                [payload[key][index] for key in payload]
                for index in range(next(iter(lengths)))
            ],
        ]

    if isinstance(payload, list) and payload and all(
        isinstance(item, list) for item in payload
    ):
        return payload
    raise IntakeError(
        "JSON must be a non-empty record list, equal-length column object, or matrix"
    )


def _split_markdown_row(line: str) -> list[str]:
    placeholder = "\ue000"
    value = line.strip().replace(r"\|", placeholder)
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.replace(placeholder, "|").strip() for cell in value.split("|")]


def _is_markdown_rule(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _strip_markdown_wrapper(value: str) -> str:
    for wrapper in ("**", "__", "`", "*", "_"):
        if value.startswith(wrapper) and value.endswith(wrapper):
            return value[len(wrapper) : -len(wrapper)].strip()
    return value


def _parse_markdown(text: str) -> list[list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index in range(len(lines) - 1):
        if "|" not in lines[index] or "|" not in lines[index + 1]:
            continue
        header = _split_markdown_row(lines[index])
        if not _is_markdown_rule(_split_markdown_row(lines[index + 1])):
            continue
        rows = [header]
        for line in lines[index + 2 :]:
            if "|" not in line:
                break
            rows.append(_split_markdown_row(line))
        return [[_strip_markdown_wrapper(cell) for cell in row] for row in rows]
    raise IntakeError("no Markdown pipe table with a separator row was found")


def _strip_tex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def _consume_braced(text: str, position: int) -> tuple[str, int]:
    while position < len(text) and text[position].isspace():
        position += 1
    if position >= len(text) or text[position] != "{":
        raise IntakeError("malformed LaTeX table arguments")
    depth = 0
    start = position + 1
    for index in range(position, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index], index + 1
    raise IntakeError("unclosed LaTeX table argument")


def _latex_body(text: str) -> str:
    cleaned = _strip_tex_comments(text)
    match = re.search(r"\\begin\{(tabular|tabularx)\}", cleaned)
    if not match:
        raise IntakeError("no tabular or tabularx environment was found")
    environment = match.group(1)
    position = match.end()
    if environment == "tabularx":
        _, position = _consume_braced(cleaned, position)
    _, position = _consume_braced(cleaned, position)
    end_marker = rf"\end{{{environment}}}"
    end = cleaned.find(end_marker, position)
    if end < 0:
        raise IntakeError(f"missing {end_marker}")
    return cleaned[position:end]


def _unwrap_latex_commands(
    value: str,
    warnings: list[dict[str, str]],
) -> str:
    if r"\multirow" in value:
        warnings.append(
            _warning(
                "complex_latex",
                r"\multirow requires manual table verification",
                blocking=True,
            )
        )

    def replace_multicolumn(match: re.Match[str]) -> str:
        if int(match.group(1)) != 1:
            warnings.append(
                _warning(
                    "complex_latex",
                    r"\multicolumn spanning multiple cells requires verification",
                    blocking=True,
                )
            )
        return match.group(2)

    value = re.sub(
        r"\\multicolumn\{(\d+)\}\{[^{}]*\}\{([^{}]*)\}",
        replace_multicolumn,
        value,
    )
    safe_one_arg = re.compile(
        r"\\(?:textbf|textit|emph|underline|mathbf|mathrm|mathit|num)\{([^{}]*)\}"
    )
    while safe_one_arg.search(value):
        value = safe_one_arg.sub(r"\1", value)

    value = re.sub(
        r"\\SI\{([^{}]*)\}\{\\?(percent|milli(?:second)?|second)\}",
        lambda match: (
            f"{match.group(1)} %"
            if match.group(2) == "percent"
            else f"{match.group(1)} {match.group(2)}"
        ),
        value,
    )
    replacements = {
        r"\pm": "±",
        r"\%": "%",
        r"\_": "_",
        r"\&": "&",
        r"\textbackslash": "\\",
        r"\percent": "%",
        "~": " ",
        "$": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)

    unknown = sorted(set(re.findall(r"\\[A-Za-z@]+", value)))
    if unknown:
        warnings.append(
            _warning(
                "unknown_latex_command",
                f"unsupported LaTeX command(s): {', '.join(unknown)}",
                blocking=True,
            )
        )
    return re.sub(r"\s+", " ", value).strip()


def _parse_latex(
    text: str,
    warnings: list[dict[str, str]],
) -> list[list[str]]:
    body = _latex_body(text)
    body = re.sub(
        r"\\(?:toprule|midrule|bottomrule|hline|addlinespace)\b(?:\[[^\]]*\])?",
        "",
        body,
    )
    body = re.sub(r"\\(?:cmidrule|cline)\s*(?:\([^)]*\))?\{[^{}]*\}", "", body)
    escaped_ampersand = "\ue000"
    body = body.replace(r"\&", escaped_ampersand)
    row_chunks = re.split(r"\\\\(?:\s*\[[^\]]*\])?", body)
    rows: list[list[str]] = []
    for row in row_chunks:
        if not row.strip():
            continue
        cells = re.split(r"(?<!\\)&", row)
        parsed = [
            _unwrap_latex_commands(
                cell.replace(escaped_ampersand, r"\&"),
                warnings,
            )
            for cell in cells
        ]
        if any(parsed):
            rows.append(parsed)
    return rows


def _detect_format(path: Path, explicit: str, text: str) -> str:
    if explicit != "auto":
        return explicit
    suffix = path.suffix.lower()
    suffix_map = {
        ".csv": "csv",
        ".tsv": "tsv",
        ".json": "json",
        ".md": "markdown",
        ".markdown": "markdown",
        ".tex": "latex",
        ".latex": "latex",
        ".txt": "text",
    }
    if suffix in suffix_map:
        return suffix_map[suffix]
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        return "json"
    if r"\begin{tabular" in text:
        return "latex"
    if re.search(r"^\s*\|?.+\|.+\n\s*\|?\s*:?-{3,}", text, re.MULTILINE):
        return "markdown"
    return "text"


def extract_rows(
    path: str | Path,
    *,
    source_format: str = "auto",
) -> tuple[str, list[list[str]], list[dict[str, str]]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8-sig")
    detected = _detect_format(source, source_format, text)
    warnings: list[dict[str, str]] = []
    if detected == "csv":
        rows = _parse_delimited(text, default_delimiter=",")
    elif detected == "tsv":
        rows = _parse_delimited(text, default_delimiter="\t")
    elif detected == "json":
        rows = _parse_json(text)
    elif detected == "markdown":
        rows = _parse_markdown(text)
    elif detected == "latex":
        rows = _parse_latex(text, warnings)
    elif detected == "text":
        rows = _parse_delimited(text)
    else:
        raise IntakeError(f"extract does not support format: {detected}")
    return detected, _rectangularize(rows, warnings), warnings


def _relative(path: Path, report: Path) -> str:
    return os.path.relpath(path.resolve(), report.parent.resolve())


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerows(rows)


def _table_metadata(path: Path) -> tuple[int, int, list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.reader(handle))
    warnings: list[dict[str, str]] = []
    rows = _rectangularize(raw_rows, warnings)
    return max(0, len(rows) - 1), len(rows[0]), warnings


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _source_entry(
    source: Path,
    report: Path,
    *,
    source_format: str,
    roles: list[str],
    extraction_method: str,
    content_kind: str,
) -> dict[str, Any]:
    return {
        "path": _relative(source, report),
        "format": source_format,
        "roles": roles,
        "content_kind": content_kind,
        "extraction_method": extraction_method,
        "sha256": sha256_file(source),
    }


def _normalized_entry(
    normalized: Path,
    report: Path,
    *,
    rows: int,
    columns: int,
) -> dict[str, Any]:
    return {
        "path": _relative(normalized, report),
        "sha256": sha256_file(normalized),
        "rows": rows,
        "columns": columns,
    }


def build_audit(
    *,
    source: Path,
    normalized: Path,
    report: Path,
    source_format: str,
    roles: list[str],
    content_kind: str,
    extraction_method: str,
    verification_status: str,
    verification_method: str,
    rows: int,
    columns: int,
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "sources": [
            _source_entry(
                source,
                report,
                source_format=source_format,
                roles=roles,
                extraction_method=extraction_method,
                content_kind=content_kind,
            )
        ],
        "normalized_sources": [
            _normalized_entry(
                normalized,
                report,
                rows=rows,
                columns=columns,
            )
        ],
        "verification_status": verification_status,
        "verification_method": verification_method,
        "warnings": warnings,
    }


def _resolve(report_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else report_path.parent / path


def validate_audit(
    audit: dict[str, Any],
    report_path: str | Path,
) -> list[dict[str, str]]:
    report = Path(report_path)
    issues: list[dict[str, str]] = []

    def issue(path: str, message: str) -> None:
        issues.append({"path": path, "message": message})

    if audit.get("schema_version") != AUDIT_SCHEMA_VERSION:
        issue("schema_version", f"must be {AUDIT_SCHEMA_VERSION}")

    status = audit.get("verification_status")
    method = audit.get("verification_method")
    if status not in VERIFICATION_STATUSES:
        issue("verification_status", f"must be one of {sorted(VERIFICATION_STATUSES)}")
    elif status == "pending":
        issue("verification_status", "is pending; data must be verified before rendering")
    if method not in VERIFICATION_METHODS:
        issue("verification_method", f"must be one of {sorted(VERIFICATION_METHODS)}")

    sources = audit.get("sources")
    if not isinstance(sources, list) or not sources:
        issue("sources", "must be a non-empty list")
        sources = []
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            issue(prefix, "must be an object")
            continue
        source_format = source.get("format")
        roles = source.get("roles")
        extraction_method = source.get("extraction_method")
        content_kind = source.get("content_kind")
        if source_format not in SUPPORTED_FORMATS:
            issue(f"{prefix}.format", f"must be one of {sorted(SUPPORTED_FORMATS)}")
        if (
            not isinstance(roles, list)
            or not roles
            or any(role not in SOURCE_ROLES for role in roles)
        ):
            issue(f"{prefix}.roles", f"must use values from {sorted(SOURCE_ROLES)}")
            roles = []
        if extraction_method not in EXTRACTION_METHODS:
            issue(
                f"{prefix}.extraction_method",
                f"must be one of {sorted(EXTRACTION_METHODS)}",
            )
        if content_kind not in CONTENT_KINDS:
            issue(
                f"{prefix}.content_kind",
                f"must be one of {sorted(CONTENT_KINDS)}",
            )
        if (
            source_format == "image"
            and content_kind == "chart"
            and "primary_data" in roles
        ):
            issue(
                prefix,
                "a chart screenshot cannot be an exact primary numeric source",
            )
        if (
            extraction_method == "vision_transcription"
            and status == "verified"
            and method not in {"user_confirmed", "mixed"}
        ):
            issue(
                "verification_method",
                "vision transcription requires user confirmation",
            )

        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            issue(f"{prefix}.path", "must be a non-empty string")
            continue
        path = _resolve(report, raw_path)
        if not path.is_file():
            issue(f"{prefix}.path", f"file is missing: {path}")
        elif source.get("sha256") != sha256_file(path):
            issue(f"{prefix}.sha256", "source file hash has changed")

    normalized_sources = audit.get("normalized_sources")
    if not isinstance(normalized_sources, list) or not normalized_sources:
        issue("normalized_sources", "must be a non-empty list")
        normalized_sources = []
    for index, normalized in enumerate(normalized_sources):
        prefix = f"normalized_sources[{index}]"
        if not isinstance(normalized, dict):
            issue(prefix, "must be an object")
            continue
        raw_path = normalized.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            issue(f"{prefix}.path", "must be a non-empty string")
            continue
        path = _resolve(report, raw_path)
        if not path.is_file():
            issue(f"{prefix}.path", f"file is missing: {path}")
            continue
        if normalized.get("sha256") != sha256_file(path):
            issue(f"{prefix}.sha256", "normalized file hash has changed")
        try:
            rows, columns, table_warnings = _table_metadata(path)
        except (OSError, UnicodeError, csv.Error, IntakeError) as exc:
            issue(prefix, str(exc))
            continue
        if normalized.get("rows") != rows:
            issue(f"{prefix}.rows", f"expected {normalized.get('rows')}, found {rows}")
        if normalized.get("columns") != columns:
            issue(
                f"{prefix}.columns",
                f"expected {normalized.get('columns')}, found {columns}",
            )
        if any(item["severity"] == "blocking" for item in table_warnings):
            issue(prefix, "normalized CSV has blocking structural warnings")

    warnings = audit.get("warnings")
    if not isinstance(warnings, list):
        issue("warnings", "must be a list")
    elif status == "verified" and any(
        isinstance(item, dict) and item.get("severity") == "blocking"
        for item in warnings
    ):
        issue("warnings", "blocking warnings cannot be marked verified")
    return issues


def _command_extract(args: argparse.Namespace) -> int:
    source = Path(args.input)
    normalized = Path(args.normalized)
    report = Path(args.report)
    detected, rows, warnings = extract_rows(source, source_format=args.format)
    _write_csv(normalized, rows)
    status = (
        "pending"
        if any(item["severity"] == "blocking" for item in warnings)
        else "verified"
    )
    audit = build_audit(
        source=source,
        normalized=normalized,
        report=report,
        source_format=detected,
        roles=args.role,
        content_kind="records" if detected == "json" else "table",
        extraction_method="stdlib_parser",
        verification_status=status,
        verification_method="deterministic_parse",
        rows=max(0, len(rows) - 1),
        columns=len(rows[0]),
        warnings=warnings,
    )
    _write_report(report, audit)
    print(
        f"Data intake: {status.upper()} "
        f"({len(rows) - 1} rows x {len(rows[0])} columns)"
    )
    print(f"- normalized: {normalized}")
    print(f"- audit: {report}")
    return 0


def _command_register(args: argparse.Namespace) -> int:
    source = Path(args.source)
    normalized = Path(args.normalized)
    report = Path(args.report)
    rows, columns, warnings = _table_metadata(normalized)
    if not args.verified:
        warnings.append(
            _warning(
                "confirmation_required",
                "external extraction has not been confirmed by the user",
                blocking=True,
            )
        )
    if (
        args.format == "image"
        and args.content_kind == "chart"
        and "primary_data" in args.role
    ):
        warnings.append(
            _warning(
                "chart_digitization",
                "a chart screenshot cannot supply exact publication values",
                blocking=True,
            )
        )
    audit = build_audit(
        source=source,
        normalized=normalized,
        report=report,
        source_format=args.format,
        roles=args.role,
        content_kind=args.content_kind,
        extraction_method=args.method,
        verification_status="verified" if args.verified else "pending",
        verification_method=args.verification_method,
        rows=rows,
        columns=columns,
        warnings=warnings,
    )
    _write_report(report, audit)
    print(f"Registered data intake: {audit['verification_status'].upper()}")
    print(f"- audit: {report}")
    return 0


def _command_validate(args: argparse.Namespace) -> int:
    report = Path(args.report)
    audit = json.loads(report.read_text(encoding="utf-8"))
    if not isinstance(audit, dict):
        raise IntakeError("audit root must be a JSON object")
    issues = validate_audit(audit, report)
    if args.json:
        print(
            json.dumps(
                {"valid": not issues, "errors": issues},
                ensure_ascii=False,
                indent=2,
            )
        )
    elif issues:
        print("Data intake: INVALID")
        for item in issues:
            print(f"- ERROR {item['path']}: {item['message']}")
    else:
        print("Data intake: VALID")
        print("- Source hashes, normalized tables, and verification state are valid.")
    return 1 if issues else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize and verify scientific figure data sources."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    extract = commands.add_parser(
        "extract",
        help="extract a deterministic text table",
    )
    extract.add_argument("input")
    extract.add_argument("--normalized", required=True)
    extract.add_argument("--report", required=True)
    extract.add_argument(
        "--format",
        default="auto",
        choices=["auto", "csv", "tsv", "json", "markdown", "latex", "text"],
    )
    extract.add_argument(
        "--role",
        action="append",
        choices=sorted(SOURCE_ROLES),
        default=None,
    )
    extract.set_defaults(handler=_command_extract)

    register = commands.add_parser(
        "register",
        help="register a visual or runtime-extracted table",
    )
    register.add_argument("source")
    register.add_argument("--normalized", required=True)
    register.add_argument("--report", required=True)
    register.add_argument(
        "--format",
        required=True,
        choices=sorted(SUPPORTED_FORMATS - {"csv", "tsv", "json", "markdown", "latex", "text"}),
    )
    register.add_argument(
        "--content-kind",
        required=True,
        choices=sorted(CONTENT_KINDS),
    )
    register.add_argument(
        "--method",
        required=True,
        choices=sorted(EXTRACTION_METHODS - {"stdlib_parser"}),
    )
    register.add_argument(
        "--verification-method",
        default="user_confirmed",
        choices=["user_confirmed", "mixed"],
    )
    register.add_argument(
        "--role",
        action="append",
        choices=sorted(SOURCE_ROLES),
        default=None,
    )
    register.add_argument(
        "--verified",
        action="store_true",
        help="use only after the user has confirmed the transcription",
    )
    register.set_defaults(handler=_command_register)

    validate = commands.add_parser("validate", help="validate an intake audit")
    validate.add_argument("report")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(handler=_command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "role", None) is None:
        args.role = ["primary_data"]
    try:
        return int(args.handler(args))
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, IntakeError) as exc:
        print(f"Data intake error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
