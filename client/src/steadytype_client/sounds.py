"""Short non-speech cues. The names match the engine's tone names."""

from __future__ import annotations

import json
import sys
from pathlib import Path


class SoundPlayer:
    def play(self, tone: str) -> None: ...


class NullPlayer:
    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, tone: str) -> None:
        self.played.append(tone)


class WinsoundPlayer:
    def __init__(self, sounds_dir: Path, play=None) -> None:
        self.sounds_dir = Path(sounds_dir)
        self._manifest = {}
        manifest_path = self.sounds_dir / "manifest.json"
        if manifest_path.exists():
            self._manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if play is None:
            import winsound
            play = lambda path: winsound.PlaySound(
                str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        self._play = play

    def path_for(self, tone: str) -> Path | None:
        entry = self._manifest.get(tone)
        if not entry:
            return None
        return self.sounds_dir / entry["synth"]

    def play(self, tone: str) -> None:
        path = self.path_for(tone)
        if path is not None and path.exists():
            self._play(path)


def create_player(sounds_dir: Path) -> SoundPlayer:
    if sys.platform == "win32":
        return WinsoundPlayer(sounds_dir)
    return NullPlayer()
