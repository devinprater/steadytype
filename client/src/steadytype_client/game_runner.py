"""The three practice games, driven by the client's keyboard."""

from __future__ import annotations

import random
import uuid
from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from steadytype_engine.keys import Key
from steadytype_engine.scoring import AttemptRecord

WORDS = ("and", "the", "home", "row", "key", "type", "word", "line", "fast", "slow",
         "hand", "desk", "read", "write", "start", "stop", "small", "large", "good",
         "work", "time", "pace")


class GameRunner:
    def __init__(self, game, save: Callable, speak: Callable, rounds: int = 5,
                 words: Sequence[str] = WORDS, display: Callable | None = None,
                 lesson_id: int = 0, rng: random.Random | None = None) -> None:
        self.game = game
        self.save = save
        self.speak = speak
        self.rounds = rounds
        self.words = words
        self.display = display
        self.lesson_id = lesson_id
        self.rng = rng or random.Random()
        self.buffer = None
        self.target = ""
        self.done = False
        self.completed = 0
        self._started = datetime.now(UTC)

    def start(self) -> None:
        self.speak("Game. Type the answer, then take the next one.", True)
        self._next()

    def _next(self) -> None:
        prompt = self.game.make(self.rng, self.words)
        self.buffer = prompt.buffer
        self.target = prompt.target
        self.speak(prompt.intro, True)
        self.speak(prompt.help)
        self._show()

    def handle(self, event) -> None:
        if self.done or self.buffer is None:
            return
        if event.key is Key.ESCAPE:
            self._finish()
            return
        result = self.buffer.handle(event)
        if result.speech:
            self.speak(result.speech)
        self._show()
        if self.game.is_complete(self.buffer):
            self.completed += 1
            self.rounds -= 1
            if self.rounds > 0:
                self.speak("That's it.")
                self._next()
            else:
                self.speak("That's it. Game over.")
                self._finish()

    def _show(self) -> None:
        if self.display is not None and self.buffer is not None:
            self.display(self.target, self.buffer.cursor)

    def _finish(self) -> None:
        if self.done:
            return
        self.done = True
        ended = datetime.now(UTC)
        record = AttemptRecord(
            id=str(uuid.uuid4()), lesson_id=self.lesson_id, kind="game",
            started_at=self._started.isoformat(), ended_at=ended.isoformat(),
            active_seconds=max(0.0, (ended - self._started).total_seconds()),
            characters=self.completed, keypresses=self.completed,
            errors=0, wpm=0.0, accuracy=100.0 if self.completed else 0.0,
            real_accuracy=100.0 if self.completed else 0.0, stars=0, key_stats=(),
            device_id="", client_version="")
        self.save(record)
        self.speak(f"Game finished. {self.completed} rounds.", True)
