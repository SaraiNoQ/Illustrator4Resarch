#!/usr/bin/env python3
"""Synchronize the portable skill source into Codex and Claude Code discovery paths.

Edit `skills/scientific-figure-making/` first, then run this script.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "scientific-figure-making"
CODEX_TARGET = ROOT / ".agents" / "skills" / "scientific-figure-making"
CLAUDE_TARGET = ROOT / ".claude" / "skills" / "scientific-figure-making"
CODEX_METADATA = SOURCE / "agents" / "openai.yaml"


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing source skill directory: {src}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    copy_tree(SOURCE, CODEX_TARGET)
    copy_tree(SOURCE, CLAUDE_TARGET)

    # Claude Code follows the Agent Skills standard and does not need the Codex UI metadata.
    claude_agents_dir = CLAUDE_TARGET / "agents"
    if claude_agents_dir.exists():
        shutil.rmtree(claude_agents_dir)

    # Codex-specific metadata should remain present in the Codex discovery copy.
    if CODEX_METADATA.exists():
        codex_agents_dir = CODEX_TARGET / "agents"
        codex_agents_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CODEX_METADATA, codex_agents_dir / "openai.yaml")

    print("Synchronized skills/scientific-figure-making to .agents/skills and .claude/skills")


if __name__ == "__main__":
    main()
