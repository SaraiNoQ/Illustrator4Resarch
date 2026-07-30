#!/usr/bin/env python3
"""Heuristic palette, chart-style, and table-style design layer for scientific figures.

This module is intentionally standalone-friendly. When installed globally it imports
base plotting primitives from sibling `figure_toolkit.py`; inside the repository it
falls back to `scientific_figure_skill.core`.

Design premise
--------------
A scientific visualization style is not a single adjective. It is a coordinated
choice across at least four separable layers:

1. palette semantics: categorical / sequential / diverging / cyclic / grayscale;
2. chart grammar: grid, spines, line weights, marker scale, background, legend;
3. table grammar: header emphasis, zebra rows, rule discipline, cell padding;
4. typography: selected separately by `figure_fonts.py` / repository font engine.

The registries below intentionally borrow conservative design ideas from common
visualization ecosystems such as Matplotlib, Seaborn, ggplot2, D3/Observable,
ColorBrewer, Tableau-like dashboards, and Datawrapper-like editorial charts,
while keeping all implementation local and Matplotlib-only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence
import colorsys
import json
import math
import re

import numpy as np
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, to_rgba

try:  # global skill mode
    import figure_toolkit as _base  # type: ignore
except Exception:  # repository package mode
    from scientific_figure_skill import core as _base  # type: ignore

BasePaletteCandidate = _base.PaletteCandidate
BASE_PALETTE_REGISTRY = dict(_base.PALETTE_REGISTRY)
BASE_ROLE_ORDER = getattr(
    _base,
    "ROLE_ORDER",
    (
        "proposed",
        "baseline",
        "secondary",
        "ablation",
        "neutral",
        "highlight",
        "improvement",
        "uncertainty",
    ),
)


@dataclass(frozen=True)
class PaletteIntent:
    kind: str = "categorical"
    mood: str = "balanced"
    temperature: str = "balanced"
    contrast: str = "medium"
    prefer_colorblind: bool = True
    prefer_print: bool = False
    prefer_grayscale: bool = False
    density: str = "normal"
    venue: str | None = None
    confidence: float = 0.35
    unknown_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaletteSelection:
    name: str
    colors: tuple[str, ...]
    color_roles: dict[str, str]
    reason: str
    candidates: tuple[str, ...]
    llm_prompt: str | None = None
    intent: PaletteIntent | None = None


@dataclass(frozen=True)
class GeneratedPaletteCandidate:
    name: str
    colors: tuple[str, ...]
    kind: str
    source: str
    tags: tuple[str, ...]
    description: str
    colorblind_safe: bool = False
    print_safe: bool = False
    priority: float = 1.0
    generated: bool = True

    def as_dict(self) -> dict[str, Any]:
        return candidate_as_dict(self)


# Optional curated additions not present in the base toolkit.
def _make_base_like(
    name: str,
    colors: Sequence[str],
    kind: str,
    source: str,
    tags: Sequence[str],
    desc: str,
    cb: bool = False,
    ps: bool = False,
    priority: float = 1.0,
):
    try:
        return BasePaletteCandidate(
            name,
            tuple(colors),
            kind,
            source,
            tuple(sorted(set(tags))),
            desc,
            cb,
            ps,
            priority,
        )  # old base signature
    except TypeError:
        return GeneratedPaletteCandidate(
            name,
            tuple(colors),
            kind,
            source,
            tuple(sorted(set(tags))),
            desc,
            cb,
            ps,
            priority,
            False,
        )


# Curated palettes. Names are descriptive references to visual grammar; colors are
# local curated hex lists so the skill has no runtime dependency on seaborn, D3,
# Tableau, or ColorBrewer packages.
PALETTE_REGISTRY = {
    **BASE_PALETTE_REGISTRY,
    "warm_muted": _make_base_like(
        "warm_muted",
        ["#8F3F3F", "#C46A3A", "#D6A03D", "#A56F5D", "#6F6F6F", "#D9C7B8"],
        "categorical",
        "curated-publication",
        ["warm", "muted", "soft", "humanities", "review", "暖色", "柔和"],
        "Muted warm palette for narrative or review-style figures.",
        False,
        True,
        1.05,
    ),
    "tableau_10": _make_base_like(
        "tableau_10",
        ["#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#76B7B2", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"],
        "categorical",
        "Tableau-like",
        ["tableau", "dashboard", "categorical", "business", "多方法", "仪表盘"],
        "Dashboard-friendly categorical palette with broad hue separation.",
        False,
        False,
        1.12,
    ),
    "observable_10": _make_base_like(
        "observable_10",
        ["#4269D0", "#EF8026", "#3CA951", "#FF5A5F", "#6CC5B0", "#A463F2", "#97BBF5", "#9C6B4E", "#9498A0", "#FFB000"],
        "categorical",
        "Observable/D3-inspired",
        ["observable", "d3", "modern", "web", "categorical", "现代"],
        "Modern web-visualization categorical palette.",
        False,
        False,
        1.08,
    ),
    "seaborn_deep": _make_base_like(
        "seaborn_deep",
        ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"],
        "categorical",
        "Seaborn-like",
        ["seaborn", "deep", "statistical", "categorical", "notebook"],
        "Balanced statistical plotting palette with moderate saturation.",
        False,
        False,
        1.10,
    ),
    "seaborn_muted": _make_base_like(
        "seaborn_muted",
        ["#4878D0", "#EE854A", "#6ACC64", "#D65F5F", "#956CB4", "#8C613C", "#DC7EC0", "#797979", "#D5BB67", "#82C6E2"],
        "categorical",
        "Seaborn-like",
        ["seaborn", "muted", "soft", "statistical", "categorical", "柔和"],
        "Muted statistical palette for figures where strong colors would dominate.",
        False,
        False,
        1.08,
    ),
    "seaborn_colorblind": _make_base_like(
        "seaborn_colorblind",
        ["#0173B2", "#DE8F05", "#029E73", "#D55E00", "#CC78BC", "#CA9161", "#FBAFE4", "#949494", "#ECE133", "#56B4E9"],
        "categorical",
        "Seaborn-like colorblind",
        ["seaborn", "colorblind", "safe", "categorical", "色盲", "高对比"],
        "Colorblind-oriented categorical palette for statistical plots.",
        True,
        False,
        1.28,
    ),
    "brewer_dark2": _make_base_like(
        "brewer_dark2",
        ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D", "#666666"],
        "categorical",
        "ColorBrewer-like",
        ["colorbrewer", "dark2", "qualitative", "categorical", "高对比"],
        "High-contrast qualitative palette inspired by cartographic palettes.",
        False,
        True,
        1.14,
    ),
    "brewer_paired": _make_base_like(
        "brewer_paired",
        ["#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", "#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A", "#FFFF99", "#B15928"],
        "categorical",
        "ColorBrewer-like",
        ["colorbrewer", "paired", "categorical", "paired", "多类别"],
        "Paired qualitative palette for grouped categories and related methods.",
        False,
        False,
        1.05,
    ),
    "brewer_set3": _make_base_like(
        "brewer_set3",
        ["#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F"],
        "categorical",
        "ColorBrewer-like",
        ["colorbrewer", "set3", "pastel", "soft", "many_categories", "柔和"],
        "Large soft qualitative palette for many low-intensity categories.",
        False,
        False,
        1.00,
    ),
    "tol_vibrant": _make_base_like(
        "tol_vibrant",
        ["#0077BB", "#EE7733", "#009988", "#CC3311", "#33BBEE", "#EE3377", "#BBBBBB"],
        "categorical",
        "Tol-style",
        ["tol", "vibrant", "colorblind", "safe", "categorical", "鲜明"],
        "Vibrant colorblind-safe palette for method comparisons.",
        True,
        True,
        1.30,
    ),
    "tol_muted": _make_base_like(
        "tol_muted",
        ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499", "#DDDDDD"],
        "categorical",
        "Tol-style",
        ["tol", "muted", "colorblind", "safe", "categorical", "柔和"],
        "Muted colorblind-safe palette for dense categorical figures.",
        True,
        True,
        1.27,
    ),
    "datawrapper_neutral": _make_base_like(
        "datawrapper_neutral",
        ["#15607A", "#F28E2B", "#7F8C8D", "#3E9A89", "#B85C38", "#6B6ECF", "#A6A6A6"],
        "categorical",
        "Datawrapper-like editorial",
        ["datawrapper", "editorial", "neutral", "newsroom", "clean", "新闻"],
        "Editorial chart palette with one strong blue and restrained supporting colors.",
        False,
        True,
        1.12,
    ),
    "economist_modern": _make_base_like(
        "economist_modern",
        ["#E3120B", "#006BA2", "#3EBCD2", "#379A8B", "#EBB434", "#B4B4B4", "#758D99"],
        "categorical",
        "Economist-inspired",
        ["economist", "magazine", "editorial", "red", "newsroom", "杂志"],
        "Magazine-like palette with a strong editorial red accent.",
        False,
        True,
        1.08,
    ),
    "financial_times_warm": _make_base_like(
        "financial_times_warm",
        ["#990F3D", "#0D7680", "#C8702A", "#A2A2A2", "#70645C", "#E2A03F", "#58595B"],
        "categorical",
        "Financial-Times-inspired",
        ["ft", "financial_times", "warm", "editorial", "report", "暖色"],
        "Warm editorial palette for reports and business-style charts.",
        False,
        True,
        1.06,
    ),
    "nordic_calm": _make_base_like(
        "nordic_calm",
        ["#5E81AC", "#88C0D0", "#81A1C1", "#A3BE8C", "#B48EAD", "#D08770", "#4C566A"],
        "categorical",
        "Nordic-inspired",
        ["nordic", "calm", "cool", "soft", "modern", "冷色"],
        "Cool calm palette for polished technical figures.",
        False,
        False,
        1.04,
    ),
    "solarized_accent": _make_base_like(
        "solarized_accent",
        ["#268BD2", "#2AA198", "#859900", "#B58900", "#CB4B16", "#D33682", "#6C71C4", "#657B83"],
        "categorical",
        "Solarized-inspired",
        ["solarized", "technical", "terminal", "muted", "retro"],
        "Muted technical palette with terminal/editorial flavor.",
        False,
        False,
        1.02,
    ),
    "kawaii_pastel": _make_base_like(
        "kawaii_pastel",
        ["#7AA2E3", "#F7A8B8", "#8FD6C3", "#F7D774", "#BBA7E8", "#F2B880", "#9FA6B2"],
        "categorical",
        "curated-playful-publication",
        ["kawaii", "cute", "anime", "pastel", "playful", "可爱", "二次元"],
        "Soft pastel palette for cute but readable academic charts.",
        False,
        False,
        0.96,
    ),
    "earth_tone": _make_base_like(
        "earth_tone",
        ["#5B8C5A", "#A57548", "#D9A441", "#8F6F5E", "#5E6C5B", "#C97E60", "#AAB7A2"],
        "categorical",
        "curated-publication",
        ["earth", "natural", "fresh", "nature", "自然", "清新"],
        "Natural earth-tone palette for fresh restrained figures.",
        False,
        True,
        1.08,
    ),
    "ocean_science": _make_base_like(
        "ocean_science",
        ["#0B4F6C", "#01BAEF", "#20BF55", "#F4D35E", "#EE964B", "#5C677D"],
        "categorical",
        "curated-publication",
        ["ocean", "science", "blue", "green", "fresh", "清新", "科技"],
        "Fresh blue-green science palette with warm contrast.",
        False,
        False,
        1.06,
    ),
    "viridis_extended": _make_base_like(
        "viridis_extended",
        ["#440154", "#482878", "#3E4989", "#31688E", "#26828E", "#1F9E89", "#35B779", "#6DCD59", "#B4DE2C", "#FDE725"],
        "sequential",
        "Matplotlib scientific sample",
        ["viridis", "scientific", "sequential", "heatmap", "perceptual", "色盲", "热力图", "连续"],
        "Perceptually ordered scientific sequential palette.",
        True,
        True,
        1.35,
    ),
    "magma_extended": _make_base_like(
        "magma_extended",
        ["#000004", "#1B0C41", "#4F0C6B", "#781C6D", "#A52C60", "#CF4446", "#ED6925", "#FB9A06", "#F7D13D", "#FCFDBF"],
        "sequential",
        "Matplotlib scientific sample",
        ["magma", "scientific", "sequential", "heatmap", "dark_to_light", "热力图"],
        "High-dynamic-range sequential palette for heatmaps.",
        True,
        False,
        1.24,
    ),
    "plasma_extended": _make_base_like(
        "plasma_extended",
        ["#0D0887", "#41049D", "#6A00A8", "#8F0DA4", "#B12A90", "#CC4778", "#E16462", "#F2844B", "#FCA636", "#F0F921"],
        "sequential",
        "Matplotlib scientific sample",
        ["plasma", "scientific", "sequential", "heatmap", "vivid"],
        "Vivid perceptual sequential palette.",
        False,
        False,
        1.15,
    ),
    "inferno_extended": _make_base_like(
        "inferno_extended",
        ["#000004", "#1F0C48", "#550F6D", "#88226A", "#A83655", "#CB4A3B", "#ED6925", "#F98E09", "#F7D13D", "#FCFFA4"],
        "sequential",
        "Matplotlib scientific sample",
        ["inferno", "scientific", "sequential", "heatmap", "high_contrast"],
        "High-contrast sequential palette for dense heatmaps.",
        False,
        False,
        1.15,
    ),
    "blue_green_sequential": _make_base_like(
        "blue_green_sequential",
        ["#F7FCF0", "#E0F3DB", "#CCEBC5", "#A8DDB5", "#7BCCC4", "#4EB3D3", "#2B8CBE", "#0868AC", "#084081"],
        "sequential",
        "ColorBrewer-like",
        ["blue", "green", "sequential", "heatmap", "map", "连续"],
        "Blue-green monotone-luminance palette for ordered data.",
        True,
        True,
        1.18,
    ),
    "orange_red_sequential": _make_base_like(
        "orange_red_sequential",
        ["#FFF7EC", "#FEE8C8", "#FDD49E", "#FDBB84", "#FC8D59", "#EF6548", "#D7301F", "#B30000", "#7F0000"],
        "sequential",
        "ColorBrewer-like",
        ["orange", "red", "sequential", "heatmap", "warm", "连续", "暖色"],
        "Warm sequential palette for magnitude or risk maps.",
        False,
        True,
        1.12,
    ),
    "purple_green_diverging": _make_base_like(
        "purple_green_diverging",
        ["#762A83", "#9970AB", "#C2A5CF", "#E7D4E8", "#F7F7F7", "#D9F0D3", "#A6DBA0", "#5AAE61", "#1B7837"],
        "diverging",
        "ColorBrewer-like",
        ["diverging", "purple", "green", "difference", "delta", "正负", "差异"],
        "Purple-green diverging palette for signed differences.",
        True,
        True,
        1.20,
    ),
    "red_blue_diverging": _make_base_like(
        "red_blue_diverging",
        ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC"],
        "diverging",
        "ColorBrewer-like",
        ["diverging", "red", "blue", "difference", "delta", "correlation", "正负"],
        "Red-blue diverging palette with a light neutral midpoint.",
        False,
        True,
        1.18,
    ),
    "brown_teal_diverging": _make_base_like(
        "brown_teal_diverging",
        ["#8C510A", "#BF812D", "#DFC27D", "#F6E8C3", "#F5F5F5", "#C7EAE5", "#80CDC1", "#35978F", "#01665E"],
        "diverging",
        "ColorBrewer-like",
        ["diverging", "brown", "teal", "difference", "earth", "正负"],
        "Brown-teal diverging palette for environmental or natural data.",
        True,
        True,
        1.12,
    ),
    "coolwarm_soft": _make_base_like(
        "coolwarm_soft",
        ["#3B4CC0", "#688AEF", "#9ABBFF", "#CDD9EC", "#F7F7F7", "#F6C6AD", "#ED8366", "#C73635", "#8E1D2C"],
        "diverging",
        "scientific-diverging",
        ["coolwarm", "diverging", "scientific", "correlation", "heatmap", "正负"],
        "Soft cool-warm diverging palette for signed scientific matrices.",
        False,
        False,
        1.13,
    ),
    "twilight_cyclic": _make_base_like(
        "twilight_cyclic",
        ["#E2D9E2", "#9EBBC9", "#5E83B1", "#3F4A8A", "#2B1B56", "#53305E", "#98546D", "#C58D7C", "#E2D9E2"],
        "cyclic",
        "Matplotlib cyclic sample",
        ["cyclic", "phase", "angle", "periodic", "方向", "周期"],
        "Cyclic palette for phase, angle, or periodic variables.",
        False,
        False,
        1.10,
    ),
}


TEXT_CUES: dict[str, dict[str, Any]] = {
    "nature": {"venue": "nature", "mood": "muted"},
    "science": {"venue": "science", "mood": "formal"},
    "cell": {"venue": "cell", "mood": "muted"},
    "ieee": {"venue": "ieee", "mood": "formal", "temperature": "cool"},
    "acm": {"venue": "acm", "mood": "formal"},
    "neurips": {"venue": "neurips", "mood": "minimal"},
    "icml": {"venue": "icml", "mood": "minimal"},
    "iclr": {"venue": "iclr", "mood": "minimal"},
    "cvpr": {"venue": "cvpr", "mood": "minimal"},
    "tableau": {"mood": "bright", "contrast": "high"},
    "dashboard": {"mood": "bright", "contrast": "high", "density": "dense"},
    "observable": {"mood": "bright"},
    "d3": {"mood": "bright"},
    "datawrapper": {"mood": "formal", "contrast": "medium"},
    "economist": {"mood": "formal", "temperature": "warm"},
    "financial times": {"mood": "muted", "temperature": "warm"},
    "ft": {"mood": "muted", "temperature": "warm"},
    "简洁": {"mood": "formal"},
    "大气": {"mood": "formal"},
    "克制": {"mood": "formal", "temperature": "cool"},
    "柔和": {"mood": "muted", "contrast": "low"},
    "高级": {"mood": "muted"},
    "现代": {"mood": "bright"},
    "清新": {"mood": "muted", "temperature": "cool"},
    "自然": {"mood": "muted", "temperature": "warm"},
    "科技": {"temperature": "cool"},
    "冷色": {"temperature": "cool"},
    "暖色": {"temperature": "warm"},
    "高对比": {"contrast": "high"},
    "色盲": {"prefer_colorblind": True},
    "黑白": {"prefer_grayscale": True, "prefer_print": True},
    "打印": {"prefer_print": True},
    "手绘": {"mood": "playful"},
    "卡通": {"mood": "playful"},
    "漫画": {"mood": "playful"},
    "二次元": {"mood": "playful"},
    "可爱": {"mood": "playful", "contrast": "low"},
    "anime": {"mood": "playful"},
    "kawaii": {"mood": "playful", "contrast": "low"},
    "cartoon": {"mood": "playful"},
    "xkcd": {"mood": "playful"},
    "heatmap": {"kind": "sequential"},
    "热力图": {"kind": "sequential"},
    "连续": {"kind": "sequential"},
    "matrix": {"kind": "sequential"},
    "正负": {"kind": "diverging"},
    "差异": {"kind": "diverging"},
    "difference": {"kind": "diverging"},
    "delta": {"kind": "diverging"},
    "correlation": {"kind": "diverging"},
    "相关": {"kind": "diverging"},
    "phase": {"kind": "cyclic"},
    "angle": {"kind": "cyclic"},
    "cyclic": {"kind": "cyclic"},
    "周期": {"kind": "cyclic"},
    "方向": {"kind": "cyclic"},
    "多方法": {"kind": "categorical", "density": "dense"},
    "主实验": {"kind": "categorical"},
    "消融": {"kind": "categorical", "mood": "formal"},
}

FIGURE_KIND = {
    "grouped_bar": "categorical",
    "bar": "categorical",
    "stacked_bar": "categorical",
    "ablation": "categorical",
    "line": "categorical",
    "trend": "categorical",
    "convergence": "categorical",
    "scatter": "categorical",
    "radar": "categorical",
    "table": "categorical",
    "heatmap": "sequential",
    "matrix": "sequential",
    "confusion_matrix": "sequential",
    "correlation": "diverging",
    "difference_heatmap": "diverging",
    "residual_heatmap": "diverging",
    "phase": "cyclic",
    "angle": "cyclic",
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_+\-/]+|[\u4e00-\u9fff]+", (text or "").lower())


def infer_kind(
    request: str = "",
    figure_type: str | None = None,
    data_role: str | None = None,
) -> str:
    if data_role in {"categorical", "sequential", "diverging", "grayscale", "cyclic"}:
        return data_role
    if figure_type and figure_type.lower() in FIGURE_KIND:
        return FIGURE_KIND[figure_type.lower()]
    lowered = (request or "").lower()
    for key, cue in TEXT_CUES.items():
        if key in lowered and "kind" in cue:
            return str(cue["kind"])
    return "categorical"


def infer_palette_intent(
    request: str = "",
    figure_type: str | None = None,
    data_role: str | None = None,
    n_colors: int | None = None,
    venue: str | None = None,
) -> PaletteIntent:
    lowered = (request or "").lower()
    kind = infer_kind(request, figure_type, data_role)
    mood, temperature, contrast = "balanced", "balanced", "medium"
    prefer_colorblind, prefer_print, prefer_grayscale = True, False, kind == "grayscale"
    density = "dense" if (n_colors or 0) >= 7 else "normal"
    inferred_venue = venue.lower() if venue else None
    hits = 0
    for key, cue in TEXT_CUES.items():
        if key in lowered:
            hits += 1
            kind = str(cue.get("kind", kind))
            mood = str(cue.get("mood", mood))
            temperature = str(cue.get("temperature", temperature))
            contrast = str(cue.get("contrast", contrast))
            prefer_colorblind = bool(cue.get("prefer_colorblind", prefer_colorblind))
            prefer_print = bool(cue.get("prefer_print", prefer_print))
            prefer_grayscale = bool(cue.get("prefer_grayscale", prefer_grayscale))
            density = str(cue.get("density", density))
            inferred_venue = (
                str(cue.get("venue", inferred_venue))
                if cue.get("venue", inferred_venue)
                else inferred_venue
            )
    known = set(TEXT_CUES)
    unknown = tuple(
        t
        for t in _tokens(request)
        if all(k not in t and t not in k for k in known) and len(t) > 1
    )
    if prefer_grayscale:
        kind = "grayscale"
    return PaletteIntent(
        kind,
        mood,
        temperature,
        contrast,
        prefer_colorblind,
        prefer_print,
        prefer_grayscale,
        density,
        inferred_venue,
        min(0.95, 0.35 + 0.12 * hits),
        unknown,
    )


def _rgb(color: str) -> tuple[float, float, float]:
    r, g, b, _ = to_rgba(color)
    return float(r), float(g), float(b)


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02X}{:02X}{:02X}".format(
        *(max(0, min(255, round(c * 255))) for c in rgb)
    )


def _blend(c1: str, c2: str, amount: float) -> str:
    a, b = _rgb(c1), _rgb(c2)
    return _hex(tuple((1 - amount) * x + amount * y for x, y in zip(a, b)))


def _adjust_saturation(color: str, factor: float) -> str:
    r, g, b = _rgb(color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return _hex(colorsys.hls_to_rgb(h, l, max(0, min(1, s * factor))))


def _adjust_lightness(color: str, factor: float) -> str:
    r, g, b = _rgb(color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return _hex(colorsys.hls_to_rgb(h, max(0, min(1, l * factor)), s))


def _luminance(color: str) -> float:
    r, g, b = _rgb(color)

    def ch(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _saturation(color: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(color))[2]


def _hue(color: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(color))[0]


def _pair_distance(c1: str, c2: str) -> float:
    r1, g1, b1 = _rgb(c1)
    r2, g2, b2 = _rgb(c2)
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) + 0.8 * abs(
        _luminance(c1) - _luminance(c2)
    )


def _min_pair_distance(colors: Sequence[str]) -> float:
    return (
        1.0
        if len(colors) < 2
        else min(_pair_distance(a, b) for i, a in enumerate(colors) for b in colors[i + 1 :])
    )


def _hue_spread(colors: Sequence[str]) -> float:
    hues = sorted(_hue(c) for c in colors if _saturation(c) > 0.05)
    if len(hues) < 2:
        return 0.0
    gaps = [hues[i + 1] - hues[i] for i in range(len(hues) - 1)] + [1 + hues[0] - hues[-1]]
    return 1 - max(gaps)


def _is_monotone(values: Sequence[float]) -> bool:
    return (
        len(values) < 3
        or all(a <= b + 1e-9 for a, b in zip(values, values[1:]))
        or all(a + 1e-9 >= b for a, b in zip(values, values[1:]))
    )


def palette_quality(colors: Sequence[str], kind: str = "categorical") -> dict[str, float]:
    colors = tuple(colors)
    lums = [_luminance(c) for c in colors]
    sats = [_saturation(c) for c in colors]
    min_dist = _min_pair_distance(colors)
    lum_range = max(lums) - min(lums) if lums else 0.0
    sat_mean = float(np.mean(sats)) if sats else 0.0
    hue_spread = _hue_spread(colors)
    monotone = 1.0 if _is_monotone(lums) else 0.0
    if kind == "categorical":
        score = (
            0.34 * min(1, min_dist / 0.45)
            + 0.26 * min(1, hue_spread / 0.55)
            + 0.20 * min(1, lum_range / 0.55)
            + 0.20 * (1 - abs(sat_mean - 0.55))
        )
    elif kind == "sequential":
        score = 0.45 * monotone + 0.35 * min(1, lum_range / 0.70) + 0.20 * min(1, min_dist / 0.30)
    elif kind == "diverging":
        mid_lum = _luminance(colors[len(colors) // 2]) if colors else 0.9
        score = (
            0.35 * min(1, lum_range / 0.70)
            + 0.25 * min(1, min_dist / 0.30)
            + 0.25 * (1 - abs(mid_lum - 0.88))
            + 0.15 * min(1, hue_spread / 0.45)
        )
    elif kind == "cyclic":
        endpoints_close = 1 - min(1.0, _pair_distance(colors[0], colors[-1]) / 0.45) if len(colors) >= 2 else 0.0
        score = 0.30 * endpoints_close + 0.30 * min(1, hue_spread / 0.55) + 0.25 * min(1, lum_range / 0.70) + 0.15 * min(1, min_dist / 0.25)
    else:
        score = 0.45 * min(1, lum_range / 0.70) + 0.35 * monotone + 0.20 * min(1, min_dist / 0.25)
    return {
        "score": round(float(max(0, min(1, score))), 4),
        "min_pair_distance": round(float(min_dist), 4),
        "luminance_range": round(float(lum_range), 4),
        "mean_saturation": round(float(sat_mean), 4),
        "hue_spread": round(float(hue_spread), 4),
        "monotone_luminance": float(monotone),
    }


def candidate_as_dict(c: Any) -> dict[str, Any]:
    return {
        "name": c.name,
        "colors": list(c.colors),
        "kind": c.kind,
        "source": c.source,
        "tags": list(c.tags),
        "description": c.description,
        "colorblind_safe": bool(getattr(c, "colorblind_safe", False)),
        "print_safe": bool(getattr(c, "print_safe", False)),
        "generated": bool(getattr(c, "generated", False)),
        "quality": palette_quality(c.colors, c.kind),
    }


def _variant(
    candidate: Any,
    suffix: str,
    colors: Sequence[str],
    tags: Sequence[str],
    desc: str,
    priority_delta: float = -0.02,
) -> GeneratedPaletteCandidate:
    return GeneratedPaletteCandidate(
        f"{candidate.name}_{suffix}",
        tuple(colors),
        candidate.kind,
        f"{candidate.source}+generated",
        tuple(sorted(set(tuple(candidate.tags) + tuple(tags)))),
        desc,
        bool(getattr(candidate, "colorblind_safe", False)),
        bool(getattr(candidate, "print_safe", False)),
        max(0.85, float(getattr(candidate, "priority", 1.0)) + priority_delta),
        True,
    )


def generate_palette_variants(
    candidate: Any,
    intent: PaletteIntent,
    n_colors: int | None = None,
) -> list[GeneratedPaletteCandidate]:
    colors = list(candidate.colors)
    out: list[GeneratedPaletteCandidate] = []
    if candidate.kind == "categorical":
        if intent.mood in {"muted", "formal"} or intent.venue in {"nature", "science", "cell"}:
            out.append(
                _variant(
                    candidate,
                    "muted",
                    [_adjust_saturation(_blend(c, "#FFFFFF", 0.08), 0.72) for c in colors],
                    ["generated", "muted", "formal"],
                    "Generated muted variant for refined publication style.",
                )
            )
        if intent.contrast == "high" or intent.density == "dense":
            out.append(
                _variant(
                    candidate,
                    "contrast",
                    [
                        _adjust_saturation(
                            _adjust_lightness(c, 0.88 if _luminance(c) > 0.55 else 1.05),
                            1.12,
                        )
                        for c in colors
                    ],
                    ["generated", "high_contrast", "dense"],
                    "Generated higher-contrast variant for dense method comparisons.",
                )
            )
        if intent.temperature == "cool":
            out.append(
                _variant(
                    candidate,
                    "cool",
                    [
                        _blend(c, "#1F4E79", 0.18)
                        if i % 2 == 0
                        else _blend(c, "#42949E", 0.12)
                        for i, c in enumerate(colors)
                    ],
                    ["generated", "cool"],
                    "Generated cool-toned variant.",
                )
            )
        if intent.temperature == "warm":
            out.append(
                _variant(
                    candidate,
                    "warm",
                    [
                        _blend(c, "#C46A3A", 0.18)
                        if i % 2 == 0
                        else _blend(c, "#D6A03D", 0.10)
                        for i, c in enumerate(colors)
                    ],
                    ["generated", "warm"],
                    "Generated warm-toned variant.",
                )
            )
        if intent.mood == "playful":
            out.append(
                _variant(
                    candidate,
                    "pastel",
                    [_adjust_saturation(_blend(c, "#FFFFFF", 0.22), 0.70) for c in colors],
                    ["generated", "pastel", "playful"],
                    "Generated softer pastel variant for playful academic figures.",
                    -0.06,
                )
            )
    if intent.prefer_grayscale or candidate.kind == "grayscale":
        vals = np.linspace(0.08, 0.82, max(n_colors or len(colors) or 6, 3))
        out.append(
            _variant(
                candidate,
                "gray_generated",
                [_hex((v, v, v)) for v in vals],
                ["generated", "grayscale", "print"],
                "Generated grayscale fallback with monotone luminance.",
                0.0,
            )
        )
    return out


def _candidate_text_match(candidate: Any, request: str) -> float:
    text = " ".join([candidate.name, candidate.source, candidate.description, *candidate.tags]).lower()
    score = 0.0
    for token in _tokens(request):
        if token in text:
            score += 1.2
        elif token:
            chars = set(token)
            overlap = max(
                (
                    len(chars & set(w)) / len(chars | set(w))
                    for w in re.findall(r"[a-zA-Z0-9_+\-/]+", text)
                ),
                default=0.0,
            )
            if overlap > 0.55:
                score += 0.25 * overlap
    return score


def _score_palette(candidate: Any, intent: PaletteIntent, request: str, n_colors: int | None) -> float:
    q = palette_quality(candidate.colors, candidate.kind)
    score = 5.0 * q["score"] + float(getattr(candidate, "priority", 1.0)) + _candidate_text_match(candidate, request)
    score += (
        3.5
        if candidate.kind == intent.kind
        else -2.5
        if intent.kind in {"sequential", "diverging", "cyclic"} and candidate.kind == "categorical"
        else -1.0
        if intent.kind == "categorical" and candidate.kind in {"sequential", "diverging", "cyclic"}
        else 0.0
    )
    tags = set(candidate.tags)
    score += 1.1 if intent.mood in tags else 0.0
    score += 0.9 if intent.temperature in tags else 0.0
    score += 1.8 if intent.venue and intent.venue in tags else 0.0
    score += 1.2 if intent.prefer_colorblind and getattr(candidate, "colorblind_safe", False) else -0.5 if intent.prefer_colorblind else 0.0
    score += 1.2 if intent.prefer_print and getattr(candidate, "print_safe", False) else -0.2 if intent.prefer_print else 0.0
    score += 3.0 if intent.prefer_grayscale and (candidate.kind == "grayscale" or "grayscale" in tags) else -1.0 if intent.prefer_grayscale else 0.0
    if n_colors and candidate.kind == "categorical":
        score += 0.8 if len(candidate.colors) >= n_colors else -0.75 * (n_colors - len(candidate.colors))
    if intent.density == "dense":
        score += q["min_pair_distance"] + (0.6 if candidate.kind == "categorical" and len(candidate.colors) >= (n_colors or 6) else 0.0)
    if getattr(candidate, "generated", False):
        score += 0.25 if intent.confidence < 0.75 else 0.05
    return score


def suggest_palettes(
    request: str,
    figure_type: str | None = None,
    n_colors: int | None = None,
    data_role: str | None = None,
    top_k: int = 6,
    venue: str | None = None,
    include_generated: bool = True,
) -> list[Any]:
    intent = infer_palette_intent(request, figure_type, data_role, n_colors, venue)
    candidates = list(PALETTE_REGISTRY.values())
    if include_generated:
        candidates += [
            v
            for c in list(PALETTE_REGISTRY.values())
            for v in generate_palette_variants(c, intent, n_colors)
        ]
    return sorted(candidates, key=lambda c: _score_palette(c, intent, request, n_colors), reverse=True)[:top_k]


def _roles(candidate: Any) -> dict[str, str]:
    colors = list(candidate.colors)
    if candidate.kind in {"sequential", "diverging", "grayscale", "cyclic"}:
        return {
            "low": colors[0],
            "mid": colors[len(colors) // 2],
            "high": colors[-1],
            "neutral": "#F7F7F7",
        }
    return {
        r: colors[i % len(colors)]
        for i, r in enumerate(
            ["proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "uncertainty"]
        )
    }


def build_llm_palette_selection_prompt(
    request: str,
    figure_type: str | None,
    candidates: Sequence[Any],
    n_colors: int | None = None,
    extra_context: str | None = None,
    venue: str | None = None,
) -> str:
    payload = {
        "user_style_request": request,
        "figure_type": figure_type,
        "n_colors": n_colors,
        "extra_context": extra_context or "",
        "heuristic_intent": infer_palette_intent(
            request,
            figure_type,
            n_colors=n_colors,
            venue=venue,
        ).__dict__,
        "rules": [
            "Choose by scientific readability first, aesthetics second.",
            "For categorical comparison, prefer separation, colorblind safety, and enough colors.",
            "For heatmaps, prefer monotone-luminance sequential palettes unless data is centered around zero.",
            "For signed differences/residuals/correlation deltas, prefer diverging palettes.",
            "For phase/angle/periodic variables, prefer cyclic palettes.",
            "Generated variants are allowed when they better match the requested mood.",
            "Use highlight once only.",
        ],
        "candidates": [candidate_as_dict(c) for c in candidates],
        "required_json_schema": {
            "selected_palette": "candidate name",
            "reason": "brief reason",
            "color_roles": {
                "proposed": "#hex",
                "baseline": "#hex",
                "secondary": "#hex",
                "ablation": "#hex",
                "neutral": "#hex",
                "highlight": "#hex",
            },
        },
    }
    return "Choose one publication-ready palette and return strict JSON only.\n\n" + json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )


def auto_palette(
    request: str,
    figure_type: str | None = None,
    n_colors: int | None = None,
    data_role: str | None = None,
    top_k: int = 6,
    venue: str | None = None,
) -> PaletteSelection:
    intent = infer_palette_intent(request, figure_type, data_role, n_colors, venue)
    cands = suggest_palettes(request, figure_type, n_colors, data_role, top_k, venue)
    sel = cands[0]
    reason = (
        f"Selected {sel.name} by request-profile and palette-quality scoring "
        f"(kind={intent.kind}, mood={intent.mood}, temperature={intent.temperature}, "
        f"contrast={intent.contrast}, generated={bool(getattr(sel, 'generated', False))})."
    )
    return PaletteSelection(
        sel.name,
        tuple(sel.colors),
        _roles(sel),
        reason,
        tuple(c.name for c in cands),
        build_llm_palette_selection_prompt(request, figure_type, cands, n_colors, venue=venue),
        intent,
    )


def apply_llm_palette_decision(
    decision: str | Mapping[str, Any],
    candidates: Sequence[Any],
) -> PaletteSelection:
    obj = json.loads(decision) if isinstance(decision, str) else dict(decision)
    names = {c.name: c for c in candidates}
    name = str(obj.get("selected_palette", "")).strip()
    if name not in names:
        raise ValueError(f"Unknown palette {name!r}; available={sorted(names)}")
    c = names[name]
    roles = obj.get("color_roles") or _roles(c)
    if not isinstance(roles, Mapping):
        raise ValueError("color_roles must be an object")
    return PaletteSelection(
        name,
        tuple(c.colors),
        {str(k): str(v) for k, v in roles.items()},
        str(obj.get("reason", "LLM selected palette.")),
        tuple(names),
    )


@dataclass(frozen=True)
class ChartStylePreset:
    name: str
    description: str
    tags: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    font_size: int = 16
    axes_linewidth: float = 2.0
    line_width: float = 2.4
    marker_size: float = 5.5
    bar_edgecolor: str = "black"
    bar_linewidth: float = 1.1
    grid: str = "none"
    spine_mode: str = "open"
    legend_frame: bool = False
    use_tex: bool = False
    use_xkcd: bool = False
    dpi: int = 300
    rc_params: Mapping[str, Any] | None = None
    priority: float = 1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "aliases": list(self.aliases),
            "font_size": self.font_size,
            "axes_linewidth": self.axes_linewidth,
            "line_width": self.line_width,
            "marker_size": self.marker_size,
            "bar_edgecolor": self.bar_edgecolor,
            "bar_linewidth": self.bar_linewidth,
            "grid": self.grid,
            "spine_mode": self.spine_mode,
            "legend_frame": self.legend_frame,
            "use_xkcd": self.use_xkcd,
            "dpi": self.dpi,
        }


def _s(name, desc, tags, aliases=(), **kwargs):
    return ChartStylePreset(name, desc, tuple(sorted(set(tags))), tuple(aliases), **kwargs)


CHART_STYLE_REGISTRY: dict[str, ChartStylePreset] = {
    "publication_minimal": _s("publication_minimal", "General minimal academic Matplotlib style: open axes, no decorative grid, high readability.", ["paper", "minimal", "clean", "default", "academic", "简洁", "论文"], ["academic", "matplotlib_academic"], font_size=16, axes_linewidth=2.0, grid="none", priority=1.25),
    "nature_journal": _s("nature_journal", "Nature-like compact high-impact journal panel: restrained axes, small typography, little grid.", ["nature", "journal", "high_impact", "compact", "muted", "科研"], ["nature", "nature_style"], font_size=14, axes_linewidth=1.6, line_width=2.2, marker_size=5.0, grid="none", priority=1.32),
    "ieee_transactions": _s("ieee_transactions", "IEEE/engineering style: compact, conservative, print-safe, restrained grid.", ["ieee", "transactions", "engineering", "compact", "print", "严肃"], ["ieee", "trans"], font_size=13, axes_linewidth=1.5, line_width=2.0, marker_size=4.5, grid="y", priority=1.28),
    "acm_conference": _s("acm_conference", "ACM/CS conference style: compact and readable at one-column width.", ["acm", "conference", "computer_science", "compact"], ["sig", "conference"], font_size=13, axes_linewidth=1.5, line_width=2.0, marker_size=4.5, grid="y", priority=1.18),
    "neurips_ml": _s("neurips_ml", "ML conference style: clean white background, light y-grid, thicker curves.", ["neurips", "icml", "iclr", "ml", "conference", "modern"], ["icml", "iclr", "ml"], font_size=15, axes_linewidth=1.8, line_width=2.6, marker_size=5.5, grid="y", priority=1.22),
    "science_compact": _s("science_compact", "Science/Cell-like compact panel with thin axes, restrained labels, and no decorative grid.", ["science", "cell", "journal", "compact", "high_impact"], ["science", "cell"], font_size=13, axes_linewidth=1.35, line_width=2.0, marker_size=4.5, grid="none", bar_linewidth=0.9, priority=1.25),
    "seaborn_whitegrid": _s("seaborn_whitegrid", "Seaborn-like whitegrid visual grammar implemented with Matplotlib rcParams only.", ["seaborn", "whitegrid", "grid", "statistical", "modern"], ["whitegrid", "sns_whitegrid"], font_size=15, axes_linewidth=1.4, line_width=2.3, grid="xy", rc_params={"axes.facecolor": "white", "grid.color": "#E6E6E6", "grid.linewidth": 0.8}, priority=1.05),
    "seaborn_darkgrid": _s("seaborn_darkgrid", "Seaborn-like darkgrid: pale gray axes background with white lookup-grid.", ["seaborn", "darkgrid", "grid", "statistical"], ["darkgrid", "sns_darkgrid"], font_size=15, axes_linewidth=1.2, line_width=2.3, grid="xy", rc_params={"axes.facecolor": "#EAEAF2", "grid.color": "white", "grid.linewidth": 1.0}, priority=1.02),
    "seaborn_ticks": _s("seaborn_ticks", "Seaborn-like ticks style: clean spines, no heavy grid, statistical plotting feel.", ["seaborn", "ticks", "statistical", "clean"], ["ticks", "sns_ticks"], font_size=15, axes_linewidth=1.5, line_width=2.2, grid="none", priority=1.04),
    "ggplot_gray": _s("ggplot_gray", "ggplot2-like gray panel with white gridlines; useful for quick statistical comparisons.", ["ggplot", "gray", "grid", "statistical", "r"], ["ggplot", "ggplot2", "theme_gray"], font_size=15, axes_linewidth=0.9, line_width=2.1, grid="xy", spine_mode="boxed", rc_params={"axes.facecolor": "#EBEBEB", "grid.color": "white", "grid.linewidth": 1.0, "axes.edgecolor": "#B0B0B0"}, priority=0.96),
    "ggplot_bw": _s("ggplot_bw", "ggplot2 theme_bw-like dark-on-light style with boxed panel and clean grid.", ["ggplot", "bw", "blackwhite", "print", "statistical"], ["theme_bw", "bw"], font_size=15, axes_linewidth=1.0, line_width=2.1, grid="xy", spine_mode="boxed", rc_params={"grid.color": "#D9D9D9", "grid.linewidth": 0.75}, priority=1.02),
    "ggplot_minimal": _s("ggplot_minimal", "ggplot2 theme_minimal-like style: no panel fill, light grid, minimal non-data ink.", ["ggplot", "minimal", "clean", "statistical", "简洁"], ["theme_minimal", "ggminimal"], font_size=15, axes_linewidth=1.1, line_width=2.2, grid="xy", rc_params={"grid.color": "#E5E5E5", "grid.linewidth": 0.7, "axes.edgecolor": "#333333"}, priority=1.10),
    "ggplot_classic": _s("ggplot_classic", "ggplot2 theme_classic-like style: axis lines only, no grid, traditional statistical figure.", ["ggplot", "classic", "axis", "traditional"], ["theme_classic"], font_size=15, axes_linewidth=1.4, line_width=2.1, grid="none", priority=1.03),
    "boxed_classic": _s("boxed_classic", "Classic boxed Matplotlib academic style for conservative reports.", ["classic", "matplotlib", "boxed", "report", "传统"], ["matplotlib_default", "classic"], font_size=15, axes_linewidth=1.4, line_width=2.0, grid="none", spine_mode="boxed", legend_frame=True, priority=0.98),
    "datawrapper_clean": _s("datawrapper_clean", "Datawrapper-like editorial chart: open frame, subtle y-grid, generous label spacing.", ["datawrapper", "editorial", "newsroom", "clean", "web"], ["newsroom", "editorial_clean"], font_size=15, axes_linewidth=1.2, line_width=2.2, marker_size=5.0, grid="y", bar_edgecolor="none", bar_linewidth=0.0, rc_params={"grid.color": "#E6E6E6", "grid.linewidth": 0.75}, priority=1.08),
    "observable_modern": _s("observable_modern", "Observable/D3-like modern web chart: light grid, clean spines, compact legend.", ["observable", "d3", "web", "modern", "interactive"], ["observable", "d3"], font_size=15, axes_linewidth=1.1, line_width=2.35, marker_size=5.2, grid="y", bar_edgecolor="white", bar_linewidth=0.8, rc_params={"grid.color": "#ECEFF4", "grid.linewidth": 0.8}, priority=1.06),
    "tableau_dashboard": _s("tableau_dashboard", "Tableau-like dashboard style: readable at screen size, stronger grid discipline, neutral frame.", ["tableau", "dashboard", "business", "screen", "仪表盘"], ["tableau"], font_size=15, axes_linewidth=1.2, line_width=2.4, marker_size=5.3, grid="y", spine_mode="boxed", legend_frame=True, rc_params={"grid.color": "#E0E0E0", "axes.edgecolor": "#C8C8C8"}, priority=1.04),
    "economist_magazine": _s("economist_magazine", "Editorial magazine style with strong red accent compatibility and minimal frame.", ["economist", "magazine", "editorial", "newsroom", "red"], ["economist"], font_size=15, axes_linewidth=1.35, line_width=2.4, grid="y", bar_edgecolor="none", bar_linewidth=0.0, rc_params={"grid.color": "#D8D8D8", "axes.titleweight": "bold"}, priority=0.96),
    "financial_times_report": _s("financial_times_report", "Warm editorial report style with pale paper background and subdued grid.", ["financial_times", "ft", "report", "editorial", "warm"], ["ft", "financial_times"], font_size=15, axes_linewidth=1.25, line_width=2.25, grid="y", rc_params={"figure.facecolor": "#FFF1E5", "axes.facecolor": "#FFF1E5", "savefig.facecolor": "#FFF1E5", "grid.color": "#D8C9B8"}, priority=0.94),
    "thesis_clean": _s("thesis_clean", "Thesis/report style with larger fonts and clear axes.", ["thesis", "report", "slides", "clean", "毕业论文"], ["thesis", "report"], font_size=18, axes_linewidth=2.0, line_width=2.6, marker_size=6.0, grid="y", priority=1.10),
    "presentation_large": _s("presentation_large", "Large-font slide style with bolder lines.", ["slide", "presentation", "large", "talk", "答辩"], ["ppt", "slides"], font_size=22, axes_linewidth=2.6, line_width=3.0, marker_size=7.0, grid="y", priority=1.02),
    "poster_infographic": _s("poster_infographic", "Poster/infographic style: large typography, strong lines, simplified background.", ["poster", "infographic", "large", "presentation", "海报"], ["poster"], font_size=24, axes_linewidth=2.8, line_width=3.2, marker_size=7.5, grid="y", legend_frame=False, priority=0.88),
    "annotation_focus": _s("annotation_focus", "Annotation-first explanatory style with light grid and nonintrusive axes.", ["annotation", "explain", "explainer", "teaching", "标注", "解释"], ["explainer"], font_size=17, axes_linewidth=1.4, line_width=2.6, marker_size=6.0, grid="y", rc_params={"grid.color": "#EFEFEF", "axes.titleweight": "bold"}, priority=0.98),
    "scientific_heatmap": _s("scientific_heatmap", "Heatmap-first scientific style: equal attention to colorbar, square cells, minimal frame.", ["heatmap", "matrix", "scientific", "热力图", "矩阵"], ["heatmap_style", "matrix_style"], font_size=14, axes_linewidth=1.0, line_width=1.8, grid="none", bar_edgecolor="none", bar_linewidth=0.0, rc_params={"image.interpolation": "nearest"}, priority=1.15),
    "monochrome_print": _s("monochrome_print", "Black-and-white print style using thicker lines and hatch-friendly bars.", ["monochrome", "grayscale", "print", "blackwhite", "黑白", "打印"], ["print_bw", "blackwhite"], font_size=14, axes_linewidth=1.6, line_width=2.3, marker_size=5.2, grid="y", bar_edgecolor="black", bar_linewidth=1.2, priority=1.20),
    "dense_appendix": _s("dense_appendix", "Dense appendix/supplement style: smaller type, light grid, compact marks.", ["appendix", "supplement", "dense", "compact", "附录"], ["supplement", "appendix"], font_size=11, axes_linewidth=1.0, line_width=1.6, marker_size=3.8, grid="y", bar_linewidth=0.6, priority=0.98),
    "soft_pastel_journal": _s("soft_pastel_journal", "Soft pastel academic style for friendly explanatory results without sketch jitter.", ["pastel", "soft", "cute", "friendly", "可爱", "柔和"], ["pastel", "soft"], font_size=16, axes_linewidth=1.5, line_width=2.4, marker_size=5.8, grid="y", bar_edgecolor="white", bar_linewidth=0.9, rc_params={"grid.color": "#EFEFEF"}, priority=0.95),
    "cartoon_handdrawn": _s("cartoon_handdrawn", "Cartoon/hand-drawn Matplotlib style using sketch paths; use for explanatory slides, not formal main-paper figures.", ["cartoon", "handdrawn", "xkcd", "playful", "手绘", "卡通", "二次元"], ["xkcd", "handdrawn", "cartoon", "anime", "manga"], font_size=17, axes_linewidth=2.0, line_width=2.8, marker_size=6.5, grid="none", use_xkcd=True, rc_params={"path.sketch": (1, 100, 2), "lines.solid_capstyle": "round"}, priority=0.86),
    "dark_presentation": _s("dark_presentation", "Dark-background presentation style; unsuitable for most paper submissions.", ["dark", "black", "presentation", "poster", "深色"], ["dark"], font_size=20, axes_linewidth=2.0, line_width=2.8, grid="y", rc_params={"figure.facecolor": "#111111", "axes.facecolor": "#111111", "axes.edgecolor": "#E6E6E6", "axes.labelcolor": "#F2F2F2", "xtick.color": "#F2F2F2", "ytick.color": "#F2F2F2", "text.color": "#F2F2F2", "grid.color": "#444444", "savefig.facecolor": "#111111"}, priority=0.70),
    "cyber_dark": _s("cyber_dark", "Cyber/tech dark style for demo slides: dark canvas, bright data marks, light grid.", ["cyber", "tech", "dark", "demo", "科技", "深色"], ["cyberpunk", "tech_dark"], font_size=18, axes_linewidth=1.8, line_width=2.8, marker_size=6.0, grid="y", rc_params={"figure.facecolor": "#07111F", "axes.facecolor": "#07111F", "savefig.facecolor": "#07111F", "axes.edgecolor": "#9FB3C8", "axes.labelcolor": "#E6F1FF", "xtick.color": "#D5E4F2", "ytick.color": "#D5E4F2", "text.color": "#E6F1FF", "grid.color": "#203040"}, priority=0.66),
}


@dataclass(frozen=True)
class TableStylePreset:
    name: str
    description: str
    tags: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    header_facecolor: str = "#F2F2F2"
    header_text_color: str = "#111111"
    body_facecolor: str = "white"
    alternate_row_facecolor: str | None = "#F7F7F7"
    edgecolor: str = "#D9D9D9"
    linewidth: float = 0.6
    font_size: int = 11
    cell_padding: float = 0.08
    header_weight: str = "bold"
    zebra: bool = True
    minimal_edges: bool = False
    priority: float = 1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "aliases": list(self.aliases),
            "header_facecolor": self.header_facecolor,
            "body_facecolor": self.body_facecolor,
            "alternate_row_facecolor": self.alternate_row_facecolor,
            "edgecolor": self.edgecolor,
            "linewidth": self.linewidth,
            "font_size": self.font_size,
            "zebra": self.zebra,
            "minimal_edges": self.minimal_edges,
        }


def _t(name, desc, tags, aliases=(), **kwargs):
    return TableStylePreset(name, desc, tuple(sorted(set(tags))), tuple(aliases), **kwargs)


TABLE_STYLE_REGISTRY: dict[str, TableStylePreset] = {
    "academic_three_line": _t("academic_three_line", "Paper-style three-line table: no vertical clutter, strong header, minimal horizontal rules.", ["academic", "paper", "three_line", "booktabs", "三线表", "论文"], ["booktabs", "three_line", "三线表"], header_facecolor="white", alternate_row_facecolor=None, edgecolor="#222222", linewidth=0.9, font_size=10, zebra=False, minimal_edges=True, priority=1.30),
    "journal_compact_table": _t("journal_compact_table", "Compact journal table for dense results, small type, light rules.", ["journal", "compact", "dense", "appendix", "期刊"], ["compact_table"], header_facecolor="#F6F6F6", alternate_row_facecolor=None, edgecolor="#BFBFBF", linewidth=0.5, font_size=9, zebra=False, minimal_edges=True, priority=1.15),
    "dataframe_zebra": _t("dataframe_zebra", "Readable DataFrame-like table with zebra rows and light grid.", ["dataframe", "zebra", "report", "readable", "表格"], ["zebra", "pandas"], header_facecolor="#EAEFF7", alternate_row_facecolor="#F8FAFC", edgecolor="#D9E2EC", linewidth=0.55, font_size=11, zebra=True, priority=1.05),
    "dashboard_table": _t("dashboard_table", "Dashboard table with stronger header fill and row separation.", ["dashboard", "tableau", "screen", "business", "仪表盘"], ["tableau_table"], header_facecolor="#E8EEF5", alternate_row_facecolor="#F7F9FC", edgecolor="#CED7E0", linewidth=0.7, font_size=11, zebra=True, priority=1.00),
    "editorial_table": _t("editorial_table", "Editorial/newsroom table with subtle warm header and sparse rules.", ["editorial", "newsroom", "datawrapper", "magazine", "新闻"], ["news_table"], header_facecolor="#F4EFE6", alternate_row_facecolor="#FBF8F2", edgecolor="#D9CEC0", linewidth=0.6, font_size=11, zebra=True, priority=0.98),
    "minimal_table": _t("minimal_table", "Minimal table with white background and very light horizontal rules.", ["minimal", "clean", "white", "简洁"], ["clean_table"], header_facecolor="white", alternate_row_facecolor=None, edgecolor="#E5E5E5", linewidth=0.45, font_size=11, zebra=False, minimal_edges=True, priority=1.10),
    "dark_table": _t("dark_table", "Dark presentation table for slides and demos.", ["dark", "presentation", "demo", "深色"], ["dark"], header_facecolor="#1F2937", header_text_color="#F9FAFB", body_facecolor="#111827", alternate_row_facecolor="#172033", edgecolor="#374151", linewidth=0.6, font_size=12, zebra=True, priority=0.75),
    "pastel_table": _t("pastel_table", "Soft pastel table for playful explanatory figures.", ["pastel", "cute", "kawaii", "可爱", "柔和"], ["kawaii_table", "cute_table"], header_facecolor="#F7DDE8", alternate_row_facecolor="#FFF6FA", edgecolor="#E8B8CC", linewidth=0.6, font_size=11, zebra=True, priority=0.85),
    "monochrome_print_table": _t("monochrome_print_table", "Black-and-white print-safe table with clear rules.", ["monochrome", "print", "blackwhite", "打印", "黑白"], ["print_table"], header_facecolor="#EFEFEF", alternate_row_facecolor=None, edgecolor="#111111", linewidth=0.8, font_size=10, zebra=False, minimal_edges=True, priority=1.08),
}


@dataclass(frozen=True)
class FigureStyle:
    font_size: int | None = None
    axes_linewidth: float | None = None
    palette: str | Sequence[str] | Mapping[str, str] = "nature_modern"
    color_roles: Mapping[str, str] | None = None
    dpi: int = 300
    font_family: tuple[str, ...] = ("Arial", "Helvetica", "DejaVu Sans", "sans-serif")
    chart_style: str | ChartStylePreset | None = "publication_minimal"
    use_tex: bool | None = None


@dataclass(frozen=True)
class FigureDesign:
    palette: PaletteSelection
    chart_style: ChartStylePreset
    reason: str
    llm_prompt: str
    table_style: TableStylePreset | None = None


STYLE_TEXT_CUES = {
    "nature": "nature_journal",
    "science": "science_compact",
    "cell": "science_compact",
    "ieee": "ieee_transactions",
    "trans": "ieee_transactions",
    "acm": "acm_conference",
    "sig": "acm_conference",
    "neurips": "neurips_ml",
    "icml": "neurips_ml",
    "iclr": "neurips_ml",
    "cvpr": "neurips_ml",
    "seaborn": "seaborn_whitegrid",
    "whitegrid": "seaborn_whitegrid",
    "darkgrid": "seaborn_darkgrid",
    "ticks": "seaborn_ticks",
    "ggplot": "ggplot_gray",
    "ggplot2": "ggplot_gray",
    "theme_gray": "ggplot_gray",
    "theme_bw": "ggplot_bw",
    "theme_minimal": "ggplot_minimal",
    "theme_classic": "ggplot_classic",
    "matplotlib": "boxed_classic",
    "默认": "boxed_classic",
    "classic": "boxed_classic",
    "论文": "publication_minimal",
    "简洁": "publication_minimal",
    "datawrapper": "datawrapper_clean",
    "新闻": "datawrapper_clean",
    "editorial": "datawrapper_clean",
    "observable": "observable_modern",
    "d3": "observable_modern",
    "tableau": "tableau_dashboard",
    "dashboard": "tableau_dashboard",
    "economist": "economist_magazine",
    "financial times": "financial_times_report",
    "ft": "financial_times_report",
    "毕业论文": "thesis_clean",
    "报告": "thesis_clean",
    "答辩": "presentation_large",
    "presentation": "presentation_large",
    "ppt": "presentation_large",
    "slide": "presentation_large",
    "poster": "poster_infographic",
    "海报": "poster_infographic",
    "annotation": "annotation_focus",
    "标注": "annotation_focus",
    "explain": "annotation_focus",
    "heatmap": "scientific_heatmap",
    "热力图": "scientific_heatmap",
    "matrix": "scientific_heatmap",
    "矩阵": "scientific_heatmap",
    "黑白": "monochrome_print",
    "打印": "monochrome_print",
    "appendix": "dense_appendix",
    "附录": "dense_appendix",
    "pastel": "soft_pastel_journal",
    "柔和": "soft_pastel_journal",
    "手绘": "cartoon_handdrawn",
    "卡通": "cartoon_handdrawn",
    "漫画": "cartoon_handdrawn",
    "二次元": "cartoon_handdrawn",
    "anime": "cartoon_handdrawn",
    "kawaii": "cartoon_handdrawn",
    "cute": "cartoon_handdrawn",
    "xkcd": "cartoon_handdrawn",
    "cyber": "cyber_dark",
    "tech_dark": "cyber_dark",
    "dark": "dark_presentation",
    "深色": "dark_presentation",
}

_HARD_STYLE_CUES = {
    "手绘": "cartoon_handdrawn",
    "xkcd": "cartoon_handdrawn",
    "handdrawn": "cartoon_handdrawn",
    "sketch": "cartoon_handdrawn",
    "三线表": "academic_three_line",
    "theme_minimal": "ggplot_minimal",
    "theme_bw": "ggplot_bw",
    "theme_classic": "ggplot_classic",
    "darkgrid": "seaborn_darkgrid",
    "whitegrid": "seaborn_whitegrid",
}


def _score_chart_style(
    preset: ChartStylePreset,
    request: str,
    venue: str | None,
    figure_type: str | None,
) -> float:
    req = (request or "").lower()
    text = " ".join([preset.name, preset.description, *preset.tags, *preset.aliases]).lower()
    score = 2.0 * preset.priority
    score += sum(1.5 for token in _tokens(req) if token in text)
    for key, target in STYLE_TEXT_CUES.items():
        if key in req and target == preset.name:
            score += 4.0
            if key in _HARD_STYLE_CUES and _HARD_STYLE_CUES[key] == preset.name:
                score += 6.0
    if venue and venue.lower() in text:
        score += 4.0
    if figure_type in {"heatmap", "matrix", "correlation", "confusion_matrix"}:
        if preset.name == "scientific_heatmap":
            score += 3.0
        if preset.grid == "xy":
            score -= 0.6
    if figure_type in {"line", "trend", "convergence"} and preset.grid in {"y", "xy"}:
        score += 0.5
    if figure_type in {"grouped_bar", "bar", "ablation"} and preset.bar_edgecolor == "black":
        score += 0.4
    if figure_type == "table":
        score -= 0.3
    return score


def resolve_chart_style(
    request: str | None = None,
    venue: str | None = None,
    figure_type: str | None = None,
    style_name: str | None = None,
) -> ChartStylePreset:
    if style_name:
        key = style_name.lower()
        if key in CHART_STYLE_REGISTRY:
            return CHART_STYLE_REGISTRY[key]
        for preset in CHART_STYLE_REGISTRY.values():
            if key in preset.aliases:
                return preset
        raise ValueError(f"Unknown chart style {style_name!r}; available={sorted(CHART_STYLE_REGISTRY)}")
    return sorted(
        CHART_STYLE_REGISTRY.values(),
        key=lambda p: _score_chart_style(p, request or "", venue, figure_type),
        reverse=True,
    )[0]


def build_llm_chart_style_prompt(
    request: str,
    figure_type: str | None = None,
    venue: str | None = None,
    candidates: Sequence[ChartStylePreset] | None = None,
) -> str:
    ranked = (
        list(candidates)
        if candidates
        else sorted(
            CHART_STYLE_REGISTRY.values(),
            key=lambda p: _score_chart_style(p, request, venue, figure_type),
            reverse=True,
        )[:8]
    )
    payload = {
        "user_style_request": request,
        "figure_type": figure_type,
        "venue": venue,
        "rules": [
            "Chart style controls form: grid, spines, linewidth, marker scale, legend, background, and sketch/dark/presentation behavior.",
            "Palette controls color only; do not confuse palette with chart style.",
            "Use formal journal styles for main-paper results.",
            "Use seaborn/ggplot/Datawrapper/Tableau/Observable-like styles when the request explicitly signals those ecosystems.",
            "Use cartoon/hand-drawn styles only when explicitly requested or for slides/explanatory figures.",
            "Avoid dark backgrounds for paper submissions unless requested.",
        ],
        "candidates": [c.as_dict() for c in ranked],
        "required_json_schema": {
            "selected_chart_style": "candidate name",
            "reason": "brief reason",
        },
    }
    return "Choose one chart-style preset and return strict JSON only.\n\n" + json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )


TABLE_TEXT_CUES = {
    "三线表": "academic_three_line",
    "booktabs": "academic_three_line",
    "paper": "academic_three_line",
    "论文": "academic_three_line",
    "journal": "journal_compact_table",
    "compact": "journal_compact_table",
    "dense": "journal_compact_table",
    "appendix": "journal_compact_table",
    "dataframe": "dataframe_zebra",
    "pandas": "dataframe_zebra",
    "zebra": "dataframe_zebra",
    "dashboard": "dashboard_table",
    "tableau": "dashboard_table",
    "editorial": "editorial_table",
    "datawrapper": "editorial_table",
    "news": "editorial_table",
    "minimal": "minimal_table",
    "简洁": "minimal_table",
    "dark": "dark_table",
    "深色": "dark_table",
    "pastel": "pastel_table",
    "cute": "pastel_table",
    "可爱": "pastel_table",
    "黑白": "monochrome_print_table",
    "打印": "monochrome_print_table",
}


def _score_table_style(preset: TableStylePreset, request: str, venue: str | None = None) -> float:
    req = (request or "").lower()
    text = " ".join([preset.name, preset.description, *preset.tags, *preset.aliases]).lower()
    score = 2.0 * preset.priority
    score += sum(1.5 for token in _tokens(req) if token in text)
    score += sum(4.0 for key, target in TABLE_TEXT_CUES.items() if key in req and target == preset.name)
    if venue and venue.lower() in text:
        score += 3.0
    return score


def suggest_table_styles(
    request: str,
    venue: str | None = None,
    top_k: int = 6,
) -> list[TableStylePreset]:
    return sorted(
        TABLE_STYLE_REGISTRY.values(),
        key=lambda p: _score_table_style(p, request, venue),
        reverse=True,
    )[:top_k]


def resolve_table_style(
    request: str | None = None,
    venue: str | None = None,
    style_name: str | None = None,
) -> TableStylePreset:
    if style_name:
        key = style_name.lower()
        if key in TABLE_STYLE_REGISTRY:
            return TABLE_STYLE_REGISTRY[key]
        for preset in TABLE_STYLE_REGISTRY.values():
            if key in preset.aliases:
                return preset
        raise ValueError(f"Unknown table style {style_name!r}; available={sorted(TABLE_STYLE_REGISTRY)}")
    return suggest_table_styles(request or "", venue, 1)[0]


def build_llm_table_style_prompt(
    request: str,
    venue: str | None = None,
    candidates: Sequence[TableStylePreset] | None = None,
) -> str:
    ranked = list(candidates) if candidates else suggest_table_styles(request, venue, top_k=6)
    payload = {
        "user_style_request": request,
        "venue": venue,
        "rules": [
            "For paper tables, prefer three-line/booktabs style: minimal rules, no vertical clutter, readable header.",
            "For reports or dashboards, zebra rows and light gridlines are acceptable.",
            "For dense appendix tables, reduce font size and line weight before shrinking content unreadably.",
            "Keep numeric alignment and significant digits consistent; style should never hide precision.",
        ],
        "candidates": [c.as_dict() for c in ranked],
        "required_json_schema": {
            "selected_table_style": "candidate name",
            "reason": "brief reason",
        },
    }
    return "Choose one publication-ready table-style preset and return strict JSON only.\n\n" + json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )


def apply_table_style(table: Any, preset: TableStylePreset | str | None = None, request: str | None = None, venue: str | None = None):
    """Apply a registered table style to a Matplotlib table-like object.

    The object is expected to expose ``get_celld()`` as returned by
    ``matplotlib.axes.Axes.table``. The function returns the table object so it
    can be chained inside plotting scripts.
    """
    resolved = preset if isinstance(preset, TableStylePreset) else resolve_table_style(request, venue, preset)
    if not hasattr(table, "get_celld"):
        raise TypeError("apply_table_style expects a Matplotlib Table-like object with get_celld().")
    cells = table.get_celld()
    for (row, _col), cell in cells.items():
        cell.set_edgecolor(resolved.edgecolor)
        cell.set_linewidth(resolved.linewidth)
        cell.PAD = resolved.cell_padding
        cell.get_text().set_fontsize(resolved.font_size)
        if row == 0:
            cell.set_facecolor(resolved.header_facecolor)
            cell.get_text().set_color(resolved.header_text_color)
            cell.get_text().set_weight(resolved.header_weight)
        else:
            if resolved.zebra and resolved.alternate_row_facecolor and row % 2 == 0:
                cell.set_facecolor(resolved.alternate_row_facecolor)
            else:
                cell.set_facecolor(resolved.body_facecolor)
        if resolved.minimal_edges and hasattr(cell, "visible_edges"):
            cell.visible_edges = "horizontal"
    return table


@dataclass(frozen=True)
class FigureDesign:
    palette: PaletteSelection
    chart_style: ChartStylePreset
    reason: str
    llm_prompt: str
    table_style: TableStylePreset | None = None


def auto_figure_design(
    request: str,
    figure_type: str | None = None,
    n_colors: int | None = None,
    data_role: str | None = None,
    venue: str | None = None,
) -> FigureDesign:
    palette = auto_palette(request, figure_type, n_colors, data_role, venue=venue)
    chart_style = resolve_chart_style(request, venue, figure_type)
    table_style = resolve_table_style(request, venue) if figure_type == "table" or "表" in (request or "") or "table" in (request or "").lower() else None
    reason = (
        f"Palette={palette.name}; chart_style={chart_style.name}"
        + (f"; table_style={table_style.name}" if table_style else "")
        + ". Palette was selected by color-quality heuristics; chart style was selected by venue/form heuristics."
    )
    payload = {
        "palette_prompt": palette.llm_prompt,
        "chart_style_prompt": build_llm_chart_style_prompt(request, figure_type, venue),
    }
    if table_style:
        payload["table_style_prompt"] = build_llm_table_style_prompt(request, venue)
    return FigureDesign(
        palette,
        chart_style,
        reason,
        json.dumps(payload, ensure_ascii=False, indent=2),
        table_style,
    )


def apply_chart_style(
    preset: ChartStylePreset | str | None = None,
    request: str | None = None,
    figure_type: str | None = None,
    venue: str | None = None,
) -> ChartStylePreset:
    resolved = preset if isinstance(preset, ChartStylePreset) else resolve_chart_style(request, venue, figure_type, preset)
    rc = {
        "axes.spines.right": resolved.spine_mode == "boxed",
        "axes.spines.top": resolved.spine_mode == "boxed",
        "legend.frameon": resolved.legend_frame,
        "axes.grid": resolved.grid != "none",
        "axes.axisbelow": True,
        "grid.alpha": 0.55,
        "grid.linestyle": "-",
        "lines.linewidth": resolved.line_width,
        "lines.markersize": resolved.marker_size,
        "patch.linewidth": resolved.bar_linewidth,
        "patch.edgecolor": resolved.bar_edgecolor,
        "savefig.dpi": resolved.dpi,
    }
    rc["axes.grid.axis"] = "both" if resolved.grid == "xy" else "y" if resolved.grid == "y" else "both"
    rc.update(resolved.rc_params or {})
    mpl.rcParams.update(rc)
    return resolved


def resolve_palette(
    palette: str | Sequence[str] | Mapping[str, str] = "nature_modern",
    n: int | None = None,
) -> list[str]:
    if isinstance(palette, str):
        colors = (
            list(PALETTE_REGISTRY[palette].colors)
            if palette in PALETTE_REGISTRY
            else [palette]
            if palette.startswith("#")
            else None
        )
        if colors is None:
            raise ValueError(f"Unknown palette {palette!r}")
    elif isinstance(palette, Mapping):
        colors = [palette[k] for k in BASE_ROLE_ORDER if k in palette] + [
            v for k, v in palette.items() if k not in BASE_ROLE_ORDER
        ]
    else:
        colors = list(palette)
    colors = [c for c in colors if to_rgba(c) or True]
    return colors if n is None else [colors[i % len(colors)] for i in range(n)]


def resolve_colors(
    labels: Sequence[str],
    palette="nature_modern",
    color_roles: Mapping[str, str] | None = None,
) -> list[str]:
    colors = resolve_palette(palette)
    role_map = {r: colors[i % len(colors)] for i, r in enumerate(BASE_ROLE_ORDER)}
    cycle = resolve_palette(palette, len(labels))
    out = []
    for i, label in enumerate(map(str, labels)):
        role = (color_roles or {}).get(label)
        out.append(role if role and role.startswith("#") else role_map.get(role, cycle[i]) if role else cycle[i])
    return out


def apply_publication_style(
    style: FigureStyle | None = None,
    chart_style: str | ChartStylePreset | None = None,
) -> FigureStyle:
    style = style or FigureStyle()
    preset = apply_chart_style(chart_style if chart_style is not None else style.chart_style)
    font_size = style.font_size if style.font_size is not None else preset.font_size
    axes_lw = style.axes_linewidth if style.axes_linewidth is not None else preset.axes_linewidth
    use_tex = preset.use_tex if style.use_tex is None else style.use_tex
    mpl.rcParams.update(
        {
            "font.family": list(style.font_family),
            "font.size": font_size,
            "axes.linewidth": axes_lw,
            "legend.frameon": preset.legend_frame,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "text.usetex": use_tex,
        }
    )
    if preset.use_xkcd:
        mpl.rcParams["path.sketch"] = (1, 100, 2)
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=resolve_palette(style.palette))
    return replace(style, font_size=font_size, axes_linewidth=axes_lw, dpi=style.dpi or preset.dpi)


def make_cmap(palette="nature_modern", name="custom_cmap"):
    colors = resolve_palette(palette)
    return LinearSegmentedColormap.from_list(
        name,
        colors if len(colors) > 1 else ["#FFFFFF", colors[0]],
    )
