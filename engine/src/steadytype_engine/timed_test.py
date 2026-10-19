"""The timed certification test: no correction, no feedback, one clock."""

from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum

from .certification import CertificationResult, score_test
from .commands import Command, Speak
from .dictation import Passage
from .keys import Key, KeyEvent


class TestState(Enum):
    __test__ = False

    READY = "ready"
    RUNNING = "running"
    FINISHED = "finished"


class TimedTest:
    def __init__(self, passage: Passage, seconds: int, allow_backspace: bool = True,
                 min_net_wpm: float = 50.0, max_errors: int = 10,
                 now: Callable[[], float] = time.monotonic) -> None:
        self.passage = passage
        self.seconds = seconds
        self.allow_backspace = allow_backspace
        self.min_net_wpm = min_net_wpm
        self.max_errors = max_errors
        self._now = now
        self.state = TestState.READY
        self.typed = ""
        self._started = 0.0
        self._warned = False

    @property
    def remaining_seconds(self) -> float:
        if self.state is TestState.READY:
            return float(self.seconds)
        return max(0.0, self.seconds - (self._now() - self._started))

    def read_passage(self) -> list[Command]:
        return [Speak(self.passage.text, interrupt=True)]

    def start(self) -> list[Command]:
        self.state = TestState.RUNNING
        self._started = self._now()
        minutes = self.seconds / 60
        return [Speak(f"The test is {minutes:g} minutes. Begin when you are ready.",
                      interrupt=True)]

    def handle(self, event: KeyEvent) -> list[Command]:
        if self.state is not TestState.RUNNING or event.kind != "down" or event.is_repeat:
            return []
        if event.key is Key.BACKSPACE:
            if self.allow_backspace and self.typed:
                self.typed = self.typed[:-1]
            return []
        if event.key is Key.ESCAPE:
            self.state = TestState.FINISHED
            return [Speak("Test finished.", interrupt=True)]
        if event.text is not None:
            self.typed += event.text
        return []

    def tick(self, now: float) -> list[Command]:
        if self.state is not TestState.RUNNING:
            return []
        remaining = self.seconds - (now - self._started)
        if remaining <= 0:
            self.state = TestState.FINISHED
            return [Speak("Time.", interrupt=True)]
        if self._warned:
            return []
        if 0 < remaining <= 60:
            self._warned = True
            return [Speak("You have one minute left.", interrupt=True)]
        return []

    def attempt_record(self, lesson_id: int = 0, result=None):
        """The row the dashboard needs, saved with kind timed_test."""
        import uuid
        from datetime import UTC, datetime

        from .scoring import AttemptRecord

        result = result or self.finish()
        elapsed = max(0.0, min(float(self.seconds), self._now() - self._started))
        stamp = datetime.now(UTC).isoformat()
        return AttemptRecord(
            id=str(uuid.uuid4()), lesson_id=lesson_id, kind="timed_test",
            started_at=stamp, ended_at=stamp, active_seconds=elapsed,
            characters=len(self.typed), keypresses=len(self.typed),
            errors=result.error_words, wpm=result.net_wpm, accuracy=result.accuracy,
            real_accuracy=result.accuracy, stars=0, key_stats=(),
            device_id="", client_version="")

    def finish(self) -> CertificationResult:
        elapsed = self._now() - self._started
        elapsed = max(0.0, min(float(self.seconds), elapsed))
        self.state = TestState.FINISHED
        return score_test(self.typed, self.passage.text, elapsed,
                          self.min_net_wpm, self.max_errors)
