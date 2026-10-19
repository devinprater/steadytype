"""Translate engine commands into speech, sound, display, and saved attempts."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from steadytype_engine.commands import Display, EndLesson, SaveAttempt, Speak, Tone
from steadytype_engine.lesson import Lesson
from steadytype_engine.names import localize
from steadytype_engine.preferences import Preferences
from steadytype_engine.scoring import Goals
from steadytype_engine.session import LessonSession, SessionState, result_commands


class DisplayPort(Protocol):
    def show(self, text: str, position: int) -> None: ...


class LessonPresenter:
    def __init__(self, lesson: Lesson, prefs: Preferences, goals: Goals,
                 speech, player, save: Callable | None = None,
                 display: DisplayPort | None = None,
                 now: Callable[[], float] = time.monotonic) -> None:
        self.lesson = lesson
        self.prefs = prefs
        self.speech = speech
        self.player = player
        self.save = save or (lambda record: None)
        self.display = display
        self.session = LessonSession(lesson, prefs, goals, now=now)
        self.finished = False

    @property
    def state(self) -> SessionState:
        return self.session.state

    @property
    def position(self) -> int:
        return self.session.position

    def start(self) -> None:
        self._run(self.session.start())
        self._show()

    def handle(self, event) -> None:
        if self.finished:
            return
        self._run(self.session.handle(event))
        self._show()

    def repeat(self) -> None:
        self._run(self.session.repeat_instructions())

    def tick(self, now: float) -> None:
        self._run(self.session.tick(now))

    def _show(self) -> None:
        if self.display is None:
            return
        if self.session.state is SessionState.LESSON_DONE:
            return
        task = self.lesson.tasks[self.session.task_index]
        self.display.show(task.text, self.session.position)

    def _run(self, commands) -> None:
        for command in commands:
            if isinstance(command, Speak):
                self.speech.speak(localize(command.text), command.interrupt)
            elif isinstance(command, Tone):
                if self.prefs.tones:
                    self.player.play(command.name)
            elif isinstance(command, Display):
                self._show()
            elif isinstance(command, SaveAttempt):
                self.save(command.record)
            elif isinstance(command, EndLesson):
                self._finish()

    def _finish(self) -> None:
        if self.finished:
            return
        self.finished = True
        record = self.session.finish()
        self.save(record)
        self._run(result_commands(record, self.prefs))
