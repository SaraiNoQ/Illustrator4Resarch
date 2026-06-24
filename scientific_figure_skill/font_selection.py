"""Publication-safe font selection for scientific figure styles.

The registry intentionally contains only common fonts that are acceptable in
journal/conference figures when embedded in PDF/SVG output.  Playful styles are
handled by choosing rounded or humanist sans-serif stacks from this safe set,
not by using decorative comic fonts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence
import json
import re

try:
    from matplotlib import font_manager
except Exception:  # pragma: no cover - matplotlib may be unavailable in docs-only use
    font_manager = None  # type: ignore[assignment]


@dataclass(frozen=True)
class FontCandidate:
    name: str
    family: tuple[str, ...]
    category: str
    tags: tuple[str, ...]
    aliases: tuple[str, ...]
    description: str
    priority: float = 1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "family": list(self.family),
            "category": self.category,
            "tags": list(self.tags),
            "aliases": list(self.aliases),
            "description": self.description,
            "priority": self.priority,
        }


def _f(
    name: str,
    family: Sequence[str],
    category: str,
    tags: Sequence[str],
    aliases: Sequence[str] = (),
    description: str = "",
    priority: float = 1.0,
) -> FontCandidate:
    return FontCandidate(
        name=name,
        family=tuple(family),
        category=category,
        tags=tuple(sorted(set(tags))),
        aliases=tuple(aliases),
        description=description,
        priority=priority,
    )


PUBLICATION_FONT_REGISTRY: dict[str, FontCandidate] = {
    "arial": _f(
        "arial",
        ("Arial", "Helvetica", "Liberation Sans", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("journal", "conference", "formal", "clean", "compact", "nature", "ieee", "acm", "neurips", "icml", "safe", "论文", "简洁"),
        ("default_sans", "journal_sans"),
        "Default publication-safe sans-serif stack for most journal and conference plots.",
        1.30,
    ),
    "helvetica": _f(
        "helvetica",
        ("Helvetica", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("journal", "nature", "science", "cell", "clean", "minimal", "compact", "safe", "科研"),
        ("nature_sans", "clean_sans"),
        "Compact high-impact-journal sans-serif stack.",
        1.24,
    ),
    "source_sans": _f(
        "source_sans",
        ("Source Sans 3", "Source Sans Pro", "Noto Sans", "Arial", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("modern", "ml", "neurips", "icml", "iclr", "slides", "clean", "safe", "现代"),
        ("source_sans_3", "source_sans_pro"),
        "Modern open-source sans-serif stack for ML conference and report figures.",
        1.12,
    ),
    "noto_sans": _f(
        "noto_sans",
        ("Noto Sans", "Noto Sans CJK SC", "Noto Sans CJK JP", "Arial Unicode MS", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("unicode", "cjk", "multilingual", "chinese", "japanese", "safe", "中文", "日文"),
        ("cjk_sans", "unicode_sans"),
        "Unicode/CJK-capable sans-serif fallback stack for multilingual labels.",
        1.08,
    ),
    "trebuchet_sans": _f(
        "trebuchet_sans",
        ("Trebuchet MS", "Verdana", "Arial", "Helvetica", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("handdrawn", "cartoon", "anime", "cute", "playful", "rounded", "informal", "手绘", "卡通", "二次元", "可爱"),
        ("playful_sans", "anime_sans", "cartoon_sans"),
        "Readable rounded/humanist sans-serif stack for hand-drawn or anime-like charts without decorative fonts.",
        1.05,
    ),
    "verdana": _f(
        "verdana",
        ("Verdana", "Arial", "Helvetica", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("readable", "large", "slides", "presentation", "cute", "rounded", "答辩"),
        ("wide_sans",),
        "Wide readable sans-serif stack for slides and dense labels.",
        0.98,
    ),
    "cmu_sans": _f(
        "cmu_sans",
        ("CMU Sans Serif", "Computer Modern Sans Serif", "DejaVu Sans", "sans-serif"),
        "sans_serif",
        ("latex", "math", "academic", "clean", "safe"),
        ("computer_modern_sans",),
        "LaTeX-compatible sans-serif stack for math-heavy figures.",
        0.94,
    ),
    "times": _f(
        "times",
        ("Times New Roman", "Times", "Nimbus Roman", "serif"),
        "serif",
        ("serif", "traditional", "formal", "paper", "legacy", "times"),
        ("times_new_roman",),
        "Traditional serif stack. Avoid for cartoon, anime, and hand-drawn styles.",
        0.82,
    ),
    "stix": _f(
        "stix",
        ("STIX Two Text", "STIXGeneral", "Times New Roman", "serif"),
        "serif",
        ("serif", "math", "latex", "traditional", "safe"),
        ("stix_two", "stixgeneral"),
        "Math-friendly serif stack for conservative manuscript figures.",
        0.86,
    ),
}

FONT_TEXT_CUES: dict[str, tuple[str, ...]] = {
    "二次元": ("anime", "playful", "cute", "sans_serif"),
    "可爱": ("cute", "rounded", "playful", "sans_serif"),
    "手绘": ("handdrawn", "rounded", "playful", "sans_serif"),
    "卡通": ("cartoon", "rounded", "playful", "sans_serif"),
    "anime": ("anime", "playful", "cute", "sans_serif"),
    "kawaii": ("cute", "rounded", "playful", "sans_serif"),
    "cartoon": ("cartoon", "playful", "sans_serif"),
    "handdrawn": ("handdrawn", "playful", "sans_serif"),
    "xkcd": ("handdrawn", "playful", "sans_serif"),
    "nature": ("nature", "journal", "sans_serif"),
    "science": ("science", "journal", "sans_serif"),
    "cell": ("cell", "journal", "sans_serif"),
    "ieee": ("ieee", "compact", "sans_serif"),
    "acm": ("acm", "conference", "sans_serif"),
    "neurips": ("neurips", "ml", "modern", "sans_serif"),
    "icml": ("icml", "ml", "modern", "sans_serif"),
    "iclr": ("iclr", "ml", "modern", "sans_serif"),
    "现代": ("modern", "sans_serif"),
    "简洁": ("clean", "sans_serif"),
    "紧凑": ("compact", "sans_serif"),
    "中文": ("cjk", "unicode", "sans_serif"),
    "日文": ("cjk", "unicode", "sans_serif"),
    "times": ("times", "serif"),
    "serif": ("serif",),
    "衬线": ("serif",),
    "非衬线": ("sans_serif",),
    "sans": ("sans_serif",),
}

SERIF_CATEGORIES = {"serif"}
DEFAULT_FONT_STACKS = {
    ("Arial", "Helvetica", "DejaVu Sans", "sans-serif"),
    ("Arial", "Helvetica", "Liberation Sans", "DejaVu Sans", "sans-serif"),
    ("Times New Roman", "Times", "serif"),
    ("Times New Roman", "serif"),
}


def _tokens(text: str | None) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_+\-/]+|[\u4e00-\u9fff]+", (text or "").lower())


def _chart_style_name(chart_style: Any | None) -> str:
    if chart_style is None:
        return ""
    if isinstance(chart_style, str):
        return chart_style.lower()
    return str(getattr(chart_style, "name", "") or "").lower()


def _style_tags(chart_style: Any | None) -> set[str]:
    name = _chart_style_name(chart_style)
    tags = set(str(t).lower() for t in getattr(chart_style, "tags", ()) or ())
    tags.update(_tokens(name))
    if getattr(chart_style, "use_xkcd", False) or name == "cartoon_handdrawn":
        tags.update({"handdrawn", "cartoon", "playful", "rounded", "sans_serif"})
    if name in {"nature_journal", "ieee_transactions", "acm_conference", "neurips_ml", "publication_minimal"}:
        tags.update({"journal", "conference", "formal", "sans_serif"})
    return tags


def infer_font_tags(request: str | None = None, chart_style: Any | None = None, venue: str | None = None) -> set[str]:
    tags: set[str] = set()
    text = " ".join(x for x in (request or "", venue or "") if x)
    lowered = text.lower()
    for key, mapped in FONT_TEXT_CUES.items():
        if key in lowered:
            tags.update(mapped)
    for token in _tokens(text):
        if token in FONT_TEXT_CUES:
            tags.update(FONT_TEXT_CUES[token])
    tags.update(_style_tags(chart_style))
    if not tags:
        tags.update({"journal", "conference", "clean", "sans_serif"})
    if {"handdrawn", "cartoon", "anime", "cute", "playful"} & tags:
        tags.add("sans_serif")
        tags.discard("serif")
    return tags


def available_font_names() -> set[str]:
    if font_manager is None:
        return set()
    try:
        return {f.name for f in font_manager.fontManager.ttflist}
    except Exception:
        return set()


def _score_font(candidate: FontCandidate, tags: set[str], available: set[str]) -> float:
    score = 2.0 * candidate.priority + 1.5 * len(tags & set(candidate.tags))
    if candidate.category == "sans_serif" and "sans_serif" in tags:
        score += 3.0
    if candidate.category in SERIF_CATEGORIES and "serif" in tags:
        score += 2.5
    if candidate.category in SERIF_CATEGORIES and ({"handdrawn", "cartoon", "anime", "cute", "playful"} & tags):
        score -= 8.0
    if candidate.family and candidate.family[0] in available:
        score += 0.45
    elif any(f in available for f in candidate.family[1:-1]):
        score += 0.20
    return score


def suggest_fonts(
    request: str | None = None,
    chart_style: Any | None = None,
    venue: str | None = None,
    top_k: int = 5,
) -> list[FontCandidate]:
    tags = infer_font_tags(request, chart_style, venue)
    available = available_font_names()
    return sorted(PUBLICATION_FONT_REGISTRY.values(), key=lambda c: _score_font(c, tags, available), reverse=True)[:top_k]


def select_font_candidate(
    request: str | None = None,
    chart_style: Any | None = None,
    venue: str | None = None,
    preferred: str | None = None,
) -> FontCandidate:
    if preferred:
        key = preferred.lower().replace("-", "_").replace(" ", "_")
        for candidate in PUBLICATION_FONT_REGISTRY.values():
            names = {candidate.name, *candidate.aliases}
            if key in {n.lower().replace("-", "_").replace(" ", "_") for n in names}:
                return candidate
        raise ValueError(f"Unknown publication font {preferred!r}; available={sorted(PUBLICATION_FONT_REGISTRY)}")
    return suggest_fonts(request=request, chart_style=chart_style, venue=venue, top_k=1)[0]


def select_font_family(
    request: str | None = None,
    chart_style: Any | None = None,
    venue: str | None = None,
    preferred: str | None = None,
) -> tuple[str, ...]:
    return select_font_candidate(request=request, chart_style=chart_style, venue=venue, preferred=preferred).family


def should_auto_replace_font(font_family: Sequence[str] | None) -> bool:
    if not font_family:
        return True
    family = tuple(str(f) for f in font_family)
    if family in DEFAULT_FONT_STACKS:
        return True
    lowered = {f.lower() for f in family}
    return bool({"times new roman", "times", "serif"} & lowered) and not bool({"arial", "helvetica", "sans-serif", "dejavu sans"} & lowered)


def build_llm_font_selection_prompt(
    request: str,
    chart_style: Any | None = None,
    venue: str | None = None,
    candidates: Sequence[FontCandidate] | None = None,
) -> str:
    ranked = list(candidates) if candidates else suggest_fonts(request, chart_style, venue, top_k=5)
    payload = {
        "user_style_request": request,
        "chart_style": _chart_style_name(chart_style),
        "venue": venue,
        "inferred_tags": sorted(infer_font_tags(request, chart_style, venue)),
        "rules": [
            "Use only fonts from the provided publication-safe registry.",
            "For cartoon, hand-drawn, anime, or cute chart styles, choose a sans-serif stack, never Times New Roman or another serif font.",
            "Prefer Arial/Helvetica-like stacks for formal journal and conference figures.",
            "Prefer CJK-capable sans-serif stacks when labels contain Chinese or Japanese text.",
            "Do not choose decorative novelty fonts; playful styles should still remain readable and embeddable.",
        ],
        "candidates": [c.as_dict() for c in ranked],
        "required_json_schema": {"selected_font": "candidate name", "reason": "brief reason"},
    }
    return "Choose one publication-safe font stack and return strict JSON only.\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)
