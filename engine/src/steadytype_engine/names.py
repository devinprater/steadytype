"""Say the keys the way this platform labels them."""

from __future__ import annotations

import re
import sys

_NAMES = {
    "alt": {"darwin": "Option", "win32": "Alt", "linux": "Alt"},
    "meta": {"darwin": "Command", "win32": "Windows key", "linux": "Super"},
    "super": {"darwin": "Command", "win32": "Windows key", "linux": "Super"},
    "windows": {"darwin": "Command", "win32": "Windows key", "linux": "Super"},
    "command": {"darwin": "Command", "win32": "Windows key", "linux": "Super"},
    "control": {"darwin": "Control", "win32": "Control", "linux": "Control"},
    "shift": {"darwin": "Shift", "win32": "Shift", "linux": "Shift"},
}


def key_name(token: str, platform: str | None = None) -> str:
    platform = platform or sys.platform
    names = _NAMES.get(token.strip().lower())
    if names is None:
        return token
    return names.get(platform, names["linux"])


def localize(text: str, platform: str | None = None) -> str:
    """Rewrite modifier names in spoken text for the current platform."""
    platform = platform or sys.platform
    def replace(match: re.Match) -> str:
        word = match.group(0)
        return key_name(word, platform)

    return re.sub(r"\b(Alt|Meta|Super|Command|Windows)\b", replace, text)
