"""A word loses one letter; the student finds the gap and types it."""

from __future__ import annotations

import random
from typing import Sequence

from ..buffer import TextBuffer
from .base import GamePrompt


class MissingLetterGame:
    def __init__(self) -> None:
        self.target = ""

    def make(self, rng: random.Random, words: Sequence[str]) -> GamePrompt:
        self.target = rng.choice(list(words))
        index = rng.randrange(len(self.target))
        text = self.target[:index] + self.target[index + 1:]
        buffer = TextBuffer(text)
        buffer.cursor = 0
        before = self.target[index - 1] if index else None
        position = f"after {before}" if before else "at the start"
        return GamePrompt(
            intro=(f"The word is {self.target}, with one letter missing. "
                   f"Move to the gap and type the missing letter."),
            buffer=buffer,
            target=self.target,
            help=f"The gap is {position} of the word.",
        )

    def is_complete(self, buffer: TextBuffer) -> bool:
        return buffer.text == self.target
