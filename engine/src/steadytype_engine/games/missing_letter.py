"""A word loses one letter; the student finds the gap and types it."""

from __future__ import annotations

import random
from typing import Sequence

from ..buffer import TextBuffer
from .base import GamePrompt


class MissingLetterGame:
    def make(self, rng: random.Random, words: Sequence[str]) -> GamePrompt:
        target = rng.choice(list(words))
        index = rng.randrange(len(target))
        missing = target[index]
        text = target[:index] + target[index + 1:]
        buffer = TextBuffer(text)
        buffer.cursor = 0
        return GamePrompt(
            intro=(f"The word is {target}, with one letter missing. "
                   f"Move to the gap and type the missing letter."),
            buffer=buffer,
            target=target,
            help=f"The missing letter is the one after {target[index - 1] if index else 'the start'}.",
        )

    def is_complete(self, buffer: TextBuffer) -> bool:
        return buffer.text == getattr(buffer, "target", None) or False
