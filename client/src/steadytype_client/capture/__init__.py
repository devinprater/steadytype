"""Pick the keyboard hook for this platform."""

from __future__ import annotations

import sys


def make_capture():
    if sys.platform == "win32":
        from .windows import WindowsCapture

        return WindowsCapture()
    if sys.platform == "darwin":
        from .macos import MacCapture

        return MacCapture()
    from .linux import LinuxCapture

    return LinuxCapture()
