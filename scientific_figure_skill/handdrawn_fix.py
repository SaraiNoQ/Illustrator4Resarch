"""Runtime patches for readable hand-drawn chart style, backgrounds, and fonts.

The standalone skill keeps most design logic in `skills/.../scripts/figure_design.py`.
This repository-side patch protects generated figures from common failure modes:

1. overly strong Matplotlib sketch jitter that makes bar/axis geometry hard to read;
2. mismatched figure / axes / save backgrounds when a warm paper background is used;
3. serif defaults, especially Times New Roman, leaking into cartoon/anime/hand-drawn
   styles where a publication-safe sans-serif stack is more appropriate.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

import matplotlib as mpl

from .font_selection import (
    PUBLICATION_FONT_REGISTRY,
    build_llm_font_selection_prompt,
    select_font_candidate,
    select_font_family,
    should_auto_replace_font,
    suggest_fonts,
)

HANDDRAWN_BG = "#FBF7EE"
HANDDRAWN_SKETCH = (0.28, 140.0, 1.0)


def _is_handdrawn(preset: Any) -> bool:
    return getattr(preset, "name", "") == "cartoon_handdrawn" or bool(getattr(preset, "use_xkcd", False))


def _set_optional_attr(obj: Any, name: str, value: Any) -> None:
    try:
        object.__setattr__(obj, name, value)
    except Exception:
        pass


def _apply_background_rc(facecolor: str = HANDDRAWN_BG, axes_color: str | None = None) -> None:
    axes_color = axes_color or facecolor
    mpl.rcParams.update({
        "figure.facecolor": facecolor,
        "axes.facecolor": axes_color,
        "savefig.facecolor": facecolor,
        "savefig.edgecolor": facecolor,
    })


def _apply_font_rc(font_family: tuple[str, ...]) -> None:
    mpl.rcParams["font.family"] = list(font_family)


def harmonize_figure_background(fig, facecolor: str | None = None, axes: str | None = None):
    """Force a Matplotlib figure and all axes patches to share one background."""
    figure_color = facecolor or mpl.rcParams.get("figure.facecolor", "white")
    axes_color = axes or mpl.rcParams.get("axes.facecolor", figure_color)
    fig.patch.set_facecolor(figure_color)
    fig.patch.set_edgecolor(figure_color)
    for ax in fig.axes:
        ax.set_facecolor(axes_color)
    return fig


def _make_finalize_wrapper(original_finalize):
    def finalize_figure_readable(fig, *args, facecolor=None, harmonize_background=True, **kwargs):
        if harmonize_background:
            harmonize_figure_background(fig, facecolor=facecolor)
        try:
            return original_finalize(fig, *args, facecolor=facecolor, harmonize_background=harmonize_background, **kwargs)
        except TypeError:
            # Backward compatibility for older finalizers that do not accept
            # facecolor/harmonize_background. The rc background is already set
            # and the figure patch has already been harmonized.
            return original_finalize(fig, *args, **kwargs)
    return finalize_figure_readable


def _resolve_preset(registry: dict[str, Any], preset: Any = None, style: Any = None) -> Any:
    candidate = preset
    if candidate is None and style is not None:
        candidate = getattr(style, "chart_style", None)
    if isinstance(candidate, str):
        return registry.get(candidate, candidate)
    return candidate


def _replace_style_font(style: Any, font_family: tuple[str, ...]) -> Any:
    if style is None:
        return style
    current = getattr(style, "font_family", None)
    if should_auto_replace_font(current):
        try:
            return replace(style, font_family=font_family)
        except Exception:
            return style
    return style


def _font_reason(request: str | None, preset: Any, venue: str | None) -> str:
    candidate = select_font_candidate(request=request, chart_style=preset, venue=venue)
    return f"font={candidate.name} ({', '.join(candidate.family)})"


def _merge_font_prompt(llm_prompt: str | None, font_prompt: str) -> str:
    if not llm_prompt:
        return font_prompt
    try:
        import json
        payload = json.loads(llm_prompt)
        payload["font_prompt"] = font_prompt
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception:
        return llm_prompt + "\n\n" + font_prompt


def patch_design_module(module: Any) -> Any:
    """Patch an imported figure_design module in place."""
    registry = getattr(module, "CHART_STYLE_REGISTRY", {})
    preset = registry.get("cartoon_handdrawn") if isinstance(registry, dict) else None
    if preset is not None:
        _set_optional_attr(preset, "sketch_params", HANDDRAWN_SKETCH)
        _set_optional_attr(preset, "background_color", HANDDRAWN_BG)
        _set_optional_attr(preset, "axes_facecolor", HANDDRAWN_BG)
        _set_optional_attr(preset, "description", "Readable cartoon/hand-drawn style: subtle sketch jitter, rounded strokes, publication-safe sans-serif fonts, and a uniform warm paper background.")
        rc = dict(getattr(preset, "rc_params", {}) or {})
        rc.update({"lines.solid_capstyle": "round", "lines.solid_joinstyle": "round", "legend.fancybox": True})
        _set_optional_attr(preset, "rc_params", rc)

    original_apply_chart_style = getattr(module, "apply_chart_style", None)
    original_apply_publication_style = getattr(module, "apply_publication_style", None)
    original_auto_figure_design = getattr(module, "auto_figure_design", None)
    original_build_llm_chart_style_prompt = getattr(module, "build_llm_chart_style_prompt", None)
    original_finalize = getattr(module, "finalize_figure", None)
    if original_finalize is None:
        original_finalize = getattr(getattr(module, "_base", None), "finalize_figure", None)

    if callable(original_apply_chart_style):
        def apply_chart_style_readable(preset=None, request=None, figure_type=None, venue=None):
            resolved = original_apply_chart_style(preset, request, figure_type, venue)
            font_family = select_font_family(request=request, chart_style=resolved, venue=venue)
            if _is_handdrawn(resolved):
                mpl.rcParams["path.sketch"] = HANDDRAWN_SKETCH
                _apply_background_rc(HANDDRAWN_BG)
                _apply_font_rc(font_family)
            else:
                mpl.rcParams["path.sketch"] = None
                if request or venue:
                    _apply_font_rc(font_family)
                if mpl.rcParams.get("figure.facecolor") == HANDDRAWN_BG:
                    _apply_background_rc("white")
            return resolved
        module.apply_chart_style = apply_chart_style_readable

    if callable(original_apply_publication_style):
        def apply_publication_style_readable(style=None, chart_style=None, request=None, figure_type=None, venue=None):
            style_obj = style
            if style_obj is None and hasattr(module, "FigureStyle"):
                try:
                    style_obj = module.FigureStyle()
                except Exception:
                    style_obj = None
            preset_obj = _resolve_preset(registry if isinstance(registry, dict) else {}, chart_style, style_obj)
            font_family = select_font_family(request=request, chart_style=preset_obj, venue=venue)
            style_obj = _replace_style_font(style_obj, font_family)
            out = original_apply_publication_style(style_obj, chart_style)
            preset_out = getattr(out, "chart_style", None)
            if isinstance(preset_out, str):
                preset_out = registry.get(preset_out)
            if preset_out is None:
                preset_out = preset_obj
            if _is_handdrawn(preset_out):
                mpl.rcParams["path.sketch"] = HANDDRAWN_SKETCH
                _apply_background_rc(HANDDRAWN_BG)
                _apply_font_rc(select_font_family(request=request, chart_style=preset_out, venue=venue))
                if hasattr(out, "background_color"):
                    try:
                        out = replace(out, background_color=HANDDRAWN_BG)
                    except Exception:
                        pass
            else:
                mpl.rcParams["path.sketch"] = None
                _apply_font_rc(getattr(out, "font_family", font_family))
            return out
        module.apply_publication_style = apply_publication_style_readable

    if callable(original_auto_figure_design):
        def auto_figure_design_readable(request: str, figure_type=None, n_colors=None, data_role=None, venue=None):
            design = original_auto_figure_design(request, figure_type, n_colors, data_role, venue)
            chart_style = getattr(design, "chart_style", None)
            font_prompt = build_llm_font_selection_prompt(request, chart_style=chart_style, venue=venue)
            reason = getattr(design, "reason", "")
            reason = f"{reason} {_font_reason(request, chart_style, venue)}."
            try:
                return replace(design, reason=reason, llm_prompt=_merge_font_prompt(getattr(design, "llm_prompt", None), font_prompt))
            except Exception:
                return design
        module.auto_figure_design = auto_figure_design_readable

    if callable(original_build_llm_chart_style_prompt):
        def build_llm_chart_style_prompt_with_fonts(request: str, figure_type=None, venue=None, candidates=None):
            prompt = original_build_llm_chart_style_prompt(request, figure_type, venue, candidates)
            return _merge_font_prompt(prompt, build_llm_font_selection_prompt(request, chart_style=None, venue=venue))
        module.build_llm_chart_style_prompt = build_llm_chart_style_prompt_with_fonts

    if callable(original_finalize):
        module.finalize_figure = _make_finalize_wrapper(original_finalize)

    module.HANDDRAWN_BG = HANDDRAWN_BG
    module.HANDDRAWN_SKETCH = HANDDRAWN_SKETCH
    module.PUBLICATION_FONT_REGISTRY = PUBLICATION_FONT_REGISTRY
    module.select_font_candidate = select_font_candidate
    module.select_font_family = select_font_family
    module.suggest_fonts = suggest_fonts
    module.build_llm_font_selection_prompt = build_llm_font_selection_prompt
    module.harmonize_figure_background = harmonize_figure_background
    return module
