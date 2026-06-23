#!/usr/bin/env python3
"""Preview palette candidates for a natural-language scientific figure style request."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def find_repo_root(start: Path) -> Path:
    """Find the repository root from any copied skill discovery path."""
    for path in [start, *start.parents]:
        if (path / "scientific_figure_skill").is_dir():
            return path
    raise RuntimeError(
        "Could not find repository root containing scientific_figure_skill/. "
        "Run this script inside the Illustrator4Resarch repository."
    )


ROOT = find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scientific_figure_skill import auto_palette, suggest_palettes  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview Illustrator4Resarch palette selection.")
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
    for idx, c in enumerate(candidates, start=1):
        print(f"{idx}. {c.name}: {', '.join(c.colors)} | {c.description}")


if __name__ == "__main__":
    main()
