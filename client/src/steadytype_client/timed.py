"""The timed test as the client drives it: instructions, keys, clock, result."""

from __future__ import annotations

from collections.abc import Callable

from steadytype_engine.certification import CERTIFICATION_TEXT
from steadytype_engine.dictation import Passage
from steadytype_engine.timed_test import TestState, TimedTest


class TimedTestRunner:
    def __init__(self, passage: Passage, seconds: int, save: Callable, speak: Callable,
                 lesson_id: int = 72, now: Callable[[], float] | None = None,
                 display: Callable[[str, int], None] | None = None) -> None:
        kwargs = {"now": now} if now is not None else {}
        self.test = TimedTest(passage, seconds=seconds, **kwargs)
        self.passage = passage
        self.save = save
        self.speak = speak
        self.lesson_id = lesson_id
        self.display = display
        self.done = False

    def start(self) -> None:
        self.speak(f"{CERTIFICATION_TEXT} The passage is: {self.passage.text} "
                   "Type it as accurately as you can. No corrections are counted "
                   "for you.", True)
        for command in self.test.start():
            self.speak(command.text, command.interrupt)
        self.test.state = TestState.RUNNING
        self._show()

    def handle(self, event) -> None:
        if self.done:
            return
        for command in self.test.handle(event):
            self.speak(command.text, command.interrupt)
        self._show()
        self._finish_if_over()

    def tick(self, now: float) -> None:
        if self.done:
            return
        for command in self.test.tick(now):
            self.speak(command.text, command.interrupt)
        self._finish_if_over()

    def _show(self) -> None:
        if self.display is not None:
            self.display(self.passage.text, len(self.test.typed))

    def _finish_if_over(self) -> None:
        if self.test.state is not TestState.FINISHED or self.done:
            return
        self.done = True
        result = self.test.finish()
        self.save(self.test.attempt_record(self.lesson_id, result))
        verdict = ("That meets Alabama's requirement." if result.passed
                   else "That does not meet the requirement yet.")
        self.speak(f"Test finished. {result.net_wpm:.0f} net words per minute, "
                   f"{result.error_words} errors. {verdict} "
                   "This is a practice score, not a certificate.", True)
