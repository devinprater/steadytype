from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from steadytype_engine.keys import KeyEvent


class KeyCapture(Protocol):
    def start(self, callback: Callable[[KeyEvent], None]) -> bool: ...
    def stop(self) -> None: ...
    @property
    def active(self) -> bool: ...
