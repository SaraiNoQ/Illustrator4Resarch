#!/usr/bin/env python3
"""Standalone scientific figure helper toolkit bundled inside the skill package.

This file intentionally has no dependency on the Illustrator4Resarch repository root.
A globally installed skill can import it from:

- ~/.agents/skills/scientific-figure-making/scripts/figure_toolkit.py
- ~/.claude/skills/scientific-figure-making/scripts/figure_toolkit.py

Dependencies: Python 3, numpy, matplotlib.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import re

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgba


@dataclass(frozen=True)
class PaletteCandidate:
    name: str
    colors: tuple[str, ...]
    kind: str
    source: str
    tags: tuple[str, ...]
    description: str
    colorblind_safe: bool = False
    print_safe: bool = False
    priority: float = 1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "colors": list(self.colors),
            "kind": self.kind,
            "source": self.source,
            "tags": list(self.tags),
            "description": self.description,
            "colorblind_safe": self.colorblind_safe,
            "print_safe": self.print_safe,
        }


@dataclass(frozen=True)
class PaletteSelection:
    name: str
    colors: tuple[str, ...]
    color_roles: dict[str, str]
    reason: str
    candidates: tuple[str, ...]
    llm_prompt: str | None = None


@dataclass(frozen=True)
class FigureStyle:
    font_size: int = 16
    axes_linewidth: float = 2.2
    palette: Sequence[str] | str = "nature_modern"
    color_roles: Mapping[str, str] | None = None
    dpi: int = 300
    use_tex: bool = False
    font_family: tuple[str, ...] = ("Arial", "Helvetica", "DejaVu Sans", "sans-serif")


def _p(name, colors, kind, source, tags, desc, cb=False, ps=False, priority=1.0):
    return PaletteCandidate(name, tuple(colors), kind, source, tuple(sorted(set(tags))), desc, cb, ps, priority)


PALETTE_REGISTRY: dict[str, PaletteCandidate] = {
    "nature_modern": _p("nature_modern", ["#3B6EA8", "#5C946E", "#C46A3A", "#7566A0", "#8C8C8C", "#D6A03D"], "categorical", "curated-publication", ["nature", "paper", "muted", "soft", "high_impact", "categorical", "科研", "论文", "柔和"], "Muted Nature-like palette for multi-method figures.", True, True, 1.28),
    "nature_soft": _p("nature_soft", ["#4E79A7", "#86BCB6", "#F2B880", "#A0CBE8", "#B699C7", "#8CD17D"], "categorical", "curated-publication", ["nature", "soft", "elegant", "clean", "简洁", "大气", "柔和"], "Soft elegant palette for high-impact journal figures.", True, False, 1.18),
    "ieee_clean": _p("ieee_clean", ["#0B3C5D", "#328CC1", "#D9B310", "#1D2731", "#7A7A7A", "#B22222"], "categorical", "curated-publication", ["ieee", "trans", "engineering", "clean", "minimal", "blue", "gray", "严肃", "简洁"], "Restrained engineering palette.", False, True, 1.20),
    "minimal_blue_gray": _p("minimal_blue_gray", ["#1F4E79", "#6C8EBF", "#A6A6A6", "#D9D9D9", "#404040"], "categorical", "curated-publication", ["minimal", "clean", "simple", "blue", "gray", "简洁", "大气", "克制", "黑白"], "Conservative blue-gray palette.", True, True, 1.22),
    "okabe_ito": _p("okabe_ito", ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"], "categorical", "Okabe-Ito-style", ["colorblind", "safe", "categorical", "high_contrast", "色盲", "高对比", "多方法"], "Colorblind-safe categorical palette.", True, True, 1.35),
    "tol_bright": _p("tol_bright", ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"], "categorical", "Tol-style", ["colorblind", "bright", "categorical", "clean", "色盲", "高对比", "现代"], "Bright colorblind-safe categorical palette.", True, True, 1.30),
    "brewer_set2": _p("brewer_set2", ["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3", "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"], "categorical", "ColorBrewer-like", ["colorbrewer", "set2", "soft", "categorical", "qualitative", "柔和", "多方法"], "Soft qualitative palette.", False, False, 1.10),
    "cividis_sample": _p("cividis_sample", ["#00204C", "#263C6A", "#575D6D", "#7F7C75", "#A59C74", "#D9C55E", "#FFFFE0"], "sequential", "cividis-style", ["cividis", "scientific", "sequential", "heatmap", "colorblind", "print", "色盲", "热力图"], "CVD-optimized blue-yellow scientific palette.", True, True, 1.35),
    "viridis_sample": _p("viridis_sample", ["#440154", "#414487", "#2A788E", "#22A884", "#7AD151", "#FDE725"], "sequential", "Matplotlib scientific sample", ["viridis", "scientific", "sequential", "heatmap", "perceptual", "色盲", "热力图", "连续"], "Perceptually ordered scientific palette.", True, True, 1.30),
    "blue_sequential": _p("blue_sequential", ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C"], "sequential", "ColorBrewer-like", ["blue", "sequential", "heatmap", "clean", "minimal", "简洁", "连续"], "Clean blue sequential palette.", True, True, 1.15),
    "blue_orange_diverging": _p("blue_orange_diverging", ["#2166AC", "#67A9CF", "#D1E5F0", "#F7F7F7", "#FDDBC7", "#EF8A62", "#B2182B"], "diverging", "ColorBrewer-like", ["diverging", "blue", "orange", "red", "difference", "delta", "heatmap", "正负", "差异"], "Diverging palette for signed differences.", True, True, 1.25),
    "print_gray": _p("print_gray", ["#111111", "#404040", "#6F6F6F", "#9B9B9B", "#C8C8C8", "#E6E6E6"], "grayscale", "print-first", ["gray", "grayscale", "print", "minimal", "blackwhite", "黑白", "打印", "简洁"], "Grayscale print-first palette.", True, True, 1.22),
    "cool_accent": _p("cool_accent", ["#0F4D92", "#42949E", "#3775BA", "#9A4D8E", "#4D4D4D", "#CFCECE"], "categorical", "curated-publication", ["cool", "blue", "teal", "violet", "technology", "冷色", "科技", "简洁"], "Cool blue/teal/violet palette.", True, True, 1.15),
}

TOKEN_TAGS = {
    "简洁": ("minimal", "clean"), "大气": ("clean", "high_impact"), "柔和": ("soft", "muted"), "科研": ("paper", "scientific"), "论文": ("paper", "scientific"),
    "色盲": ("colorblind", "safe"), "黑白": ("grayscale", "print"), "打印": ("print", "grayscale"), "热力图": ("heatmap", "sequential"),
    "正负": ("diverging", "difference"), "差异": ("diverging", "difference"), "对比": ("categorical", "comparison"), "消融": ("categorical", "ablation"),
    "nature": ("nature", "muted", "soft"), "ieee": ("ieee", "engineering"), "minimal": ("minimal", "clean"), "clean": ("minimal", "clean"),
    "colorblind": ("colorblind", "safe"), "heatmap": ("heatmap", "sequential"), "diverging": ("diverging", "difference"), "print": ("print", "grayscale"),
    "bar": ("categorical",), "line": ("categorical",), "scatter": ("categorical",),
}
FIGURE_KIND = {"grouped_bar": "categorical", "bar": "categorical", "ablation": "categorical", "line": "categorical", "trend": "categorical", "scatter": "categorical", "heatmap": "sequential", "matrix": "sequential", "correlation": "diverging", "difference_heatmap": "diverging"}


def infer_kind(request: str = "", figure_type: str | None = None, data_role: str | None = None) -> str:
    if data_role in {"categorical", "sequential", "diverging", "grayscale"}:
        return data_role
    if figure_type and figure_type.lower() in FIGURE_KIND:
        return FIGURE_KIND[figure_type.lower()]
    r = request.lower()
    if any(x in r for x in ["正负", "差异", "delta", "difference", "correlation"]):
        return "diverging"
    if any(x in r for x in ["热力图", "heatmap", "continuous", "连续", "matrix"]):
        return "sequential"
    if any(x in r for x in ["黑白", "grayscale"]):
        return "grayscale"
    return "categorical"


def request_to_tags(request: str, figure_type: str | None = None, data_role: str | None = None) -> set[str]:
    tags = {infer_kind(request, figure_type, data_role)}
    tokens = re.findall(r"[a-zA-Z0-9_+\-/]+|[\u4e00-\u9fff]+", request.lower())
    tokens += [k for k in TOKEN_TAGS if any("\u4e00" <= ch <= "\u9fff" for ch in k) and k in request]
    for token in tokens:
        for key, mapped in TOKEN_TAGS.items():
            if token == key or key in token:
                tags.update(mapped)
    if figure_type:
        tags.add(figure_type.lower())
    return tags


def _score(candidate: PaletteCandidate, tags: set[str], kind: str, n_colors: int | None) -> float:
    score = 2.0 * len(tags & set(candidate.tags))
    if candidate.kind == kind:
        score += 4.0
    elif kind in {"sequential", "diverging"} and candidate.kind == "categorical":
        score -= 2.0
    if {"colorblind", "safe"} & tags:
        score += 3.0 if candidate.colorblind_safe else 0.0
    elif candidate.colorblind_safe:
        score += 0.7
    if {"print", "grayscale"} & tags:
        score += 3.0 if candidate.print_safe else 0.0
    elif candidate.print_safe:
        score += 0.4
    if n_colors and candidate.kind == "categorical":
        score += 1.0 if len(candidate.colors) >= n_colors else -0.7 * (n_colors - len(candidate.colors))
    return score * candidate.priority


def suggest_palettes(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6) -> list[PaletteCandidate]:
    kind = infer_kind(request, figure_type, data_role)
    tags = request_to_tags(request, figure_type, data_role)
    return sorted(PALETTE_REGISTRY.values(), key=lambda c: _score(c, tags, kind, n_colors), reverse=True)[:top_k]


def _roles(candidate: PaletteCandidate) -> dict[str, str]:
    colors = list(candidate.colors)
    if candidate.kind in {"sequential", "diverging", "grayscale"}:
        return {"low": colors[0], "mid": colors[len(colors) // 2], "high": colors[-1], "neutral": "#F7F7F7"}
    roles = ["proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "uncertainty"]
    return {role: colors[i % len(colors)] for i, role in enumerate(roles)}


def build_llm_palette_selection_prompt(request: str, figure_type: str | None, candidates: Sequence[PaletteCandidate], n_colors: int | None = None, extra_context: str | None = None) -> str:
    payload = {
        "user_style_request": request,
        "figure_type": figure_type,
        "n_colors": n_colors,
        "extra_context": extra_context or "",
        "rules": [
            "For categorical method comparison, prefer clear separation and colorblind safety.",
            "For heatmaps, prefer sequential palettes unless data is centered around zero.",
            "For signed differences/residuals, prefer diverging palettes.",
            "Prioritize scientific readability over decoration.",
            "Assign proposed/ours to the dominant but non-neon color.",
        ],
        "candidates": [c.as_dict() for c in candidates],
        "required_json_schema": {
            "selected_palette": "candidate name",
            "reason": "brief reason",
            "color_roles": {"proposed": "#hex", "baseline": "#hex", "secondary": "#hex", "ablation": "#hex", "neutral": "#hex", "highlight": "#hex"},
        },
    }
    return "Choose one publication-ready palette and return strict JSON only.\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def auto_palette(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6) -> PaletteSelection:
    candidates = suggest_palettes(request, figure_type, n_colors, data_role, top_k)
    selected = candidates[0]
    return PaletteSelection(selected.name, selected.colors, _roles(selected), f"Selected {selected.name} by deterministic request/tag scoring.", tuple(c.name for c in candidates), build_llm_palette_selection_prompt(request, figure_type, candidates, n_colors))


def apply_llm_palette_decision(decision: str | Mapping[str, Any], candidates: Sequence[PaletteCandidate]) -> PaletteSelection:
    obj = json.loads(decision) if isinstance(decision, str) else dict(decision)
    by_name = {c.name: c for c in candidates}
    name = str(obj.get("selected_palette", "")).strip()
    if name not in by_name:
        raise ValueError(f"Unknown palette {name!r}; available={sorted(by_name)}")
    candidate = by_name[name]
    roles = dict(obj.get("color_roles") or _roles(candidate))
    for color in roles.values():
        _validate_color(color)
    return PaletteSelection(candidate.name, candidate.colors, roles, str(obj.get("reason", "Selected by LLM decision.")), tuple(by_name), None)


def _validate_color(color: str) -> str:
    try:
        to_rgba(color)
    except ValueError as exc:
        raise ValueError(f"Invalid Matplotlib color: {color!r}") from exc
    return color


def resolve_palette(palette: Sequence[str] | str, n: int | None = None) -> list[str]:
    if isinstance(palette, str):
        colors = list(PALETTE_REGISTRY[palette].colors) if palette in PALETTE_REGISTRY else [palette]
    else:
        colors = list(palette)
    colors = [_validate_color(c) for c in colors]
    if not colors:
        raise ValueError("Palette is empty.")
    if n is None:
        return colors
    return [colors[i % len(colors)] for i in range(n)]


def resolve_colors(labels: Sequence[str], palette: Sequence[str] | str, color_roles: Mapping[str, str] | None = None) -> list[str]:
    color_roles = color_roles or {}
    colors = resolve_palette(palette, len(labels))
    result: list[str] = []
    for i, label in enumerate(labels):
        role_or_color = color_roles.get(str(label))
        if role_or_color:
            result.append(_validate_color(role_or_color))
        else:
            result.append(colors[i])
    return result


def apply_publication_style(style: FigureStyle | None = None) -> FigureStyle:
    style = style or FigureStyle()
    mpl.rcParams.update({
        "font.family": list(style.font_family),
        "font.size": style.font_size,
        "axes.linewidth": style.axes_linewidth,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "text.usetex": style.use_tex,
    })
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=resolve_palette(style.palette))
    return style


def dynamic_ylim(values: Sequence[float], margin_ratio: float = 0.08, lower: float | None = None, upper: float | None = None) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError("Cannot compute limits from empty or non-finite values.")
    vmin, vmax = float(arr.min()), float(arr.max())
    span = max(vmax - vmin, abs(vmax) * 0.05, 1e-9)
    return (vmin - span * margin_ratio if lower is None else lower, vmax + span * margin_ratio if upper is None else upper)


def make_grouped_bar(ax, categories: Sequence[str], series: Sequence[Sequence[float]], labels: Sequence[str], ylabel: str = "Value", colors: Sequence[str] | None = None, palette: Sequence[str] | str | None = None, color_roles: Mapping[str, str] | None = None, annotate: bool = False, fmt: str = "{:.2f}", edgecolor: str = "black", linewidth: float = 1.2, hatch: bool | Sequence[str] = False):
    categories = [str(x) for x in categories]
    labels = [str(x) for x in labels]
    data = np.asarray(series, dtype=float)
    if data.ndim != 2:
        raise ValueError(f"series must be 2D, got shape {data.shape}")
    if data.shape != (len(labels), len(categories)):
        raise ValueError(f"series shape {data.shape} must be (len(labels), len(categories)) = {(len(labels), len(categories))}")
    n_series, n_cat = data.shape
    x = np.arange(n_cat)
    width = min(0.8 / max(n_series, 1), 0.25)
    colors = list(colors) if colors is not None else resolve_colors(labels, palette or "nature_modern", color_roles)
    hatches = ["/", "\\", ".", "x", "-", "+", "o", "*"] if hatch is True else (list(hatch) if hatch else [""] * n_series)
    containers = []
    for i, (values, label) in enumerate(zip(data, labels)):
        offset = (i - (n_series - 1) / 2) * width
        bars = ax.bar(x + offset, values, width=width, label=label, color=colors[i % len(colors)], edgecolor=edgecolor, linewidth=linewidth, hatch=hatches[i % len(hatches)])
        containers.append(bars)
        if annotate:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(fmt.format(height), xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=max(8, int(mpl.rcParams["font.size"] * 0.7)))
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    return containers


def make_trend(ax, x: Sequence[float], y_series: Sequence[Sequence[float]], labels: Sequence[str], colors: Sequence[str] | None = None, palette: Sequence[str] | str | None = None, color_roles: Mapping[str, str] | None = None, ylabel: str | None = None, xlabel: str | None = None, uncertainty: Sequence[Sequence[float]] | None = None, linewidth: float = 2.5):
    x_arr = np.asarray(x, dtype=float)
    ys = [np.asarray(y, dtype=float) for y in y_series]
    if len(ys) != len(labels):
        raise ValueError("Number of y_series must equal number of labels.")
    for idx, y in enumerate(ys):
        if y.shape != x_arr.shape:
            raise ValueError(f"y_series[{idx}] shape {y.shape} must match x shape {x_arr.shape}")
    colors = list(colors) if colors is not None else resolve_colors(labels, palette or "nature_modern", color_roles)
    unc = [np.asarray(u, dtype=float) for u in uncertainty] if uncertainty is not None else None
    for i, (y, label) in enumerate(zip(ys, labels)):
        color = colors[i % len(colors)]
        ax.plot(x_arr, y, label=label, color=color, linewidth=linewidth)
        if unc is not None:
            ax.fill_between(x_arr, y - unc[i], y + unc[i], color=color, alpha=0.18, linewidth=0)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)


def make_heatmap(ax, matrix: Sequence[Sequence[float]], x_labels: Sequence[str] | None = None, y_labels: Sequence[str] | None = None, cmap: str | LinearSegmentedColormap | None = None, palette: Sequence[str] | str | None = None, cbar_label: str | None = None, annotate: bool = False, fmt: str = ".2f"):
    mat = np.asarray(matrix, dtype=float)
    if mat.ndim != 2:
        raise ValueError(f"matrix must be 2D, got shape {mat.shape}")
    if cmap is None:
        cmap = LinearSegmentedColormap.from_list("skill_heatmap", resolve_palette(palette or "viridis_sample"))
    im = ax.imshow(mat, cmap=cmap, aspect="auto")
    if x_labels is not None:
        ax.set_xticks(np.arange(mat.shape[1]))
        ax.set_xticklabels(x_labels, rotation=45, ha="right")
    if y_labels is not None:
        ax.set_yticks(np.arange(mat.shape[0]))
        ax.set_yticklabels(y_labels)
    cbar = ax.figure.colorbar(im, ax=ax)
    if cbar_label:
        cbar.set_label(cbar_label)
    if annotate:
        threshold = np.nanmean(mat)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                color = "white" if mat[i, j] > threshold else "black"
                ax.text(j, i, format(mat[i, j], fmt), ha="center", va="center", color=color)
    return im


def finalize_figure(fig, out_path: str | Path, formats: Sequence[str] | None = None, dpi: int = 300, close: bool = True, pad: float = 0.05) -> list[Path]:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stem = out_path.with_suffix("") if out_path.suffix else out_path
    formats = list(formats) if formats is not None else ([out_path.suffix.lstrip(".")] if out_path.suffix else ["png", "pdf"])
    fig.tight_layout(pad=2)
    saved: list[Path] = []
    for fmt in formats:
        path = stem.with_suffix(f".{fmt.lower().lstrip('.')}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=pad, facecolor="white")
        saved.append(path)
    if close:
        plt.close(fig)
    return saved
