#!/usr/bin/env python3
"""Create an original-plus-grayscale review sheet for visual figure QA."""
from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np


def _rgb(image: np.ndarray) -> np.ndarray:
    array = np.asarray(image, dtype=float)
    if array.max(initial=0.0) > 1.0:
        array = array / 255.0
    if array.ndim == 2:
        return np.repeat(array[..., None], 3, axis=2)
    if array.ndim != 3 or array.shape[2] not in {3, 4}:
        raise ValueError(f"unsupported image shape {array.shape}")
    rgb = array[..., :3]
    if array.shape[2] == 4:
        alpha = np.clip(array[..., 3:4], 0.0, 1.0)
        rgb = rgb * alpha + (1.0 - alpha)
    return np.clip(rgb, 0.0, 1.0)


def _grayscale(rgb: np.ndarray) -> np.ndarray:
    return (
        0.2126 * rgb[..., 0]
        + 0.7152 * rgb[..., 1]
        + 0.0722 * rgb[..., 2]
    )


def create_review_sheet(
    inputs: Sequence[str | Path],
    output: str | Path,
    *,
    include_grayscale: bool = False,
    title: str = "Scientific figure visual review",
) -> Path:
    """Render source figures in a consistent visual-review sheet."""
    input_paths = [Path(path) for path in inputs]
    if not input_paths:
        raise ValueError("at least one input image is required")
    images = []
    for path in input_paths:
        if not path.is_file():
            raise FileNotFoundError(f"missing input image: {path}")
        images.append((path, _rgb(mpimg.imread(path))))

    columns = 2 if include_grayscale else 1
    rows = len(images)
    max_aspect = max(image.shape[1] / image.shape[0] for _, image in images)
    panel_width = min(10.0, max(5.0, 5.5 * max_aspect))
    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(panel_width * columns, 4.8 * rows),
        squeeze=False,
        facecolor="#ECEFF3",
    )
    fig.suptitle(title, fontsize=14, fontweight="bold")

    for row, (path, image) in enumerate(images):
        original_ax = axes[row, 0]
        original_ax.imshow(image)
        original_ax.set_title(f"{path.name} — original", fontsize=10)
        original_ax.axis("off")
        if include_grayscale:
            gray_ax = axes[row, 1]
            gray_ax.imshow(_grayscale(image), cmap="gray", vmin=0.0, vmax=1.0)
            gray_ax.set_title(f"{path.name} — grayscale", fontsize=10)
            gray_ax.axis("off")

    fig.tight_layout(rect=(0, 0, 1, 0.97), pad=1.2)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
        pad_inches=0.08,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an original/grayscale scientific-figure review sheet."
    )
    parser.add_argument("inputs", nargs="+", help="input raster images")
    parser.add_argument("--output", help="review PNG output path")
    parser.add_argument(
        "--grayscale",
        action="store_true",
        help="include a grayscale panel for each input",
    )
    parser.add_argument(
        "--title",
        default="Scientific figure visual review",
        help="review-sheet title",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    first = Path(args.inputs[0])
    output = Path(args.output) if args.output else first.with_name(
        f"{first.stem}.review.png"
    )
    try:
        result = create_review_sheet(
            args.inputs,
            output,
            include_grayscale=args.grayscale,
            title=args.title,
        )
    except (OSError, ValueError) as exc:
        print(f"Review preview error: {exc}")
        return 2
    print(f"Wrote review preview: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
