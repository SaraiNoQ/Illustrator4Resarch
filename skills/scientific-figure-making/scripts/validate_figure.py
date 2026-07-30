#!/usr/bin/env python3
"""Run deterministic checks on exported scientific-figure files.

This tool deliberately does not claim to replace visual review. Its JSON report
marks visual inspection as required even when every deterministic check passes.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import numpy as np

from figure_spec import load_spec, validate_spec

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PDF_SIGNATURE = b"%PDF-"


@dataclass(frozen=True)
class Check:
    status: str
    name: str
    path: str
    message: str


def _check(status: str, name: str, path: Path, message: str) -> Check:
    return Check(status, name, str(path), message)


def read_png_metadata(path: str | Path) -> dict[str, Any]:
    """Read PNG dimensions and optional pHYs density without Pillow."""
    png_path = Path(path)
    with png_path.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise ValueError("invalid PNG signature")
        width = height = bit_depth = color_type = None
        dpi_x = dpi_y = None
        while True:
            length_raw = handle.read(4)
            if not length_raw:
                break
            if len(length_raw) != 4:
                raise ValueError("truncated PNG chunk length")
            length = struct.unpack(">I", length_raw)[0]
            chunk_type = handle.read(4)
            payload = handle.read(length)
            crc = handle.read(4)
            if len(chunk_type) != 4 or len(payload) != length or len(crc) != 4:
                raise ValueError("truncated PNG chunk")
            if chunk_type == b"IHDR":
                if length != 13:
                    raise ValueError("invalid IHDR length")
                width, height, bit_depth, color_type = struct.unpack(
                    ">IIBB", payload[:10]
                )
            elif chunk_type == b"pHYs" and length == 9:
                pixels_x, pixels_y, unit = struct.unpack(">IIB", payload)
                if unit == 1:
                    dpi_x = pixels_x * 0.0254
                    dpi_y = pixels_y * 0.0254
            elif chunk_type == b"IEND":
                break
    if width is None or height is None:
        raise ValueError("PNG is missing IHDR")
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "dpi_x": dpi_x,
        "dpi_y": dpi_y,
    }


def _as_rgb(image: np.ndarray) -> np.ndarray:
    array = np.asarray(image, dtype=float)
    if array.size == 0:
        raise ValueError("decoded image is empty")
    if array.max(initial=0.0) > 1.0:
        array = array / 255.0
    if array.ndim == 2:
        return np.repeat(array[..., None], 3, axis=2)
    if array.ndim != 3 or array.shape[2] not in {3, 4}:
        raise ValueError(f"unsupported decoded image shape {array.shape}")
    rgb = array[..., :3]
    if array.shape[2] == 4:
        alpha = np.clip(array[..., 3:4], 0.0, 1.0)
        rgb = rgb * alpha + (1.0 - alpha)
    return np.clip(rgb, 0.0, 1.0)


def _raster_statistics(path: Path) -> dict[str, Any]:
    rgb = _as_rgb(mpimg.imread(path))
    luminance = (
        0.2126 * rgb[..., 0]
        + 0.7152 * rgb[..., 1]
        + 0.0722 * rgb[..., 2]
    )
    border = np.concatenate(
        (
            rgb[0, :, :].reshape(-1, 3),
            rgb[-1, :, :].reshape(-1, 3),
            rgb[:, 0, :].reshape(-1, 3),
            rgb[:, -1, :].reshape(-1, 3),
        ),
        axis=0,
    )
    background = np.median(border, axis=0)
    distance = np.max(np.abs(rgb - background), axis=2)
    content = distance > 0.04
    edge_fractions = {
        "top": float(content[0, :].mean()),
        "bottom": float(content[-1, :].mean()),
        "left": float(content[:, 0].mean()),
        "right": float(content[:, -1].mean()),
    }
    return {
        "luminance_std": float(np.std(luminance)),
        "tonal_span_p99_p01": float(
            np.percentile(luminance, 99) - np.percentile(luminance, 1)
        ),
        "content_fraction": float(content.mean()),
        "edge_content_fraction": edge_fractions,
    }


def validate_png(path: Path, expected_dpi: float | None = None) -> list[Check]:
    checks: list[Check] = []
    try:
        metadata = read_png_metadata(path)
    except (OSError, ValueError, struct.error) as exc:
        return [_check("error", "png_structure", path, str(exc))]

    width = int(metadata["width"])
    height = int(metadata["height"])
    checks.append(
        _check("pass", "png_structure", path, f"valid PNG, {width}x{height}px")
    )
    if width < 600 or height < 400:
        checks.append(
            _check(
                "warning",
                "raster_dimensions",
                path,
                "raster is smaller than the general 600x400 inspection minimum",
            )
        )
    else:
        checks.append(
            _check(
                "pass",
                "raster_dimensions",
                path,
                f"dimensions are suitable for review ({width}x{height}px)",
            )
        )

    dpi_x = metadata.get("dpi_x")
    dpi_y = metadata.get("dpi_y")
    if dpi_x is None or dpi_y is None:
        checks.append(
            _check(
                "warning",
                "raster_dpi",
                path,
                "PNG does not encode physical pixel density",
            )
        )
    else:
        actual_dpi = min(float(dpi_x), float(dpi_y))
        target = float(expected_dpi or 300)
        if actual_dpi + 1 < min(target, 300):
            checks.append(
                _check(
                    "warning",
                    "raster_dpi",
                    path,
                    f"encoded DPI is {actual_dpi:.1f}, below target {target:.1f}",
                )
            )
        else:
            checks.append(
                _check(
                    "pass",
                    "raster_dpi",
                    path,
                    f"encoded DPI is {actual_dpi:.1f}",
                )
            )

    try:
        stats = _raster_statistics(path)
    except (OSError, ValueError) as exc:
        checks.append(_check("error", "raster_decode", path, str(exc)))
        return checks

    std = stats["luminance_std"]
    span = stats["tonal_span_p99_p01"]
    content_fraction = stats["content_fraction"]
    if std < 0.01 or content_fraction < 0.001:
        checks.append(
            _check(
                "error",
                "non_blank_content",
                path,
                (
                    "image appears blank or nearly uniform "
                    f"(std={std:.4f}, span={span:.4f}, content={content_fraction:.4f})"
                ),
            )
        )
    else:
        checks.append(
            _check(
                "pass",
                "non_blank_content",
                path,
                (
                    "image contains visible tonal structure "
                    f"(std={std:.4f}, span={span:.4f})"
                ),
            )
        )

    if span < 0.15:
        checks.append(
            _check(
                "warning",
                "tonal_contrast",
                path,
                f"low grayscale tonal span ({span:.3f}); inspect accessibility",
            )
        )
    else:
        checks.append(
            _check(
                "pass",
                "tonal_contrast",
                path,
                f"grayscale tonal span is {span:.3f}",
            )
        )

    touched = [
        edge
        for edge, fraction in stats["edge_content_fraction"].items()
        if fraction > 0.05
    ]
    if len(touched) >= 3:
        checks.append(
            _check(
                "warning",
                "crop_boundary",
                path,
                f"visible content reaches multiple crop edges: {', '.join(touched)}",
            )
        )
    else:
        checks.append(
            _check(
                "pass",
                "crop_boundary",
                path,
                "no broad multi-edge crop contact detected",
            )
        )
    return checks


def validate_pdf(path: Path) -> list[Check]:
    try:
        signature = path.read_bytes()[: len(PDF_SIGNATURE)]
    except OSError as exc:
        return [_check("error", "pdf_structure", path, str(exc))]
    if signature != PDF_SIGNATURE:
        return [_check("error", "pdf_structure", path, "invalid PDF signature")]
    return [_check("pass", "pdf_structure", path, "valid PDF signature")]


def validate_paths(
    paths: Iterable[str | Path],
    *,
    expected_dpi: float | None = None,
) -> list[Check]:
    """Validate output existence, signatures, and PNG raster characteristics."""
    checks: list[Check] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            checks.append(_check("error", "file_exists", path, "file is missing"))
            continue
        if not path.is_file():
            checks.append(_check("error", "file_exists", path, "path is not a file"))
            continue
        size = path.stat().st_size
        if size == 0:
            checks.append(_check("error", "file_nonempty", path, "file is empty"))
            continue
        checks.append(
            _check("pass", "file_nonempty", path, f"file size is {size} bytes")
        )
        suffix = path.suffix.lower()
        if suffix == ".png":
            checks.extend(validate_png(path, expected_dpi))
        elif suffix == ".pdf":
            checks.extend(validate_pdf(path))
        else:
            checks.append(
                _check(
                    "pass",
                    "generic_export",
                    path,
                    f"non-empty {suffix or 'unknown'} export",
                )
            )
    return checks


def expected_paths_from_spec(spec: dict[str, Any]) -> list[Path]:
    output = spec.get("output", {})
    stem = Path(str(output.get("stem", "")))
    return [stem.with_suffix(f".{fmt}") for fmt in output.get("formats", [])]


def build_report(
    checks: list[Check],
    *,
    spec_path: str | Path | None = None,
) -> dict[str, Any]:
    counts = {
        level: sum(check.status == level for check in checks)
        for level in ("pass", "warning", "error")
    }
    return {
        "schema_version": "1.0",
        "passed": counts["error"] == 0,
        "spec_path": str(spec_path) if spec_path else None,
        "summary": counts,
        "checks": [asdict(check) for check in checks],
        "visual_review_required": True,
        "manual_checks": [
            "data and label correctness",
            "text, tick, legend, and annotation collisions",
            "legibility at target publication size",
            "semantic hierarchy and non-misleading scale",
            "uncertainty representation",
            "grayscale and color-independent differentiation",
            "multi-panel alignment and whitespace",
        ],
    }


def _print_report(report: dict[str, Any]) -> None:
    status = "PASS" if report["passed"] else "FAIL"
    summary = report["summary"]
    print(
        f"Figure export QA: {status} "
        f"({summary['pass']} pass, {summary['warning']} warning, "
        f"{summary['error']} error)"
    )
    for check in report["checks"]:
        print(
            f"- {check['status'].upper()} {check['name']} "
            f"[{check['path']}]: {check['message']}"
        )
    print("- VISUAL REVIEW REQUIRED: deterministic checks are not visual approval")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic QA on scientific-figure exports."
    )
    parser.add_argument("paths", nargs="*", help="export files to check")
    parser.add_argument("--spec", help="Figure Spec used to resolve expected outputs")
    parser.add_argument("--report", help="write JSON QA report")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checks: list[Check] = []
    paths = [Path(path) for path in args.paths]
    expected_dpi: float | None = None

    try:
        if args.spec:
            spec = load_spec(args.spec)
            spec_result = validate_spec(spec)
            for issue in spec_result.errors:
                checks.append(
                    Check("error", "figure_spec", str(args.spec), f"{issue.path}: {issue.message}")
                )
            for issue in spec_result.warnings:
                checks.append(
                    Check(
                        "warning",
                        "figure_spec",
                        str(args.spec),
                        f"{issue.path}: {issue.message}",
                    )
                )
            paths.extend(expected_paths_from_spec(spec))
            dpi = spec.get("output", {}).get("dpi")
            if isinstance(dpi, (int, float)) and not isinstance(dpi, bool):
                expected_dpi = float(dpi)
        if not paths:
            raise ValueError("provide at least one export path or --spec")

        unique_paths = list(dict.fromkeys(paths))
        checks.extend(validate_paths(unique_paths, expected_dpi=expected_dpi))
        report = build_report(checks, spec_path=args.spec)
        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            _print_report(report)
        return 0 if report["passed"] else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Figure QA error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
