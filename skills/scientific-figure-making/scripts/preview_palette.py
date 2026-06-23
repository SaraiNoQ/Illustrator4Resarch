#!/usr/bin/env python3
"""Preview palette candidates for a natural-language scientific figure style request.

This script works both inside the Illustrator4Resarch repository and when the
skill is copied to a global agent skill directory.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from figure_toolkit import auto_palette, suggest_palettes
except ImportError:
    # Repository-development fallback. A globally installed skill should not need this.
    for path in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (path / "scientific_figure_skill").is_dir():
            sys.path.insert(0, str(path))
            break
    else:
        raise RuntimeError(
            "Could not import figure_toolkit.py or scientific_figure_skill. "
            "Check that this script is inside scientific-figure-making/scripts/."
        )
    from scientific_figure_skill import auto_palette, suggest_palettes  # type: ignore  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview scientific figure palette selection.")
    parser.add_argument("request", nargs="?", default="简洁大气，Nature科研风格", help="Natural-language style request")
    parser.add_argument("--figure-type", default="grouped_bar", help="Figure type, e.g. grouped_bar, heatmap, line")
    parser.add_argument("--n-colors", type=int, default=5, help="Number of distinct colors needed")
    parser.add_argument("--top-k", type=int, default=6, help="Number of candidates to print")
    args = parser.parse_args()

    candidates = suggest_palettes(args.request, figure_type=args.figure_type, n_colors=args.n_colors, top_k=args.top_k)
    selection = auto_palette(args.request, figure_type=args.figure_type, n_colors=args.n_colors, top_k=args.top_k)

    print("Selected:", selection.name)
    print("Colors:", ", ".join(selection.colors))
    print("Roles:", selection.color_roles)
    print("\nCandidates:")
    for idx, candidate in enumerate(candidates, start=1):
        print(f"{idx}. {candidate.name}: {', '.join(candidate.colors)} | {candidate.description}")


if __name__ == "__main__":
    main()
