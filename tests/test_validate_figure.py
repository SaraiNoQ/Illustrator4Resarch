import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "scientific-figure-making"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from render_preview import create_review_sheet
from validate_figure import (
    build_report,
    read_png_metadata,
    validate_paths,
)


def _write_line_figure(path: Path, *, dpi: int = 300) -> None:
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    ax.plot([0, 1, 2], [0.2, 0.8, 0.5], marker="o", color="#0072B2")
    ax.set_xlabel("Round")
    ax.set_ylabel("Accuracy")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def _write_blank_figure(path: Path) -> None:
    fig = plt.figure(figsize=(4.0, 3.0), facecolor="white")
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def _write_wide_margin_figure(path: Path) -> None:
    fig = plt.figure(figsize=(4.0, 3.0), facecolor="white")
    ax = fig.add_axes((0.38, 0.2, 0.52, 0.65))
    ax.plot([0, 1, 2], [0.2, 0.8, 0.5], marker="o", color="#0072B2")
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)


def test_png_metadata_reads_dimensions_and_dpi(tmp_path):
    path = tmp_path / "figure.png"
    _write_line_figure(path, dpi=300)

    metadata = read_png_metadata(path)

    assert metadata["width"] >= 600
    assert metadata["height"] >= 400
    assert metadata["dpi_x"] is not None
    assert abs(metadata["dpi_x"] - 300) < 1


def test_visible_png_passes_deterministic_checks(tmp_path):
    path = tmp_path / "figure.png"
    _write_line_figure(path)

    checks = validate_paths([path], expected_dpi=300)

    assert not [check for check in checks if check.status == "error"]
    assert any(
        check.name == "non_blank_content" and check.status == "pass"
        for check in checks
    )
    assert any(
        check.name == "outer_whitespace" and check.status == "pass"
        for check in checks
    )


def test_blank_png_is_rejected(tmp_path):
    path = tmp_path / "blank.png"
    _write_blank_figure(path)

    checks = validate_paths([path], expected_dpi=300)

    assert any(
        check.name == "non_blank_content" and check.status == "error"
        for check in checks
    )


def test_excess_outer_whitespace_is_reported(tmp_path):
    path = tmp_path / "wide-margin.png"
    _write_wide_margin_figure(path)

    checks = validate_paths([path], expected_dpi=300)

    whitespace = next(check for check in checks if check.name == "outer_whitespace")
    assert whitespace.status == "warning"
    assert "left=" in whitespace.message
    assert "bbox_inches='tight'" in whitespace.message


def test_pdf_signature_is_checked(tmp_path):
    valid = tmp_path / "valid.pdf"
    invalid = tmp_path / "invalid.pdf"
    valid.write_bytes(b"%PDF-1.7\nminimal")
    invalid.write_bytes(b"not a pdf")

    valid_checks = validate_paths([valid])
    invalid_checks = validate_paths([invalid])

    assert not [check for check in valid_checks if check.status == "error"]
    assert any(check.status == "error" for check in invalid_checks)


def test_report_never_claims_visual_completion(tmp_path):
    path = tmp_path / "figure.png"
    _write_line_figure(path)

    report = build_report(validate_paths([path]))

    assert report["passed"] is True
    assert report["visual_review_required"] is True
    assert "legibility at target publication size" in report["manual_checks"]
    json.dumps(report)


def test_review_sheet_contains_original_and_grayscale(tmp_path):
    source = tmp_path / "figure.png"
    output = tmp_path / "figure.review.png"
    _write_line_figure(source)

    result = create_review_sheet(
        [source],
        output,
        include_grayscale=True,
    )

    assert result == output
    assert output.is_file()
    metadata = read_png_metadata(output)
    assert metadata["width"] > metadata["height"]
