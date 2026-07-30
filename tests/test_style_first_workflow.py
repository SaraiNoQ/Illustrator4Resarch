import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "scientific-figure-making"


def test_skill_orders_style_before_scientific_questions():
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    style_index = text.index("Style questions")
    science_index = text.index("Scientific questions")

    assert style_index < science_index
    assert "Do not create a formal plotting script" in text


def test_requirement_workflow_distinguishes_undecided_from_delegated():
    text = (
        SKILL_ROOT / "references" / "requirement-workflow.md"
    ).read_text(encoding="utf-8")

    assert "I have not decided" in text
    assert "You decide" in text
    assert "style_status=pending" in text


def test_real_log_regression_eval_checks_question_order_and_render_block():
    payload = json.loads(
        (SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
    )
    regression = next(item for item in payload["evals"] if item["id"] == 2)
    expectations = "\n".join(regression["expectations"])

    assert "Style Brief before scientific interpretation" in expectations
    assert "style-question block appears before" in expectations
    assert "error-semantics question appears after" in expectations
    assert "No formal script" in expectations


def test_reference_eval_fixture_exists():
    fixture = SKILL_ROOT / "evals" / "fixtures" / "reference-style.png"

    assert fixture.is_file()
    assert fixture.stat().st_size > 1_000
