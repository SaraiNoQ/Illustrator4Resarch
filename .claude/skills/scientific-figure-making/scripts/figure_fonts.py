"""Standalone publication-safe font stacks for figure scripts."""
from __future__ import annotations

import re
from typing import Any

try:
    from matplotlib import font_manager
except Exception:  # pragma: no cover - standalone metadata use without Matplotlib
    font_manager = None

PUBLICATION_FONT_REGISTRY = {
    "arial": ("Arial", "Helvetica", "Liberation Sans", "DejaVu Sans", "sans-serif"),
    "helvetica": ("Helvetica", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif"),
    "source_sans": ("Source Sans 3", "Source Sans Pro", "Noto Sans", "Arial", "DejaVu Sans", "sans-serif"),
    "noto_sans": ("Noto Sans", "Noto Sans CJK SC", "Noto Sans CJK JP", "Arial Unicode MS", "DejaVu Sans", "sans-serif"),
    "trebuchet_sans": ("Trebuchet MS", "Verdana", "Arial", "Helvetica", "DejaVu Sans", "sans-serif"),
    "verdana": ("Verdana", "Arial", "Helvetica", "DejaVu Sans", "sans-serif"),
    "times": ("Times New Roman", "Times", "Nimbus Roman", "serif"),
    "stix": ("STIX Two Text", "STIXGeneral", "Times New Roman", "serif"),
}

_FONT_TAGS = {
    "arial": {"formal", "journal", "conference", "clean", "ieee", "acm", "safe", "sans_serif"},
    "helvetica": {"formal", "journal", "nature", "science", "clean", "safe", "sans_serif"},
    "source_sans": {"modern", "ml", "neurips", "icml", "iclr", "safe", "sans_serif"},
    "noto_sans": {"unicode", "cjk", "chinese", "japanese", "safe", "sans_serif"},
    "trebuchet_sans": {"handdrawn", "cartoon", "anime", "cute", "playful", "rounded", "sans_serif"},
    "verdana": {"readable", "large", "slides", "cute", "rounded", "sans_serif"},
    "times": {"serif", "traditional", "times"},
    "stix": {"serif", "math", "latex"},
}

_CUES = {
    "二次元": {"anime", "cute", "playful"}, "可爱": {"cute", "rounded", "playful"},
    "手绘": {"handdrawn", "rounded", "playful"}, "卡通": {"cartoon", "rounded", "playful"},
    "anime": {"anime", "cute", "playful"}, "kawaii": {"cute", "rounded", "playful"},
    "cartoon": {"cartoon", "playful"}, "handdrawn": {"handdrawn", "playful"}, "xkcd": {"handdrawn", "playful"},
    "nature": {"nature", "journal"}, "ieee": {"ieee", "formal"}, "acm": {"acm", "conference"},
    "neurips": {"neurips", "ml", "modern"}, "icml": {"icml", "ml", "modern"}, "iclr": {"iclr", "ml", "modern"},
    "中文": {"cjk", "chinese", "unicode"}, "日文": {"cjk", "japanese", "unicode"},
    "times": {"times", "serif"}, "serif": {"serif"}, "衬线": {"serif"},
    "非衬线": {"safe", "sans_serif"}, "sans": {"safe", "sans_serif"},
}


def _tokens(text: str | None) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_+\-/]+|[\u4e00-\u9fff]+", (text or "").lower())


def infer_font_tags(request: str | None = None, chart_style: Any | None = None, venue: str | None = None) -> set[str]:
    text = " ".join(x for x in (request or "", venue or "") if x)
    lowered = text.lower()
    explicit_sans = any(
        cue in lowered
        for cue in ("sans-serif", "sans serif", "sans_serif", "非衬线")
    )
    tags: set[str] = set()
    for key, mapped in _CUES.items():
        if key in {"serif", "衬线"} and explicit_sans:
            continue
        if key in lowered:
            tags.update(mapped)
    for token in _tokens(text):
        tags.update(_CUES.get(token, set()))
    name = chart_style if isinstance(chart_style, str) else getattr(chart_style, "name", "")
    name = str(name).lower()
    tags.update(_tokens(name))
    if getattr(chart_style, "use_xkcd", False) or name == "cartoon_handdrawn":
        tags.update({"handdrawn", "cartoon", "playful", "rounded", "sans_serif"})
    if name in {"nature_journal", "ieee_transactions", "acm_conference", "neurips_ml", "publication_minimal"}:
        tags.update({"journal", "conference", "formal", "sans_serif"})
    if not tags:
        tags.update({"formal", "journal", "safe", "sans_serif"})
    if explicit_sans or tags & {"handdrawn", "cartoon", "anime", "cute", "playful"}:
        tags.add("sans_serif")
        tags.discard("serif")
    return tags


def suggest_fonts(request: str | None = None, chart_style: Any | None = None, venue: str | None = None, top_k: int = 5) -> list[str]:
    tags = infer_font_tags(request, chart_style, venue)
    def score(name: str) -> float:
        s = len(tags & _FONT_TAGS[name])
        if name in {"times", "stix"} and tags & {"handdrawn", "cartoon", "anime", "cute", "playful"}:
            s -= 10
        if name in {"times", "stix"} and "sans_serif" in tags:
            s -= 10
        if name not in {"times", "stix"} and "sans_serif" in tags:
            s += 3
        if name not in {"times", "stix"} and "serif" not in tags:
            s += 2
        return s
    return sorted(PUBLICATION_FONT_REGISTRY, key=score, reverse=True)[:top_k]


def available_font_names() -> set[str]:
    if font_manager is None:
        return set()
    try:
        return {font.name for font in font_manager.fontManager.ttflist}
    except Exception:
        return set()


def available_font_family(family: tuple[str, ...]) -> tuple[str, ...]:
    """Avoid Matplotlib warnings for every unavailable fallback candidate."""
    available = available_font_names()
    if not available:
        return family
    generic = {"serif", "sans-serif", "cursive", "fantasy", "monospace"}
    filtered = tuple(name for name in family if name in available or name in generic)
    return filtered or family


def select_font_family(request: str | None = None, chart_style: Any | None = None, venue: str | None = None, preferred: str | None = None) -> tuple[str, ...]:
    key = preferred or suggest_fonts(request, chart_style, venue, 1)[0]
    if key not in PUBLICATION_FONT_REGISTRY:
        raise ValueError(f"Unknown publication font {key!r}; available={sorted(PUBLICATION_FONT_REGISTRY)}")
    return available_font_family(PUBLICATION_FONT_REGISTRY[key])
