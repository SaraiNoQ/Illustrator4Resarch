import matplotlib as mpl
import sys
from pathlib import Path

from scientific_figure_skill import (
    FigureStyle,
    apply_publication_style,
    available_font_names,
    auto_figure_design,
    build_llm_font_selection_prompt,
    select_font_candidate,
    select_font_family,
)

STANDALONE_SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "scientific-figure-making"
    / "scripts"
)
sys.path.insert(0, str(STANDALONE_SCRIPT_DIR))
from figure_fonts import select_font_family as select_standalone_font_family


def test_anime_handdrawn_request_selects_publication_safe_sans_font():
    request = "二次元、可爱、手绘风格 grouped bar"
    design = auto_figure_design(request, figure_type="grouped_bar", n_colors=4)

    candidate = select_font_candidate(request=request, chart_style=design.chart_style)
    family = select_font_family(request=request, chart_style=design.chart_style)

    assert design.chart_style.name == "cartoon_handdrawn"
    assert candidate.category == "sans_serif"
    assert candidate.name == "trebuchet_sans"
    assert family[-1] == "sans-serif"
    assert "Times New Roman" not in family
    assert "serif" not in family


def test_apply_publication_style_replaces_times_for_handdrawn_style():
    style = FigureStyle(
        font_family=("Times New Roman", "Times", "serif"),
        chart_style="cartoon_handdrawn",
    )

    resolved = apply_publication_style(style)

    assert resolved.font_family[-1] == "sans-serif"
    assert resolved.font_family[0] != "Times New Roman"
    assert mpl.rcParams["font.family"][0] != "Times New Roman"
    assert mpl.rcParams["path.sketch"] == (0.28, 140.0, 1.0)


def test_formal_ieee_request_prefers_clean_sans_font():
    candidate = select_font_candidate(request="IEEE Transactions compact grouped bar", chart_style="ieee_transactions")

    assert candidate.category == "sans_serif"
    assert candidate.name in {"arial", "helvetica"}


def test_font_prompt_restricts_llm_to_registry():
    prompt = build_llm_font_selection_prompt(
        "二次元、可爱、手绘风格",
        chart_style="cartoon_handdrawn",
    )

    assert "publication-safe" in prompt
    assert "trebuchet_sans" in prompt
    assert "never Times New Roman" in prompt


def test_selected_family_filters_unavailable_concrete_fonts():
    family = select_font_family(
        request="general publication figure",
        chart_style="publication_minimal",
    )
    available = available_font_names()
    generic = {"serif", "sans-serif", "cursive", "fantasy", "monospace"}

    assert family
    if available:
        assert all(name in available or name in generic for name in family)


def test_explicit_sans_serif_request_cannot_be_misread_as_serif():
    family = select_font_family(
        request="clean sans-serif typography for a general publication",
        chart_style="publication_minimal",
    )

    assert family[-1] == "sans-serif"
    assert "serif" not in family


def test_standalone_explicit_sans_serif_request_uses_sans_stack():
    family = select_standalone_font_family(
        request="clean sans-serif typography for a general publication",
        chart_style="publication_minimal",
    )

    assert family[-1] == "sans-serif"
    assert "serif" not in family
