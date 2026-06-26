#!/usr/bin/env python3
"""Install scientific-figure-making into global tool directories."""
from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "scientific-figure-making"
SOURCE = ROOT / "skills" / SKILL_NAME


def skills_root_from_env(env_var: str, default: Path) -> Path:
    raw_value = os.environ.get(env_var)
    if raw_value:
        return Path(raw_value).expanduser()
    return default


CODEX_DEST = skills_root_from_env("CODEX_SKILLS_DIR", Path.home() / ".agents" / "skills") / SKILL_NAME
CLAUDE_DEST = skills_root_from_env("CLAUDE_SKILLS_DIR", Path.home() / ".claude" / "skills") / SKILL_NAME
HERMES_DEST = skills_root_from_env("HERMES_SKILLS_DIR", Path.home() / ".hermes" / "skills") / SKILL_NAME


@dataclass(frozen=True)
class InstallTarget:
    name: str
    destination: Path
    remove_codex_metadata: bool = False


INSTALL_TARGETS = {
    "codex": InstallTarget("Codex", CODEX_DEST, False),
    "claude": InstallTarget("Claude Code", CLAUDE_DEST, True),
    "hermes": InstallTarget("Hermes", HERMES_DEST, False),
}

TARGET_ALIASES = {
    "both": ["codex", "claude"],
    "all": ["codex", "claude", "hermes"],
}


def ensure_source_exists() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source skill directory: {SOURCE}")
    if not SOURCE.is_dir():
        raise NotADirectoryError(f"Source skill path is not a directory: {SOURCE}")
    if not (SOURCE / "SKILL.md").exists():
        raise FileNotFoundError(f"Source skill package is missing SKILL.md: {SOURCE}")


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def looks_like_installed_skill(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").exists()


def remove_existing_installation(destination: Path, *, label: str) -> bool:
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
    target_keys = TARGET_ALIASES.get(target, [target])
    return [INSTALL_TARGETS[target_key] for target_key in target_keys]


def main() -> None:
    parser = argparse.ArgumentParser(description="Install scientific-figure-making globally.")
    parser.add_argument(
        "--target",
        choices=["codex", "claude", "hermes", "both", "all"],
        default="both",
        help="Target runtime. 'both' installs Codex and Claude Code; 'all' also installs Hermes.",
    )
    args = parser.parse_args()

    for target in selected_targets(args.target):
        copy_skill(
            target.destination,
            remove_codex_metadata=target.remove_codex_metadata,
            label=target.name,
        )

    print("Done. Restart the session if it does not pick up the refreshed skill immediately.")


if __name__ == "__main__":
    main()
