"""Runtime patches for readable hand-drawn chart style and uniform backgrounds.

The standalone skill keeps most design logic in `skills/.../scripts/figure_design.py`.
This small repository-side patch protects generated figures from two common
failure modes:

1. overly strong Matplotlib sketch jitter that makes bar/axis geometry hard to read;
2. mismatched figure / axes / save backgrounds when a warm paper background is used.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

import matplotlib as mpl

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


def harmonize_figure_background(fig, facecolor: str | None = None, axes: str | None = None):
    """Force a Matplotlib figure and all axes patches to share one background."""
    figure_color = facecolor or mpl.rcParams.get("figure.facecolor", "white")
    axes_color = axes or mpl.rcParams.get("axes.facecolor", figure_color)
    fig.patch.set_facecolor(figure_color)
    fig.patch.set_edgecolor(figure_color)
    for ax in fig.axes:
        ax.set_facecolor(axes_color)
    return fig


def patch_design_module(module: Any) -> Any:
    """Patch an imported figure_design module in place."""
    registry = getattr(module, "CHART_STYLE_REGISTRY", {})
    preset = registry.get("cartoon_handdrawn") if isinstance(registry, dict) else None
    if preset is not None:
        _set_optional_attr(preset, "sketch_params", HANDDRAWN_SKETCH)
        _set_optional_attr(preset, "background_color", HANDDRAWN_BG)
        _set_optional_attr(preset, "axes_facecolor", HANDDRAWN_BG)
        _set_optional_attr(preset, "description", "Readable cartoon/hand-drawn style: subtle sketch jitter, rounded strokes, and a uniform warm paper background.")
        rc = dict(getattr(preset, "rc_params", {}) or {})
        rc.update({"lines.solid_capstyle": "round", "lines.solid_joinstyle": "round", "legend.fancybox": True})
        _set_optional_attr(preset, "rc_params", rc)

    original_apply_chart_style = getattr(module, "apply_chart_style", None)
    original_apply_publication_style = getattr(module, "apply_publication_style", None)
    original_finalize = getattr(module, "finalize_figure", None)

    if callable(original_apply_chart_style):
        def apply_chart_style_readable(preset=None, request=None, figure_type=None, venue=None):
            resolved = original_apply_chart_style(preset, request, figure_type, venue)
            if _is_handdrawn(resolved):
                mpl.rcParams["path.sketch"] = HANDDRAWN_SKETCH
                _apply_background_rc(HANDDRAWN_BG)
            else:
                mpl.rcParams["path.sketch"] = None
                if mpl.rcParams.get("figure.facecolor") == HANDDRAWN_BG:
                    _apply_background_rc("white")
            return resolved
        module.apply_chart_style = apply_chart_style_readable

    if callable(original_apply_publication_style):
        def apply_publication_style_readable(style=None, chart_style=None):
            out = original_apply_publication_style(style, chart_style)
            preset_obj = getattr(out, "chart_style", None)
            if isinstance(preset_obj, str):
                preset_obj = registry.get(preset_obj)
            if _is_handdrawn(preset_obj):
                mpl.rcParams["path.sketch"] = HANDDRAWN_SKETCH
                _apply_background_rc(HANDDRAWN_BG)
                if hasattr(out, "background_color"):
                    try:
                        out = replace(out, background_color=HANDDRAWN_BG)
                    except Exception:
                        pass
            else:
                mpl.rcParams["path.sketch"] = None
            return out
        module.apply_publication_style = apply_publication_style_readable

    if callable(original_finalize):
        def finalize_figure_readable(fig, *args, facecolor=None, harmonize_background=True, **kwargs):
            if harmonize_background:
                harmonize_figure_background(fig, facecolor=facecolor)
            return original_finalize(fig, *args, facecolor=facecolor, harmonize_background=harmonize_background, **kwargs)
        module.finalize_figure = finalize_figure_readable

    module.HANDDRAWN_BG = HANDDRAWN_BG
    module.HANDDRAWN_SKETCH = HANDDRAWN_SKETCH
    module.harmonize_figure_background = harmonize_figure_background
    return module
