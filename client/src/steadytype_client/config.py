"""Where the client keeps its data and finds its sounds."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _platform_data_dir() -> Path:
    override = os.environ.get("STEADYTYPE_DATA_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        return Path(base) / "SteadyType"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SteadyType"
    return Path.home() / ".local" / "share" / "steadytype"


def _bundled_sounds() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "assets" / "sounds"
        if candidate.exists():
            return candidate
    return _platform_data_dir() / "sounds"


@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    sounds: Path = field(default=None)

    def __post_init__(self) -> None:
        if self.sounds is None:
            object.__setattr__(self, "sounds", _bundled_sounds())
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def database(self) -> Path:
        return self.data_dir / "steadytype.db"


def bundled_content() -> Path | None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "content" / "course.yaml"
        if candidate.exists():
            return candidate
    return None


def default_paths() -> AppPaths:
    return AppPaths(_platform_data_dir())
