import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_global_skill.py"
spec = importlib.util.spec_from_file_location("install_global_skill", MODULE_PATH)
installer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["install_global_skill"] = installer
spec.loader.exec_module(installer)


def test_copy_skill_reinstalls_existing_skill_directory(tmp_path):
    destination = tmp_path / "scientific-figure-making"
    destination.mkdir()
    (destination / "SKILL.md").write_text("stale skill", encoding="utf-8")
    (destination / "stale.txt").write_text("remove me", encoding="utf-8")

    removed_existing = installer.copy_skill(destination, label="Test")

    assert removed_existing is True
    assert destination.is_dir()
    assert (destination / "SKILL.md").exists()
    assert not (destination / "stale.txt").exists()


def test_copy_skill_replaces_existing_non_directory_path(tmp_path):
    destination = tmp_path / "scientific-figure-making"
    destination.write_text("stale file", encoding="utf-8")

    removed_existing = installer.copy_skill(destination, label="Test")

    assert removed_existing is True
    assert destination.is_dir()
    assert (destination / "SKILL.md").exists()


def test_copy_skill_reports_clean_install_when_missing(tmp_path):
    destination = tmp_path / "scientific-figure-making"

    removed_existing = installer.copy_skill(destination, label="Test")

    assert removed_existing is False
    assert destination.is_dir()
    assert (destination / "SKILL.md").exists()


def test_claude_install_removes_codex_metadata(tmp_path):
    destination = tmp_path / "scientific-figure-making"

    installer.copy_skill(destination, remove_codex_metadata=True, label="Claude Code")

    assert destination.is_dir()
    assert (destination / "SKILL.md").exists()
    assert not (destination / "agents").exists()


def test_selected_targets_expands_all_alias():
    targets = installer.selected_targets("all")

    assert [target.name for target in targets] == ["Codex", "Claude Code"]
