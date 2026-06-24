"""Repository package bridge to the standalone skill design engine."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SKILL_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "scientific-figure-making" / "scripts"
_SKILL_DESIGN = _SKILL_SCRIPTS / "figure_design.py"
if not _SKILL_DESIGN.exists():
    raise ImportError(f"Missing standalone figure design engine: {_SKILL_DESIGN}")
if str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

_MODULE_NAME = "_scientific_figure_skill_design_engine"
_spec = importlib.util.spec_from_file_location(_MODULE_NAME, _SKILL_DESIGN)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load standalone figure design engine: {_SKILL_DESIGN}")
_module = importlib.util.module_from_spec(_spec)
sys.modules[_MODULE_NAME] = _module
_spec.loader.exec_module(_module)

from .handdrawn_fix import patch_design_module as _patch_design_module
_module = _patch_design_module(_module)

for _name in dir(_module):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_module, _name)

__all__ = [name for name in globals() if not name.startswith("_")]
