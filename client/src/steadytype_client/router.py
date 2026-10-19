"""Turn repeated key presses into menu commands."""

from __future__ import annotations

import time
from collections.abc import Callable

from steadytype_engine.keys import Key, KeyEvent

ACTIONS = {
    Key.F1: {2: "repeat"},
    Key.F2: {2: "next", 3: "repeat"},
    Key.F3: {2: "pick"},
    Key.F4: {2: "dictation"},
    Key.F5: {2: "race"},
    Key.F6: {2: "test"},
    Key.F12: {2: "progress", 3: "history"},
    Key.ESCAPE: {3: "quit"},
}
FUNCTION_KEYS = {Key.F1, Key.F2, Key.F3, Key.F4, Key.F5, Key.F6,
                 Key.F7, Key.F8, Key.F9, Key.F10, Key.F11, Key.F12}


class CommandRouter:
    def __init__(self, double_press_ms: int = 500, now: Callable[[], float] = time.monotonic,
                 enabled: bool = True) -> None:
        self.window = double_press_ms / 1000
        self._now = now
        self.enabled = enabled
        self._key: Key | None = None
        self._count = 0
        self._last = 0.0

    def reset(self) -> None:
        self._key = None
        self._count = 0

    def feed(self, event: KeyEvent) -> str | None:
        if event.kind != "down" or event.is_repeat:
            return None
        if not self.enabled and event.key in FUNCTION_KEYS:
            return None

        now = self._now()
        if event.key is not self._key or now - self._last > self.window:
            self._key = event.key
            self._count = 1
            self._last = now
            return None

        self._count += 1
        self._last = now
        action = ACTIONS.get(event.key, {}).get(self._count)
        if action:
            self.reset()
        return action
