#!/usr/bin/env python3
"""Package the standalone skill folder as a ZIP archive."""
from __future__ import annotations

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "scientific-figure-making"
DIST = ROOT / "dist"
ZIP_PATH = DIST / "scientific-figure-making.zip"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.name in EXCLUDE_SUFFIXES:
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source skill directory: {SOURCE}")
    DIST.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in SOURCE.rglob("*"):
            if should_include(path):
                zf.write(path, arcname=path.relative_to(SOURCE.parent))
    print(f"Wrote {ZIP_PATH}")


if __name__ == "__main__":
    main()
