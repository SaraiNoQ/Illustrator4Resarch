from scientific_figure_skill import (
    auto_palette,
    suggest_palettes,
    build_llm_palette_selection_prompt,
    resolve_palette,
    palette_quality,
    resolve_chart_style,
    auto_figure_design,
    build_llm_chart_style_prompt,
    CHART_STYLE_REGISTRY,
    apply_publication_style,
    FigureStyle,
    HANDDRAWN_BG,
    HANDDRAWN_SKETCH,
    harmonize_figure_background,
)
import matplotlib as mpl
import matplotlib.pyplot as plt


def test_auto_palette():
    s = auto_palette("简洁大气 Nature 科研风格", "grouped_bar", n_colors=4)
    assert s.name in s.candidates
    assert len(s.colors) >= 4
    assert s.intent is not None


def test_heatmap_prefers_continuous():
    c = suggest_palettes("热力图 连续变量 色盲安全", "heatmap", n_colors=7)
    assert c[0].kind in {"sequential", "diverging"}


def test_unknown_palette_request_falls_back_to_quality():
    s = auto_palette("清透克莱因式克制氛围但没有预设关键词", "grouped_bar", n_colors=5)
    assert s.name
    assert palette_quality(s.colors, "categorical")["score"] > 0.25


def test_llm_prompt():
    c = suggest_palettes("IEEE 风格 多方法对比", "grouped_bar", n_colors=5)
    p = build_llm_palette_selection_prompt("IEEE 风格 多方法对比", "grouped_bar", c)
    assert "heuristic_intent" in p
    assert "required_json_schema" in p


def test_resolve_registry_palette():
    assert len(resolve_palette("nature_modern", n=8)) == 8


def test_chart_style_resolution():
    assert resolve_chart_style("Nature 科研风格 主实验", figure_type="grouped_bar").name == "nature_journal"
    assert resolve_chart_style("seaborn whitegrid statistical plot").name == "seaborn_whitegrid"
    assert resolve_chart_style("卡通手绘风格解释图").name == "cartoon_handdrawn"


def test_auto_figure_design_decouples_palette_and_chart_style():
    d = auto_figure_design("IEEE 风格，色盲安全，多方法柱状图", "grouped_bar", n_colors=5)
    assert d.palette.name
    assert d.chart_style.name == "ieee_transactions"
    assert "Palette=" in d.reason


def test_chart_style_prompt():
    p = build_llm_chart_style_prompt("Nature科研风格", "grouped_bar")
    assert "selected_chart_style" in p
    assert "Chart style" in p
    assert "nature_journal" in p


def test_style_registry_available():
    assert "publication_minimal" in CHART_STYLE_REGISTRY
    assert "cartoon_handdrawn" in CHART_STYLE_REGISTRY


def test_handdrawn_sketch_is_subtle_and_readable():
    preset = resolve_chart_style("二次元手绘风格", figure_type="grouped_bar")
    assert preset.name == "cartoon_handdrawn"
    assert getattr(preset, "sketch_params") == HANDDRAWN_SKETCH
    scale, length, randomness = HANDDRAWN_SKETCH
    assert 0 < scale < 0.5
    assert length >= 120
    assert randomness <= 1.25
    apply_publication_style(FigureStyle(chart_style="cartoon_handdrawn"))
    assert mpl.rcParams["path.sketch"] == HANDDRAWN_SKETCH


def test_non_handdrawn_resets_sketch():
    apply_publication_style(FigureStyle(chart_style="cartoon_handdrawn"))
    assert mpl.rcParams["path.sketch"] is not None
    apply_publication_style(FigureStyle(chart_style="publication_minimal"))
    assert mpl.rcParams["path.sketch"] is None


def test_handdrawn_background_is_harmonized():
    apply_publication_style(FigureStyle(chart_style="cartoon_handdrawn"))
    fig, ax = plt.subplots()
    harmonize_figure_background(fig)
    assert fig.get_facecolor() == mpl.colors.to_rgba(HANDDRAWN_BG)
    assert ax.get_facecolor() == mpl.colors.to_rgba(HANDDRAWN_BG)
    plt.close(fig)
