"""Dictation as the client drives it: chunks spoken, keys taken, result saved."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from steadytype_engine.dictation import DictationSession, Passage
from steadytype_engine.preferences import Preferences
from steadytype_engine.scoring import AttemptRecord

PASSAGES = (
    Passage(title="A short note", text="Set your hands on the home row and begin. "
            "Keep an even pace and let the words come one at a time."),
    Passage(title="At the desk", text="The room is quiet and the work is ready. "
            "Type each line as you hear it, then wait for the next one."),
    Passage(title="On the way", text="A good day starts with a steady hand. "
            "Take your time and the speed will follow."),
)


class DictationRunner:
    def __init__(self, passage: Passage, prefs: Preferences, save: Callable,
                 speak: Callable, display: Callable | None = None,
                 lesson_id: int = 0) -> None:
        self.session = DictationSession(passage, prefs)
        self.passage = passage
        self.save = save
        self.speak = speak
        self.display = display
        self.lesson_id = lesson_id
        self.done = False
        self._started = datetime.now(UTC)

    def start(self) -> None:
        self.speak(f"Dictation. {self.passage.title}. Type what you hear. "
                   "Press Enter to move on, or Escape to stop.", True)
        for command in self.session.start():
            self.speak(command.text, command.interrupt)
        self._show()

    def handle(self, event) -> None:
        if self.done:
            return
        for command in self.session.handle(event):
            self.speak(command.text, command.interrupt)
        self._show()
        if self.session.finished:
            self._finish()

    def _show(self) -> None:
        if self.display is not None:
            self.display(self.passage.text, len(self.session.typed))

    def _finish(self) -> None:
        if self.done:
            return
        self.done = True
        result = self.session.finish()
        ended = datetime.now(UTC)
        record = AttemptRecord(
            id=str(uuid.uuid4()), lesson_id=self.lesson_id, kind="dictation",
            started_at=self._started.isoformat(), ended_at=ended.isoformat(),
            active_seconds=max(0.0, (ended - self._started).total_seconds()),
            characters=len(self.session.typed), keypresses=len(self.session.typed),
            errors=len(result.misspelled), wpm=result.wpm, accuracy=result.accuracy,
            real_accuracy=result.accuracy, stars=0, key_stats=(),
            device_id="", client_version="")
        self.save(record)
        self.speak(f"Dictation finished. {result.wpm:.0f} words per minute, "
                   f"{result.accuracy:.0f} percent accurate.", True)
