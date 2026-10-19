"""A sentence gains one word; the student selects it and deletes it."""

from __future__ import annotations

import random
from collections.abc import Sequence

from ..buffer import TextBuffer
from .base import GamePrompt

EXTRA_WORDS = ("very", "quickly", "always", "really", "suddenly", "nearly")


def _normalize(text: str) -> str:
    return " ".join(text.split())


class SelectDeleteGame:
    def __init__(self) -> None:
        self.target = ""

    def make(self, rng: random.Random, words: Sequence[str]) -> GamePrompt:
        self.target = rng.choice(list(words))
        words_in_target = self.target.split()
        candidates = [w for w in EXTRA_WORDS if w not in words_in_target]
        extra = rng.choice(candidates)
        position = rng.randrange(len(words_in_target) + 1)
        modified = words_in_target[:position] + [extra] + words_in_target[position:]
        buffer = TextBuffer(" ".join(modified))
        buffer.cursor = 0
        return GamePrompt(
            intro=("This sentence has one word too many. Find it, select it "
                   "with Shift and the arrow keys, and delete it."),
            buffer=buffer,
            target=self.target,
            help=f"The extra word starts at word {position + 1}.",
        )

    def is_complete(self, buffer: TextBuffer) -> bool:
        return _normalize(buffer.text) == _normalize(self.target)
