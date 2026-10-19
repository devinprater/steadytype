"""A word carries one wrong letter; the student deletes it and types the right one."""

from __future__ import annotations

import random
import string
from typing import Sequence

from ..buffer import TextBuffer
from .base import GamePrompt


class WrongLetterGame:
    def __init__(self) -> None:
        self.target = ""

    def make(self, rng: random.Random, words: Sequence[str]) -> GamePrompt:
        self.target = rng.choice(list(words))
        index = rng.randrange(len(self.target))
        original = self.target[index]
        choices = [c for c in string.ascii_lowercase if c != original]
        wrong = rng.choice(choices)
        text = self.target[:index] + wrong + self.target[index + 1:]
        buffer = TextBuffer(text)
        buffer.cursor = 0
        return GamePrompt(
            intro=(f"The word should be {self.target}, but one letter is wrong. "
                   f"Find the wrong letter, delete it, and type the right one."),
            buffer=buffer,
            target=self.target,
            help=f"The wrong letter is in position {index + 1}.",
        )

    def is_complete(self, buffer: TextBuffer) -> bool:
        return buffer.text == self.target
