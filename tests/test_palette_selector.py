from scientific_figure_skill import (
    auto_palette,
    suggest_palettes,
    build_llm_palette_selection_prompt,
    resolve_palette,
)


def test_auto_palette():
    s = auto_palette("简洁大气 Nature 科研风格", "grouped_bar", n_colors=4)
    assert s.name in s.candidates
    assert len(s.colors) >= 4


def test_heatmap_prefers_continuous():
    c = suggest_palettes("热力图 连续变量 色盲安全", "heatmap", n_colors=7)
    assert c[0].kind in {"sequential", "diverging"}


def test_llm_prompt():
    c = suggest_palettes("IEEE 风格 多方法对比", "grouped_bar", n_colors=5)
    p = build_llm_palette_selection_prompt("IEEE 风格 多方法对比", "grouped_bar", c)
    assert "required_json_schema" in p


def test_resolve_registry_palette():
    assert len(resolve_palette("nature_modern", n=8)) == 8
