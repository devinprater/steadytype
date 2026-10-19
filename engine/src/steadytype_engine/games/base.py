"""Shared shape for the games."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, Sequence

from ..buffer import TextBuffer


@dataclass(frozen=True)
class GamePrompt:
    intro: str
    buffer: TextBuffer
    target: str
    help: str


class Game(Protocol):
    def make(self, rng: random.Random, words: Sequence[str]) -> GamePrompt: ...
    def is_complete(self, buffer: TextBuffer) -> bool: ...
