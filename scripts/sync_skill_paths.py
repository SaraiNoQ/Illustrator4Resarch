#!/usr/bin/env python3
"""Synchronize portable skill sources into Codex and Claude Code discovery paths."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "scientific-figure-making"
TARGETS = [
    ROOT / ".agents" / "skills" / "scientific-figure-making",
    ROOT / ".claude" / "skills" / "scientific-figure-making",
]
CODEX_METADATA = SOURCE / "agents" / "openai.yaml"


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing source skill directory: {src}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    for target in TARGETS:
        copy_tree(SOURCE, target)

    # Claude Code ignores agents/openai.yaml; keep it harmless but remove it from
    # the Claude-specific copy to reduce visual noise.
    claude_metadata = ROOT / ".claude" / "skills" / "scientific-figure-making" / "agents"
    if claude_metadata.exists():
        shutil.rmtree(claude_metadata)

    # Ensure the Codex-specific metadata remains present in the Codex copy.
    if CODEX_METADATA.exists():
        codex_agents_dir = ROOT / ".agents" / "skills" / "scientific-figure-making" / "agents"
        codex_agents_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CODEX_METADATA, codex_agents_dir / "openai.yaml")

    print("Synchronized skill package to .agents/skills and .claude/skills")


if __name__ == "__main__":
    main()
