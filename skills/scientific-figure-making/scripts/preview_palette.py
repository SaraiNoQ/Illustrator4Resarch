#!/usr/bin/env python3
"""Preview palette and chart-style candidates for a scientific figure request."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from figure_design import auto_figure_design, suggest_palettes, resolve_chart_style
except ImportError:
    # Repository-development fallback. A globally installed skill should not need this.
    for path in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (path / "scientific_figure_skill").is_dir():
            sys.path.insert(0, str(path))
            break
    else:
        raise RuntimeError(
            "Could not import figure_design.py or scientific_figure_skill. "
            "Check that this script is inside scientific-figure-making/scripts/."
        )
    from scientific_figure_skill import auto_figure_design, suggest_palettes, resolve_chart_style  # type: ignore  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview scientific figure palette and chart-style selection.")
    parser.add_argument("request", nargs="?", default="简洁大气，Nature科研风格", help="Natural-language style request")
    parser.add_argument("--figure-type", default="grouped_bar", help="Figure type, e.g. grouped_bar, heatmap, line")
    parser.add_argument("--n-colors", type=int, default=5, help="Number of distinct colors needed")
    parser.add_argument("--venue", default=None, help="Optional venue/journal/conference hint, e.g. nature, ieee, neurips")
    parser.add_argument("--top-k", type=int, default=6, help="Number of palette candidates to print")
    args = parser.parse_args()

    candidates = suggest_palettes(args.request, figure_type=args.figure_type, n_colors=args.n_colors, top_k=args.top_k, venue=args.venue)
    design = auto_figure_design(args.request, figure_type=args.figure_type, n_colors=args.n_colors, venue=args.venue)
    chart_style = resolve_chart_style(args.request, venue=args.venue, figure_type=args.figure_type)

    print("Selected palette:", design.palette.name)
    print("Colors:", ", ".join(design.palette.colors))
    print("Roles:", design.palette.color_roles)
    print("Palette reason:", design.palette.reason)
    print("\nSelected chart style:", chart_style.name)
    print("Chart style:", chart_style.description)
    print("\nPalette candidates:")
    for idx, candidate in enumerate(candidates, start=1):
        generated = " generated" if getattr(candidate, "generated", False) else ""
        print(f"{idx}. {candidate.name}{generated}: {', '.join(candidate.colors)} | {candidate.description}")


if __name__ == "__main__":
    main()
