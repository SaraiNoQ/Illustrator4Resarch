from scientific_figure_skill import (
    CHART_STYLE_REGISTRY,
    PALETTE_REGISTRY,
    TABLE_STYLE_REGISTRY,
    auto_figure_design,
    build_llm_table_style_prompt,
    resolve_chart_style,
    resolve_table_style,
    suggest_palettes,
)


def test_design_registries_are_significantly_expanded():
    assert len(CHART_STYLE_REGISTRY) >= 25
    assert len(TABLE_STYLE_REGISTRY) >= 8
    assert len(PALETTE_REGISTRY) >= 30

    for name in [
        "ggplot_minimal",
        "datawrapper_clean",
        "observable_modern",
        "tableau_dashboard",
        "scientific_heatmap",
        "monochrome_print",
    ]:
        assert name in CHART_STYLE_REGISTRY

    assert "academic_three_line" in TABLE_STYLE_REGISTRY
    assert "seaborn_colorblind" in PALETTE_REGISTRY
    assert "twilight_cyclic" in PALETTE_REGISTRY


def test_external_style_cues_resolve_to_expected_presets():
    assert resolve_chart_style("ggplot2 theme_minimal line chart").name == "ggplot_minimal"
    assert resolve_chart_style("Datawrapper newsroom editorial bar").name == "datawrapper_clean"
    assert resolve_chart_style("Tableau dashboard grouped bar").name == "tableau_dashboard"
    assert resolve_chart_style("heatmap correlation matrix", figure_type="heatmap").name == "scientific_heatmap"


def test_handdrawn_and_table_style_prompts_are_preserved():
    handdrawn = auto_figure_design(
        "二次元、可爱、手绘风格 grouped bar",
        figure_type="grouped_bar",
        n_colors=4,
    )
    assert handdrawn.chart_style.name == "cartoon_handdrawn"

    table_design = auto_figure_design("论文 三线表 table", figure_type="table")
    assert table_design.table_style is not None
    assert table_design.table_style.name == "academic_three_line"
    assert "table_style_prompt" in table_design.llm_prompt


def test_table_style_resolver_and_prompt():
    assert resolve_table_style("论文 三线表").name == "academic_three_line"
    prompt = build_llm_table_style_prompt("dashboard tableau table")
    assert "selected_table_style" in prompt
    assert "dashboard_table" in prompt


def test_palette_kinds_include_editorial_and_cyclic_options():
    tableau_names = [
        p.name
        for p in suggest_palettes(
            "Tableau dashboard categorical",
            figure_type="grouped_bar",
            n_colors=8,
            include_generated=False,
        )
    ]
    assert "tableau_10" in tableau_names

    cyclic_names = [
        p.name
        for p in suggest_palettes(
            "phase angle cyclic heatmap",
            figure_type="phase",
            data_role="cyclic",
            include_generated=False,
        )
    ]
    assert "twilight_cyclic" in cyclic_names
