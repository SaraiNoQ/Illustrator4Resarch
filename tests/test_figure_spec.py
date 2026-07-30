import copy
import sys
from pathlib import Path


SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "scientific-figure-making"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from figure_spec import default_spec, main, validate_spec


def valid_spec():
    spec = copy.deepcopy(default_spec())
    spec["research_goal"] = {
        "question": "Which method is strongest across datasets?",
        "message": "The proposed method performs consistently well.",
        "metric_direction": "higher",
    }
    spec["data"] = {
        "source": "results.csv",
        "structure": "method_by_dataset",
        "metrics": ["Accuracy (%)"],
        "uncertainty": {"kind": "none", "source": None},
    }
    spec["chart"] = {
        "type": "grouped_bar",
        "selection_status": "confirmed",
        "x": "dataset",
        "y": "Accuracy (%)",
        "series": "method",
        "panels": [],
    }
    spec["design"]["style_status"] = "confirmed"
    spec["design"]["style_source"] = "approved_recommendation"
    spec["acceptance_criteria"] = [
        "Every method/dataset value is represented once.",
        "Labels remain readable at double-column width.",
    ]
    return spec


def test_valid_spec_passes_without_warnings():
    result = validate_spec(valid_spec())

    assert result.valid is True
    assert result.errors == ()
    assert result.warnings == ()


def test_missing_scientific_goal_is_an_error():
    spec = valid_spec()
    spec["research_goal"]["message"] = ""

    result = validate_spec(spec)

    assert result.valid is False
    assert any(
        issue.path == "research_goal.message" for issue in result.errors
    )


def test_critical_open_question_blocks_rendering():
    spec = valid_spec()
    spec["open_questions"] = [
        {
            "question": "Do the ± values mean SD or SE?",
            "reason": "It changes the error-bar semantics.",
            "severity": "critical",
        }
    ]

    result = validate_spec(spec)

    assert result.valid is False
    assert any("unresolved critical" in issue.message for issue in result.errors)


def test_preference_question_warns_but_does_not_block():
    spec = valid_spec()
    spec["open_questions"] = [
        {
            "question": "Do you prefer a warm or cool accent?",
            "reason": "This changes presentation only.",
            "severity": "preference",
        }
    ]

    result = validate_spec(spec)

    assert result.valid is True
    assert any("documented default" in issue.message for issue in result.warnings)


def test_pending_style_blocks_formal_rendering():
    spec = valid_spec()
    spec["design"]["style_status"] = "pending"

    result = validate_spec(spec)

    assert result.valid is False
    assert any(
        issue.path == "design.style_status" and "pending" in issue.message
        for issue in result.errors
    )


def test_recommended_chart_blocks_formal_rendering():
    spec = valid_spec()
    spec["chart"]["selection_status"] = "recommended"

    result = validate_spec(spec)

    assert result.valid is False
    assert any(
        issue.path == "chart.selection_status"
        and "confirm or delegate" in issue.message
        for issue in result.errors
    )


def test_reference_style_requires_reference_image():
    spec = valid_spec()
    spec["design"]["style_source"] = "reference"
    spec["design"]["reference_images"] = []

    result = validate_spec(spec)

    assert result.valid is False
    assert any(
        issue.path == "design.reference_images" for issue in result.errors
    )


def test_reference_style_with_image_is_valid():
    spec = valid_spec()
    spec["design"]["style_source"] = "reference"
    spec["design"]["reference_images"] = ["references/target-style.png"]

    result = validate_spec(spec)

    assert result.valid is True
    assert result.errors == ()


def test_confirmed_style_requires_every_recorded_dimension():
    spec = valid_spec()
    spec["design"]["font_request"] = ""

    result = validate_spec(spec)

    assert result.valid is False
    assert any(
        issue.path == "design.font_request" for issue in result.errors
    )


def test_legacy_schema_1_0_remains_valid_with_warning():
    spec = valid_spec()
    spec["schema_version"] = "1.0"
    for key in (
        "style_status",
        "style_source",
        "reference_images",
        "font_request",
        "graphic_grammar",
        "layout_request",
    ):
        spec["design"].pop(key, None)
    spec["chart"].pop("selection_status", None)

    result = validate_spec(spec)

    assert result.valid is True
    assert any(
        issue.path == "schema_version" and "legacy schema 1.0" in issue.message
        for issue in result.warnings
    )


def test_non_string_schema_version_reports_error_instead_of_crashing():
    spec = valid_spec()
    spec["schema_version"] = ["1.1"]

    result = validate_spec(spec)

    assert result.valid is False
    assert any(issue.path == "schema_version" for issue in result.errors)


def test_unknown_uncertainty_and_direction_warn():
    spec = valid_spec()
    spec["research_goal"]["metric_direction"] = "unknown"
    spec["data"]["uncertainty"]["kind"] = "unknown"

    result = validate_spec(spec)

    assert result.valid is True
    warning_paths = {issue.path for issue in result.warnings}
    assert "research_goal.metric_direction" in warning_paths
    assert "data.uncertainty.kind" in warning_paths


def test_output_stem_rejects_extension():
    spec = valid_spec()
    spec["output"]["stem"] = "figures/main.png"

    result = validate_spec(spec)

    assert result.valid is False
    assert any(issue.path == "output.stem" for issue in result.errors)


def test_cli_init_and_validate_round_trip(tmp_path):
    path = tmp_path / "figure.spec.json"

    assert main(["init", "--output", str(path)]) == 0
    assert path.exists()
    assert main(["validate", str(path), "--json"]) == 1
