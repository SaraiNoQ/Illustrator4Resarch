#!/usr/bin/env python3
"""Heuristic palette and chart-style design layer for scientific figures.

This module is intentionally standalone-friendly. When installed globally it imports
base plotting primitives from sibling `figure_toolkit.py`; inside the repository it
falls back to `scientific_figure_skill.core`.
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
BASE_ROLE_ORDER = getattr(_base, "ROLE_ORDER", ("proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "improvement", "uncertainty"))


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
def _make_base_like(name: str, colors: Sequence[str], kind: str, source: str, tags: Sequence[str], desc: str, cb=False, ps=False, priority=1.0):
    try:
        return BasePaletteCandidate(name, tuple(colors), kind, source, tuple(sorted(set(tags))), desc, cb, ps, priority)  # old base signature
    except TypeError:
        return GeneratedPaletteCandidate(name, tuple(colors), kind, source, tuple(sorted(set(tags))), desc, cb, ps, priority, False)


PALETTE_REGISTRY = {
    **BASE_PALETTE_REGISTRY,
    "warm_muted": _make_base_like("warm_muted", ["#8F3F3F", "#C46A3A", "#D6A03D", "#A56F5D", "#6F6F6F", "#D9C7B8"], "categorical", "curated-publication", ["warm", "muted", "soft", "humanities", "review", "暖色", "柔和"], "Muted warm palette for narrative or review-style figures.", False, True, 1.05),
}

TEXT_CUES: dict[str, dict[str, Any]] = {
    "nature": {"venue": "nature", "mood": "muted"}, "science": {"venue": "science", "mood": "formal"}, "cell": {"venue": "cell", "mood": "muted"},
    "ieee": {"venue": "ieee", "mood": "formal", "temperature": "cool"}, "acm": {"venue": "acm", "mood": "formal"},
    "neurips": {"venue": "neurips", "mood": "minimal"}, "icml": {"venue": "icml", "mood": "minimal"}, "cvpr": {"venue": "cvpr", "mood": "minimal"},
    "简洁": {"mood": "formal"}, "大气": {"mood": "formal"}, "克制": {"mood": "formal", "temperature": "cool"}, "柔和": {"mood": "muted", "contrast": "low"}, "高级": {"mood": "muted"}, "现代": {"mood": "bright"},
    "科技": {"temperature": "cool"}, "冷色": {"temperature": "cool"}, "暖色": {"temperature": "warm"}, "高对比": {"contrast": "high"},
    "色盲": {"prefer_colorblind": True}, "黑白": {"prefer_grayscale": True, "prefer_print": True}, "打印": {"prefer_print": True},
    "手绘": {"mood": "playful"}, "卡通": {"mood": "playful"}, "cartoon": {"mood": "playful"}, "xkcd": {"mood": "playful"},
    "heatmap": {"kind": "sequential"}, "热力图": {"kind": "sequential"}, "连续": {"kind": "sequential"},
    "正负": {"kind": "diverging"}, "差异": {"kind": "diverging"}, "difference": {"kind": "diverging"}, "delta": {"kind": "diverging"}, "correlation": {"kind": "diverging"},
    "多方法": {"kind": "categorical", "density": "dense"}, "主实验": {"kind": "categorical"}, "消融": {"kind": "categorical", "mood": "formal"},
}
FIGURE_KIND = {"grouped_bar": "categorical", "bar": "categorical", "ablation": "categorical", "line": "categorical", "trend": "categorical", "convergence": "categorical", "scatter": "categorical", "heatmap": "sequential", "matrix": "sequential", "correlation": "diverging", "difference_heatmap": "diverging", "residual_heatmap": "diverging"}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_+\-/]+|[\u4e00-\u9fff]+", (text or "").lower())


def infer_kind(request: str = "", figure_type: str | None = None, data_role: str | None = None) -> str:
    if data_role in {"categorical", "sequential", "diverging", "grayscale"}:
        return data_role
    if figure_type and figure_type.lower() in FIGURE_KIND:
        return FIGURE_KIND[figure_type.lower()]
    lowered = (request or "").lower()
    for key, cue in TEXT_CUES.items():
        if key in lowered and "kind" in cue:
            return str(cue["kind"])
    return "categorical"


def infer_palette_intent(request: str = "", figure_type: str | None = None, data_role: str | None = None, n_colors: int | None = None, venue: str | None = None) -> PaletteIntent:
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
            kind = str(cue.get("kind", kind)); mood = str(cue.get("mood", mood)); temperature = str(cue.get("temperature", temperature)); contrast = str(cue.get("contrast", contrast))
            prefer_colorblind = bool(cue.get("prefer_colorblind", prefer_colorblind)); prefer_print = bool(cue.get("prefer_print", prefer_print)); prefer_grayscale = bool(cue.get("prefer_grayscale", prefer_grayscale))
            density = str(cue.get("density", density)); inferred_venue = str(cue.get("venue", inferred_venue)) if cue.get("venue", inferred_venue) else inferred_venue
    known = set(TEXT_CUES)
    unknown = tuple(t for t in _tokens(request) if all(k not in t and t not in k for k in known) and len(t) > 1)
    if prefer_grayscale:
        kind = "grayscale"
    return PaletteIntent(kind, mood, temperature, contrast, prefer_colorblind, prefer_print, prefer_grayscale, density, inferred_venue, min(0.95, 0.35 + 0.12 * hits), unknown)


def _rgb(color: str) -> tuple[float, float, float]:
    r, g, b, _ = to_rgba(color); return float(r), float(g), float(b)

def _hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c * 255))) for c in rgb))

def _blend(c1: str, c2: str, amount: float) -> str:
    a, b = _rgb(c1), _rgb(c2); return _hex(tuple((1 - amount) * x + amount * y for x, y in zip(a, b)))

def _adjust_saturation(color: str, factor: float) -> str:
    r, g, b = _rgb(color); h, l, s = colorsys.rgb_to_hls(r, g, b); return _hex(colorsys.hls_to_rgb(h, l, max(0, min(1, s * factor))))

def _adjust_lightness(color: str, factor: float) -> str:
    r, g, b = _rgb(color); h, l, s = colorsys.rgb_to_hls(r, g, b); return _hex(colorsys.hls_to_rgb(h, max(0, min(1, l * factor)), s))

def _luminance(color: str) -> float:
    r, g, b = _rgb(color)
    def ch(v): return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def _saturation(color: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(color))[2]

def _hue(color: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(color))[0]

def _pair_distance(c1: str, c2: str) -> float:
    r1, g1, b1 = _rgb(c1); r2, g2, b2 = _rgb(c2)
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) + 0.8 * abs(_luminance(c1) - _luminance(c2))

def _min_pair_distance(colors: Sequence[str]) -> float:
    return 1.0 if len(colors) < 2 else min(_pair_distance(a, b) for i, a in enumerate(colors) for b in colors[i+1:])

def _hue_spread(colors: Sequence[str]) -> float:
    hues = sorted(_hue(c) for c in colors if _saturation(c) > 0.05)
    if len(hues) < 2: return 0.0
    gaps = [hues[i+1] - hues[i] for i in range(len(hues)-1)] + [1 + hues[0] - hues[-1]]
    return 1 - max(gaps)

def _is_monotone(values: Sequence[float]) -> bool:
    return len(values) < 3 or all(a <= b + 1e-9 for a, b in zip(values, values[1:])) or all(a + 1e-9 >= b for a, b in zip(values, values[1:]))


def palette_quality(colors: Sequence[str], kind: str = "categorical") -> dict[str, float]:
    colors = tuple(colors); lums = [_luminance(c) for c in colors]; sats = [_saturation(c) for c in colors]
    min_dist = _min_pair_distance(colors); lum_range = max(lums) - min(lums) if lums else 0.0; sat_mean = float(np.mean(sats)) if sats else 0.0; hue_spread = _hue_spread(colors); monotone = 1.0 if _is_monotone(lums) else 0.0
    if kind == "categorical": score = 0.34*min(1, min_dist/0.45) + 0.26*min(1, hue_spread/0.55) + 0.20*min(1, lum_range/0.55) + 0.20*(1-abs(sat_mean-0.55))
    elif kind == "sequential": score = 0.45*monotone + 0.35*min(1, lum_range/0.70) + 0.20*min(1, min_dist/0.30)
    elif kind == "diverging":
        mid_lum = _luminance(colors[len(colors)//2]) if colors else 0.9
        score = 0.35*min(1, lum_range/0.70) + 0.25*min(1, min_dist/0.30) + 0.25*(1-abs(mid_lum-0.88)) + 0.15*min(1, hue_spread/0.45)
    else: score = 0.45*min(1, lum_range/0.70) + 0.35*monotone + 0.20*min(1, min_dist/0.25)
    return {"score": round(float(max(0, min(1, score))), 4), "min_pair_distance": round(float(min_dist), 4), "luminance_range": round(float(lum_range), 4), "mean_saturation": round(float(sat_mean), 4), "hue_spread": round(float(hue_spread), 4), "monotone_luminance": float(monotone)}


def candidate_as_dict(c: Any) -> dict[str, Any]:
    return {"name": c.name, "colors": list(c.colors), "kind": c.kind, "source": c.source, "tags": list(c.tags), "description": c.description, "colorblind_safe": bool(getattr(c, "colorblind_safe", False)), "print_safe": bool(getattr(c, "print_safe", False)), "generated": bool(getattr(c, "generated", False)), "quality": palette_quality(c.colors, c.kind)}


def _variant(candidate: Any, suffix: str, colors: Sequence[str], tags: Sequence[str], desc: str, priority_delta: float = -0.02) -> GeneratedPaletteCandidate:
    return GeneratedPaletteCandidate(f"{candidate.name}_{suffix}", tuple(colors), candidate.kind, f"{candidate.source}+generated", tuple(sorted(set(tuple(candidate.tags) + tuple(tags)))), desc, bool(getattr(candidate, "colorblind_safe", False)), bool(getattr(candidate, "print_safe", False)), max(0.85, float(getattr(candidate, "priority", 1.0)) + priority_delta), True)


def generate_palette_variants(candidate: Any, intent: PaletteIntent, n_colors: int | None = None) -> list[GeneratedPaletteCandidate]:
    colors = list(candidate.colors); out: list[GeneratedPaletteCandidate] = []
    if candidate.kind == "categorical":
        if intent.mood in {"muted", "formal"} or intent.venue in {"nature", "science", "cell"}:
            out.append(_variant(candidate, "muted", [_adjust_saturation(_blend(c, "#FFFFFF", 0.08), 0.72) for c in colors], ["generated", "muted", "formal"], "Generated muted variant for refined publication style."))
        if intent.contrast == "high" or intent.density == "dense":
            out.append(_variant(candidate, "contrast", [_adjust_saturation(_adjust_lightness(c, 0.88 if _luminance(c) > 0.55 else 1.05), 1.12) for c in colors], ["generated", "high_contrast", "dense"], "Generated higher-contrast variant for dense method comparisons."))
        if intent.temperature == "cool":
            out.append(_variant(candidate, "cool", [_blend(c, "#1F4E79", 0.18) if i % 2 == 0 else _blend(c, "#42949E", 0.12) for i, c in enumerate(colors)], ["generated", "cool"], "Generated cool-toned variant."))
        if intent.temperature == "warm":
            out.append(_variant(candidate, "warm", [_blend(c, "#C46A3A", 0.18) if i % 2 == 0 else _blend(c, "#D6A03D", 0.10) for i, c in enumerate(colors)], ["generated", "warm"], "Generated warm-toned variant."))
    if intent.prefer_grayscale or candidate.kind == "grayscale":
        vals = np.linspace(0.08, 0.82, max(n_colors or len(colors) or 6, 3)); out.append(_variant(candidate, "gray_generated", [_hex((v, v, v)) for v in vals], ["generated", "grayscale", "print"], "Generated grayscale fallback with monotone luminance.", 0.0))
    return out


def _candidate_text_match(candidate: Any, request: str) -> float:
    text = " ".join([candidate.name, candidate.source, candidate.description, *candidate.tags]).lower(); score = 0.0
    for token in _tokens(request):
        if token in text: score += 1.2
        elif token:
            chars = set(token); overlap = max((len(chars & set(w)) / len(chars | set(w)) for w in re.findall(r"[a-zA-Z0-9_+\-/]+", text)), default=0.0)
            if overlap > 0.55: score += 0.25 * overlap
    return score


def _score_palette(candidate: Any, intent: PaletteIntent, request: str, n_colors: int | None) -> float:
    q = palette_quality(candidate.colors, candidate.kind); score = 5.0 * q["score"] + float(getattr(candidate, "priority", 1.0)) + _candidate_text_match(candidate, request)
    score += 3.5 if candidate.kind == intent.kind else (-2.5 if intent.kind in {"sequential", "diverging"} and candidate.kind == "categorical" else -1.0 if intent.kind == "categorical" and candidate.kind in {"sequential", "diverging"} else 0.0)
    tags = set(candidate.tags)
    score += 1.1 if intent.mood in tags else 0.0; score += 0.9 if intent.temperature in tags else 0.0; score += 1.8 if intent.venue and intent.venue in tags else 0.0
    score += 1.2 if intent.prefer_colorblind and getattr(candidate, "colorblind_safe", False) else -0.5 if intent.prefer_colorblind else 0.0
    score += 1.2 if intent.prefer_print and getattr(candidate, "print_safe", False) else -0.2 if intent.prefer_print else 0.0
    score += 3.0 if intent.prefer_grayscale and (candidate.kind == "grayscale" or "grayscale" in tags) else -1.0 if intent.prefer_grayscale else 0.0
    if n_colors and candidate.kind == "categorical": score += 0.8 if len(candidate.colors) >= n_colors else -0.75 * (n_colors - len(candidate.colors))
    if intent.density == "dense": score += q["min_pair_distance"] + (0.6 if candidate.kind == "categorical" and len(candidate.colors) >= (n_colors or 6) else 0.0)
    if getattr(candidate, "generated", False): score += 0.25 if intent.confidence < 0.75 else 0.05
    return score


def suggest_palettes(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6, venue: str | None = None, include_generated: bool = True) -> list[Any]:
    intent = infer_palette_intent(request, figure_type, data_role, n_colors, venue); candidates = list(PALETTE_REGISTRY.values())
    if include_generated: candidates += [v for c in list(PALETTE_REGISTRY.values()) for v in generate_palette_variants(c, intent, n_colors)]
    return sorted(candidates, key=lambda c: _score_palette(c, intent, request, n_colors), reverse=True)[:top_k]


def _roles(candidate: Any) -> dict[str, str]:
    colors = list(candidate.colors)
    if candidate.kind in {"sequential", "diverging", "grayscale"}: return {"low": colors[0], "mid": colors[len(colors)//2], "high": colors[-1], "neutral": "#F7F7F7"}
    return {r: colors[i % len(colors)] for i, r in enumerate(["proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "uncertainty"])}


def build_llm_palette_selection_prompt(request: str, figure_type: str | None, candidates: Sequence[Any], n_colors: int | None = None, extra_context: str | None = None, venue: str | None = None) -> str:
    payload = {"user_style_request": request, "figure_type": figure_type, "n_colors": n_colors, "extra_context": extra_context or "", "heuristic_intent": infer_palette_intent(request, figure_type, n_colors=n_colors, venue=venue).__dict__, "rules": ["Choose by scientific readability first, aesthetics second.", "For categorical comparison, prefer separation, colorblind safety, and enough colors.", "For heatmaps, prefer monotone-luminance sequential palettes unless data is centered around zero.", "Generated variants are allowed when they better match the requested mood.", "Use highlight once only."], "candidates": [candidate_as_dict(c) for c in candidates], "required_json_schema": {"selected_palette": "candidate name", "reason": "brief reason", "color_roles": {"proposed": "#hex", "baseline": "#hex", "secondary": "#hex", "ablation": "#hex", "neutral": "#hex", "highlight": "#hex"}}}
    return "Choose one publication-ready palette and return strict JSON only.\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def auto_palette(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6, venue: str | None = None) -> PaletteSelection:
    intent = infer_palette_intent(request, figure_type, data_role, n_colors, venue); cands = suggest_palettes(request, figure_type, n_colors, data_role, top_k, venue); sel = cands[0]
    reason = f"Selected {sel.name} by request-profile and palette-quality scoring (kind={intent.kind}, mood={intent.mood}, temperature={intent.temperature}, contrast={intent.contrast}, generated={bool(getattr(sel, 'generated', False))})."
    return PaletteSelection(sel.name, tuple(sel.colors), _roles(sel), reason, tuple(c.name for c in cands), build_llm_palette_selection_prompt(request, figure_type, cands, n_colors, venue=venue), intent)


def apply_llm_palette_decision(decision: str | Mapping[str, Any], candidates: Sequence[Any]) -> PaletteSelection:
    obj = json.loads(decision) if isinstance(decision, str) else dict(decision); names = {c.name: c for c in candidates}; name = str(obj.get("selected_palette", "")).strip()
    if name not in names: raise ValueError(f"Unknown palette {name!r}; available={sorted(names)}")
    c = names[name]; roles = obj.get("color_roles") or _roles(c)
    if not isinstance(roles, Mapping): raise ValueError("color_roles must be an object")
    return PaletteSelection(name, tuple(c.colors), {str(k): str(v) for k, v in roles.items()}, str(obj.get("reason", "LLM selected palette.")), tuple(names))


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
        return {"name": self.name, "description": self.description, "tags": list(self.tags), "aliases": list(self.aliases), "font_size": self.font_size, "axes_linewidth": self.axes_linewidth, "line_width": self.line_width, "marker_size": self.marker_size, "bar_edgecolor": self.bar_edgecolor, "bar_linewidth": self.bar_linewidth, "grid": self.grid, "spine_mode": self.spine_mode, "legend_frame": self.legend_frame, "use_xkcd": self.use_xkcd, "dpi": self.dpi}


def _s(name, desc, tags, aliases=(), **kwargs):
    return ChartStylePreset(name, desc, tuple(sorted(set(tags))), tuple(aliases), **kwargs)


CHART_STYLE_REGISTRY: dict[str, ChartStylePreset] = {
    "publication_minimal": _s("publication_minimal", "General minimal academic Matplotlib style: open axes, no decorative grid, high readability.", ["paper", "minimal", "clean", "default", "academic", "简洁", "论文"], ["academic", "matplotlib_academic"], font_size=16, axes_linewidth=2.0, grid="none", priority=1.25),
    "nature_journal": _s("nature_journal", "Nature-like compact high-impact journal panel: restrained axes, small typography, little grid.", ["nature", "journal", "high_impact", "compact", "muted", "科研"], ["nature", "nature_style"], font_size=14, axes_linewidth=1.6, line_width=2.2, marker_size=5.0, grid="none", priority=1.32),
    "ieee_transactions": _s("ieee_transactions", "IEEE/engineering style: compact, conservative, print-safe, restrained grid.", ["ieee", "transactions", "engineering", "compact", "print", "严肃"], ["ieee", "trans"], font_size=13, axes_linewidth=1.5, line_width=2.0, marker_size=4.5, grid="y", priority=1.28),
    "acm_conference": _s("acm_conference", "ACM/CS conference style: compact and readable at one-column width.", ["acm", "conference", "computer_science", "compact"], ["sig", "conference"], font_size=13, axes_linewidth=1.5, line_width=2.0, marker_size=4.5, grid="y", priority=1.18),
    "neurips_ml": _s("neurips_ml", "ML conference style: clean white background, light y-grid, thicker curves.", ["neurips", "icml", "iclr", "ml", "conference", "modern"], ["icml", "iclr", "ml"], font_size=15, axes_linewidth=1.8, line_width=2.6, marker_size=5.5, grid="y", priority=1.22),
    "seaborn_whitegrid": _s("seaborn_whitegrid", "Seaborn-like whitegrid visual grammar implemented with Matplotlib rcParams only.", ["seaborn", "whitegrid", "grid", "statistical", "modern"], ["whitegrid", "sns_whitegrid"], font_size=15, axes_linewidth=1.4, line_width=2.3, grid="xy", rc_params={"axes.facecolor": "white", "grid.color": "#E6E6E6", "grid.linewidth": 0.8}, priority=1.05),
    "seaborn_ticks": _s("seaborn_ticks", "Seaborn-like ticks style: clean spines, no heavy grid, statistical plotting feel.", ["seaborn", "ticks", "statistical", "clean"], ["ticks", "sns_ticks"], font_size=15, axes_linewidth=1.5, line_width=2.2, grid="none", priority=1.04),
    "boxed_classic": _s("boxed_classic", "Classic boxed Matplotlib academic style for conservative reports.", ["classic", "matplotlib", "boxed", "report", "传统"], ["matplotlib_default", "classic"], font_size=15, axes_linewidth=1.4, line_width=2.0, grid="none", spine_mode="boxed", legend_frame=True, priority=0.98),
    "thesis_clean": _s("thesis_clean", "Thesis/report style with larger fonts and clear axes.", ["thesis", "report", "slides", "clean", "毕业论文"], ["thesis", "report"], font_size=18, axes_linewidth=2.0, line_width=2.6, marker_size=6.0, grid="y", priority=1.10),
    "presentation_large": _s("presentation_large", "Large-font slide style with bolder lines.", ["slide", "presentation", "large", "talk", "答辩"], ["ppt", "slides"], font_size=22, axes_linewidth=2.6, line_width=3.0, marker_size=7.0, grid="y", priority=1.02),
    "cartoon_handdrawn": _s("cartoon_handdrawn", "Cartoon/hand-drawn Matplotlib style using sketch paths; use for explanatory slides, not formal main-paper figures.", ["cartoon", "handdrawn", "xkcd", "playful", "手绘", "卡通"], ["xkcd", "handdrawn", "cartoon"], font_size=17, axes_linewidth=2.0, line_width=2.8, marker_size=6.5, grid="none", use_xkcd=True, rc_params={"path.sketch": (1, 100, 2), "lines.solid_capstyle": "round"}, priority=0.85),
    "dark_presentation": _s("dark_presentation", "Dark-background presentation style; unsuitable for most paper submissions.", ["dark", "black", "presentation", "poster", "深色"], ["dark"], font_size=20, axes_linewidth=2.0, line_width=2.8, grid="y", rc_params={"figure.facecolor": "#111111", "axes.facecolor": "#111111", "axes.edgecolor": "#E6E6E6", "axes.labelcolor": "#F2F2F2", "xtick.color": "#F2F2F2", "ytick.color": "#F2F2F2", "text.color": "#F2F2F2", "grid.color": "#444444"}, priority=0.70),
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


STYLE_TEXT_CUES = {"nature": "nature_journal", "ieee": "ieee_transactions", "trans": "ieee_transactions", "acm": "acm_conference", "sig": "acm_conference", "neurips": "neurips_ml", "icml": "neurips_ml", "iclr": "neurips_ml", "seaborn": "seaborn_whitegrid", "whitegrid": "seaborn_whitegrid", "ticks": "seaborn_ticks", "matplotlib": "boxed_classic", "默认": "boxed_classic", "classic": "boxed_classic", "论文": "publication_minimal", "简洁": "publication_minimal", "毕业论文": "thesis_clean", "报告": "thesis_clean", "答辩": "presentation_large", "presentation": "presentation_large", "ppt": "presentation_large", "slide": "presentation_large", "手绘": "cartoon_handdrawn", "卡通": "cartoon_handdrawn", "xkcd": "cartoon_handdrawn", "dark": "dark_presentation", "深色": "dark_presentation"}


def _score_chart_style(preset: ChartStylePreset, request: str, venue: str | None, figure_type: str | None) -> float:
    req = (request or "").lower(); text = " ".join([preset.name, preset.description, *preset.tags, *preset.aliases]).lower(); score = 2.0 * preset.priority
    score += sum(1.5 for token in _tokens(req) if token in text)
    score += sum(4.0 for key, target in STYLE_TEXT_CUES.items() if key in req and target == preset.name)
    if venue and venue.lower() in text: score += 4.0
    if figure_type in {"heatmap", "matrix", "correlation"} and preset.grid == "xy": score -= 0.6
    if figure_type in {"line", "trend", "convergence"} and preset.grid in {"y", "xy"}: score += 0.5
    if figure_type in {"grouped_bar", "bar", "ablation"} and preset.bar_edgecolor == "black": score += 0.4
    return score


def resolve_chart_style(request: str | None = None, venue: str | None = None, figure_type: str | None = None, style_name: str | None = None) -> ChartStylePreset:
    if style_name:
        key = style_name.lower()
        if key in CHART_STYLE_REGISTRY: return CHART_STYLE_REGISTRY[key]
        for preset in CHART_STYLE_REGISTRY.values():
            if key in preset.aliases: return preset
        raise ValueError(f"Unknown chart style {style_name!r}; available={sorted(CHART_STYLE_REGISTRY)}")
    return sorted(CHART_STYLE_REGISTRY.values(), key=lambda p: _score_chart_style(p, request or "", venue, figure_type), reverse=True)[0]


def build_llm_chart_style_prompt(request: str, figure_type: str | None = None, venue: str | None = None, candidates: Sequence[ChartStylePreset] | None = None) -> str:
    ranked = list(candidates) if candidates else sorted(CHART_STYLE_REGISTRY.values(), key=lambda p: _score_chart_style(p, request, venue, figure_type), reverse=True)[:6]
    payload = {"user_style_request": request, "figure_type": figure_type, "venue": venue, "rules": ["Chart style controls form: grid, spines, linewidth, fonts, legend, and sketch/dark/presentation behavior.", "Palette controls color only; do not confuse palette with chart style.", "Use formal journal styles for main-paper results.", "Use seaborn-like or cartoon styles only when explicitly requested or for slides/explanatory figures.", "Avoid dark backgrounds for paper submissions unless requested."], "candidates": [c.as_dict() for c in ranked], "required_json_schema": {"selected_chart_style": "candidate name", "reason": "brief reason"}}
    return "Choose one chart-style preset and return strict JSON only.\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def auto_figure_design(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, venue: str | None = None) -> FigureDesign:
    palette = auto_palette(request, figure_type, n_colors, data_role, venue=venue); chart_style = resolve_chart_style(request, venue, figure_type)
    reason = f"Palette={palette.name}; chart_style={chart_style.name}. Palette was selected by color-quality heuristics; chart style was selected by venue/form heuristics."
    return FigureDesign(palette, chart_style, reason, json.dumps({"palette_prompt": palette.llm_prompt, "chart_style_prompt": build_llm_chart_style_prompt(request, figure_type, venue)}, ensure_ascii=False, indent=2))


def apply_chart_style(preset: ChartStylePreset | str | None = None, request: str | None = None, figure_type: str | None = None, venue: str | None = None) -> ChartStylePreset:
    resolved = preset if isinstance(preset, ChartStylePreset) else resolve_chart_style(request, venue, figure_type, preset)
    rc = {"axes.spines.right": resolved.spine_mode == "boxed", "axes.spines.top": resolved.spine_mode == "boxed", "legend.frameon": resolved.legend_frame, "axes.grid": resolved.grid != "none", "axes.axisbelow": True, "grid.alpha": 0.55, "grid.linestyle": "-", "lines.linewidth": resolved.line_width, "lines.markersize": resolved.marker_size, "patch.linewidth": resolved.bar_linewidth, "patch.edgecolor": resolved.bar_edgecolor, "savefig.dpi": resolved.dpi}
    rc["axes.grid.axis"] = "both" if resolved.grid == "xy" else "y" if resolved.grid == "y" else "both"
    rc.update(resolved.rc_params or {}); mpl.rcParams.update(rc); return resolved


def resolve_palette(palette: str | Sequence[str] | Mapping[str, str] = "nature_modern", n: int | None = None) -> list[str]:
    if isinstance(palette, str):
        colors = list(PALETTE_REGISTRY[palette].colors) if palette in PALETTE_REGISTRY else [palette] if palette.startswith("#") else None
        if colors is None: raise ValueError(f"Unknown palette {palette!r}")
    elif isinstance(palette, Mapping): colors = [palette[k] for k in BASE_ROLE_ORDER if k in palette] + [v for k, v in palette.items() if k not in BASE_ROLE_ORDER]
    else: colors = list(palette)
    colors = [c for c in colors if to_rgba(c) or True]
    return colors if n is None else [colors[i % len(colors)] for i in range(n)]


def resolve_colors(labels: Sequence[str], palette="nature_modern", color_roles: Mapping[str, str] | None = None) -> list[str]:
    colors = resolve_palette(palette); role_map = {r: colors[i % len(colors)] for i, r in enumerate(BASE_ROLE_ORDER)}; cycle = resolve_palette(palette, len(labels)); out = []
    for i, label in enumerate(map(str, labels)):
        role = (color_roles or {}).get(label); out.append(role if role and role.startswith("#") else role_map.get(role, cycle[i]) if role else cycle[i])
    return out


def apply_publication_style(style: FigureStyle | None = None, chart_style: str | ChartStylePreset | None = None) -> FigureStyle:
    style = style or FigureStyle(); preset = apply_chart_style(chart_style if chart_style is not None else style.chart_style)
    font_size = style.font_size if style.font_size is not None else preset.font_size; axes_lw = style.axes_linewidth if style.axes_linewidth is not None else preset.axes_linewidth; use_tex = preset.use_tex if style.use_tex is None else style.use_tex
    mpl.rcParams.update({"font.family": list(style.font_family), "font.size": font_size, "axes.linewidth": axes_lw, "legend.frameon": preset.legend_frame, "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42, "text.usetex": use_tex})
    if preset.use_xkcd: mpl.rcParams["path.sketch"] = (1, 100, 2)
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=resolve_palette(style.palette))
    return replace(style, font_size=font_size, axes_linewidth=axes_lw, dpi=style.dpi or preset.dpi)


def make_cmap(palette="nature_modern", name="custom_cmap"):
    colors = resolve_palette(palette); return LinearSegmentedColormap.from_list(name, colors if len(colors) > 1 else ["#FFFFFF", colors[0]])
