#!/usr/bin/env python3
"""Install the scientific-figure-making skill into global agent skill directories."""
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "scientific-figure-making"
CODEX_DEST = Path.home() / ".agents" / "skills" / "scientific-figure-making"
CLAUDE_DEST = Path.home() / ".claude" / "skills" / "scientific-figure-making"


@dataclass(frozen=True)
class InstallTarget:
    """Global installation target for one agent runtime."""

    name: str
    destination: Path
    remove_codex_metadata: bool = False


INSTALL_TARGETS = {
    "codex": InstallTarget(
        name="Codex",
        destination=CODEX_DEST,
        remove_codex_metadata=False,
    ),
    "claude": InstallTarget(
        name="Claude Code",
        destination=CLAUDE_DEST,
        remove_codex_metadata=True,
    ),
}


def ensure_source_exists() -> None:
    """Fail early if the canonical skill package is missing."""
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source skill directory: {SOURCE}")
    if not SOURCE.is_dir():
        raise NotADirectoryError(f"Source skill path is not a directory: {SOURCE}")
    if not (SOURCE / "SKILL.md").exists():
        raise FileNotFoundError(f"Source skill package is missing SKILL.md: {SOURCE}")


def path_exists(path: Path) -> bool:
    """Return True for normal paths and broken symlinks."""
    return path.exists() or path.is_symlink()


def looks_like_installed_skill(path: Path) -> bool:
    """Best-effort check for an existing scientific-figure-making installation."""
    return path.is_dir() and (path / "SKILL.md").exists()


def remove_existing_installation(destination: Path, *, label: str) -> bool:
    """Delete a previous installation or stale path before reinstalling.

    The installer owns the exact destination path for the selected target. If that
    path already exists, replacing it is safer than merging directories because
    old helper scripts, references, or metadata files can otherwise survive.
    """
    if not path_exists(destination):
        print(f"[{label}] No existing skill found at {destination}")
        return False

    if looks_like_installed_skill(destination):
        print(f"[{label}] Existing skill found at {destination}; removing before reinstall")
    else:
        print(f"[{label}] Existing path found at {destination}; replacing it with the current skill")

    if destination.is_dir() and not destination.is_symlink():
        shutil.rmtree(destination)
    else:
        destination.unlink()
    return True


def copy_skill(destination: Path, *, remove_codex_metadata: bool = False, label: str = "skill") -> bool:
    """Install the canonical skill package and return whether a previous path was removed."""
    ensure_source_exists()
    destination.parent.mkdir(parents=True, exist_ok=True)

    removed_existing = remove_existing_installation(destination, label=label)
    shutil.copytree(SOURCE, destination)

    if remove_codex_metadata:
        agents_dir = destination / "agents"
        if agents_dir.exists():
            shutil.rmtree(agents_dir)

    print(f"[{label}] Installed current skill at {destination}")
    return removed_existing


def selected_targets(target: str) -> list[InstallTarget]:
    """Expand CLI target aliases into concrete install targets."""
    if target in {"both", "all"}:
        return [INSTALL_TARGETS["codex"], INSTALL_TARGETS["claude"]]
    return [INSTALL_TARGETS[target]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Install scientific-figure-making globally for Codex and/or Claude Code.")
    parser.add_argument(
        "--target",
        choices=["codex", "claude", "both", "all"],
        default="both",
        help="Which global skill directory to install into. 'all' is an alias for 'both'.",
    )
    args = parser.parse_args()

    for target in selected_targets(args.target):
        copy_skill(
            target.destination,
            remove_codex_metadata=target.remove_codex_metadata,
            label=target.name,
        )

    print("Done. Restart the agent session if it does not pick up the refreshed skill immediately.")


if __name__ == "__main__":
    main()
