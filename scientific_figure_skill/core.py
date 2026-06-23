"""Scientific figure helpers with automatic palette selection."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import json, re
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


@dataclass(frozen=True)
class PaletteSelection:
    name: str
    colors: tuple[str, ...]
    color_roles: dict[str, str]
    reason: str
    candidates: tuple[str, ...]
    llm_prompt: str | None = None


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
    for t in tokens:
        for k, mapped in TOKEN_TAGS.items():
            if t == k or k in t:
                tags.update(mapped)
    if figure_type:
        tags.add(figure_type.lower())
    return tags


def _score(c: PaletteCandidate, tags: set[str], kind: str, n_colors: int | None) -> float:
    s = 2.0 * len(tags & set(c.tags))
    s += 4.0 if c.kind == kind else (-2.0 if kind in {"sequential", "diverging"} and c.kind == "categorical" else 0.0)
    s += 3.0 if ({"colorblind", "safe"} & tags) and c.colorblind_safe else 0.7 if c.colorblind_safe else 0.0
    s += 3.0 if ({"print", "grayscale"} & tags) and c.print_safe else 0.4 if c.print_safe else 0.0
    if n_colors and c.kind == "categorical":
        s += 1.0 if len(c.colors) >= n_colors else -0.7 * (n_colors - len(c.colors))
    return s * c.priority


def suggest_palettes(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6) -> list[PaletteCandidate]:
    kind = infer_kind(request, figure_type, data_role)
    tags = request_to_tags(request, figure_type, data_role)
    return sorted(PALETTE_REGISTRY.values(), key=lambda c: _score(c, tags, kind, n_colors), reverse=True)[:top_k]


def _roles(c: PaletteCandidate) -> dict[str, str]:
    colors = list(c.colors)
    if c.kind in {"sequential", "diverging", "grayscale"}:
        return {"low": colors[0], "mid": colors[len(colors) // 2], "high": colors[-1], "neutral": "#F7F7F7"}
    roles = ["proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "uncertainty"]
    return {r: colors[i % len(colors)] for i, r in enumerate(roles)}


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
        "required_json_schema": {"selected_palette": "candidate name", "reason": "brief reason", "color_roles": {"proposed": "#hex", "baseline": "#hex", "secondary": "#hex", "ablation": "#hex", "neutral": "#hex", "highlight": "#hex"}},
    }
    return "Choose one publication-ready palette and return strict JSON only.\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def auto_palette(request: str, figure_type: str | None = None, n_colors: int | None = None, data_role: str | None = None, top_k: int = 6) -> PaletteSelection:
    cands = suggest_palettes(request, figure_type, n_colors, data_role, top_k)
    sel = cands[0]
    return PaletteSelection(sel.name, sel.colors, _roles(sel), f"Selected {sel.name} by deterministic request/tag scoring.", tuple(c.name for c in cands), build_llm_palette_selection_prompt(request, figure_type, cands, n_colors))


def apply_llm_palette_decision(decision: str | Mapping[str, Any], candidates: Sequence[PaletteCandidate]) -> PaletteSelection:
    obj = json.loads(decision) if isinstance(decision, str) else dict(decision)
    names = {c.name: c for c in candidates}
    name = str(obj.get("selected_palette", "")).strip()
    if name not in names:
        raise ValueError(f"Unknown palette {name!r}; available={sorted(names)}")
    c = names[name]
    roles = obj.get("color_roles") or _roles(c)
    if not isinstance(roles, Mapping):
        raise ValueError("color_roles must be an object")
    return PaletteSelection(name, c.colors, {str(k): str(v) for k, v in roles.items()}, str(obj.get("reason", "LLM selected palette.")), tuple(names))


@dataclass(frozen=True)
class FigureStyle:
    font_size: int = 16
    axes_linewidth: float = 2.5
    palette: str | Sequence[str] | Mapping[str, str] = "nature_modern"
    color_roles: Mapping[str, str] | None = None
    dpi: int = 300
    font_family: tuple[str, ...] = ("Arial", "Helvetica", "DejaVu Sans", "sans-serif")


ROLE_ORDER = ("proposed", "baseline", "secondary", "ablation", "neutral", "highlight", "improvement", "uncertainty")


def _valid(color: str) -> str:
    to_rgba(color)
    return color


def resolve_palette(palette: str | Sequence[str] | Mapping[str, str] = "nature_modern", n: int | None = None) -> list[str]:
    if isinstance(palette, str):
        if palette in PALETTE_REGISTRY:
            colors = list(PALETTE_REGISTRY[palette].colors)
        elif palette.startswith("#"):
            colors = [palette]
        else:
            raise ValueError(f"Unknown palette {palette!r}")
    elif isinstance(palette, Mapping):
        colors = [palette[k] for k in ROLE_ORDER if k in palette] + [v for k, v in palette.items() if k not in ROLE_ORDER]
    else:
        colors = list(palette)
    colors = [_valid(c) for c in colors]
    if n is None:
        return colors
    return [colors[i % len(colors)] for i in range(n)]


def _palette_dict(palette) -> dict[str, str]:
    colors = resolve_palette(palette)
    return {role: colors[i % len(colors)] for i, role in enumerate(ROLE_ORDER)}


def resolve_colors(labels: Sequence[str], palette="nature_modern", color_roles: Mapping[str, str] | None = None) -> list[str]:
    pd = _palette_dict(palette)
    cyc = resolve_palette(palette, len(labels))
    out = []
    for i, label in enumerate(map(str, labels)):
        role = (color_roles or {}).get(label)
        out.append(_valid(role) if role and role.startswith("#") else pd.get(role, cyc[i]) if role else cyc[i])
    return out


def apply_publication_style(style: FigureStyle | None = None) -> FigureStyle:
    style = style or FigureStyle()
    mpl.rcParams.update({"font.family": list(style.font_family), "font.size": style.font_size, "axes.linewidth": style.axes_linewidth, "axes.spines.right": False, "axes.spines.top": False, "legend.frameon": False, "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42})
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=resolve_palette(style.palette))
    return style


def make_cmap(palette="nature_modern", name="custom_cmap"):
    colors = resolve_palette(palette)
    return LinearSegmentedColormap.from_list(name, colors if len(colors) > 1 else ["#FFFFFF", colors[0]])


def finalize_figure(fig, out_path: str | Path, formats: Sequence[str] = ("png", "pdf"), dpi: int = 300) -> list[Path]:
    stem = Path(out_path)
    stem.parent.mkdir(parents=True, exist_ok=True)
    if stem.suffix:
        stem = stem.with_suffix("")
    fig.tight_layout(pad=2)
    paths = []
    for fmt in formats:
        p = stem.with_suffix("." + fmt.lstrip("."))
        fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.05, facecolor="white")
        paths.append(p)
    plt.close(fig)
    return paths


def dynamic_ylim(values, margin_ratio=0.08, lower=None, upper=None):
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    lo, hi = float(arr.min()), float(arr.max())
    span = max(hi - lo, abs(hi) * 0.05, 1e-9)
    return (lo - span * margin_ratio if lower is None else lower, hi + span * margin_ratio if upper is None else upper)


def make_grouped_bar(ax, categories, series, labels, ylabel="Value", palette="nature_modern", color_roles=None, annotate=False, hatch=False):
    data = np.asarray(series, dtype=float)
    if data.ndim != 2:
        raise ValueError("series must be 2D with shape [num_series, num_categories]")
    if data.shape != (len(labels), len(categories)):
        raise ValueError(f"shape mismatch: series={data.shape}, labels={len(labels)}, categories={len(categories)}")
    x = np.arange(len(categories))
    width = min(0.8 / max(len(labels), 1), 0.25)
    colors = resolve_colors(labels, palette, color_roles)
    hatches = ["/", "\\", ".", "x", "-", "+", "o", "*"] if hatch else [""]
    for i, (vals, label) in enumerate(zip(data, labels)):
        bars = ax.bar(x + (i - (len(labels) - 1) / 2) * width, vals, width=width, label=label, color=colors[i], edgecolor="black", linewidth=1.2, hatch=hatches[i % len(hatches)])
        if annotate:
            for b in bars:
                ax.annotate(f"{b.get_height():.2f}", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=max(8, mpl.rcParams["font.size"] * 0.65))
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    return ax
