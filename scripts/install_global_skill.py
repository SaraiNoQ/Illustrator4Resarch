#!/usr/bin/env python3
"""Install the scientific-figure-making skill into global agent skill directories."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "scientific-figure-making"
CODEX_DEST = Path.home() / ".agents" / "skills" / "scientific-figure-making"
CLAUDE_DEST = Path.home() / ".claude" / "skills" / "scientific-figure-making"


def copy_skill(destination: Path, *, remove_codex_metadata: bool = False) -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source skill directory: {SOURCE}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(SOURCE, destination)
    if remove_codex_metadata:
        agents_dir = destination / "agents"
        if agents_dir.exists():
            shutil.rmtree(agents_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install scientific-figure-making globally for Codex and/or Claude Code.")
    parser.add_argument("--target", choices=["codex", "claude", "both"], default="both", help="Which global skill directory to install into.")
    args = parser.parse_args()

    if args.target in {"codex", "both"}:
        copy_skill(CODEX_DEST, remove_codex_metadata=False)
        print(f"Installed Codex user skill: {CODEX_DEST}")

    if args.target in {"claude", "both"}:
        copy_skill(CLAUDE_DEST, remove_codex_metadata=True)
        print(f"Installed Claude Code personal skill: {CLAUDE_DEST}")

    print("Done. Restart the agent session if the skill directory did not exist before installation.")


if __name__ == "__main__":
    main()
