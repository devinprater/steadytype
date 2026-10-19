"""The keyboarding lesson state machine. No I/O, no platform calls."""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable

from .commands import Command, Display, EndLesson, Speak, Tone, ToneName
from .hints import KEY_HINTS, spoken
from .keys import Key, KeyEvent
from .lesson import EndKey, Lesson, TaskKind
from .preferences import Feedback, Preferences
from .scoring import Goals, Metrics

IDLE_GAP_SECONDS = 5.0


class SessionState(Enum):
    INTRO = "intro"
    TASK_INTRO = "task_intro"
    TYPING = "typing"
    TASK_DONE = "task_done"
    LESSON_DONE = "lesson_done"


def _has_tone(prefs: Preferences) -> bool:
    return prefs.feedback in (Feedback.TONE, Feedback.BOTH)


def _has_word(prefs: Preferences) -> bool:
    return prefs.feedback in (Feedback.WORD, Feedback.BOTH)


class LessonSession:
    def __init__(self, lesson: Lesson, prefs: Preferences,
                 goals: Goals | None = None,
                 now: Callable[[], float] = time.monotonic) -> None:
        self.lesson = lesson
        self.prefs = prefs
        self.goals = goals or Goals()
        self._now = now
        self.state = SessionState.INTRO
        self.task_index = 0
        self.position = 0
        self.current_repeat = 1
        self._errors_at_key: dict[str, int] = {}
        self._first_try_at_position = 0
        self._keypresses = 0
        self._errors = 0
        self._first_try_correct = 0
        self._active_seconds = 0.0
        self._last_timestamp: float | None = None

    # -- inputs ---------------------------------------------------------
    def start(self) -> list[Command]:
        self.state = SessionState.TASK_INTRO
        return [Speak(self.lesson.intro, interrupt=True),
                Speak(self._task_intro(), interrupt=False)]

    def handle(self, event: KeyEvent) -> list[Command]:
        if event.kind != "down" or self.state is SessionState.LESSON_DONE:
            return []
        if event.is_repeat:
            return []

        self._account_time(event.timestamp)
        self._keypresses += 1

        if self.state is SessionState.TASK_INTRO:
            self.state = SessionState.TYPING

        if self.position >= len(self._target()):
            return self._handle_end_key(event)
        return self._handle_character(event)

    def tick(self, now: float) -> list[Command]:
        return []

    def repeat_instructions(self) -> list[Command]:
        target = self._target()
        expected = target[self.position] if self.position < len(target) else None
        if expected is None:
            return [Speak(f"Type {spoken(self._end_key_name())} to finish this one.", interrupt=True)]
        return [Speak(
            f"Type {spoken(expected)}. You are at character {self.position + 1} "
            f"of {len(target)}.", interrupt=True)]

    # -- internals ------------------------------------------------------
    def _target(self) -> str:
        return self.lesson.tasks[self.task_index].text

    def _end_key_name(self) -> str:
        return "space" if self.lesson.end_key is EndKey.SPACE else "enter"

    def _task_intro(self) -> str:
        task = self.lesson.tasks[self.task_index]
        count = len(self.lesson.tasks)
        if task.kind is TaskKind.KEY:
            body = f"Press {spoken(task.text)}"
        else:
            body = f"Type {task.text}"
        ending = "" if self.lesson.end_key is EndKey.NONE else (
            f" Then press {self._end_key_name()}.")
        return (f"Task {self.task_index + 1} of {count}. {body}, "
                f"{self.lesson.repeat} times.{ending}")

    def _account_time(self, timestamp: float) -> None:
        if self._last_timestamp is not None:
            gap = timestamp - self._last_timestamp
            if 0 < gap <= IDLE_GAP_SECONDS:
                self._active_seconds += gap
        self._last_timestamp = timestamp

    def _handle_character(self, event: KeyEvent) -> list[Command]:
        expected = self._target()[self.position]
        task = self.lesson.tasks[self.task_index]

        if task.kind is TaskKind.TEXT:
            produced = event.text
            if produced is None:
                return self._wrong("unknown", expected)
            if produced != expected:
                return self._wrong(produced, expected)
        else:
            if event.key.value != task.text.lower():
                return self._wrong(event.key.value, task.text.lower())

        return self._correct()

    def _correct(self) -> list[Command]:
        if self._first_try_at_position == 0:
            self._first_try_correct += 1
        self._first_try_at_position = 0
        self.position += 1
        commands: list[Command] = []
        if _has_tone(self.prefs) and self.prefs.tones:
            commands.append(Tone(ToneName.CORRECT))
        if _has_word(self.prefs):
            commands.append(Speak("right"))
        if self.position >= len(self._target()):
            if self.lesson.end_key is EndKey.NONE:
                commands.extend(self._complete_repeat())
            else:
                commands.append(Speak(f"Press {self._end_key_name()}."))
        return commands

    def _wrong(self, produced: str, expected: str) -> list[Command]:
        self._errors += 1
        self._first_try_at_position += 1
        seen = self._errors_at_key.get(expected, 0) + 1
        self._errors_at_key[expected] = seen

        commands: list[Command] = []
        if _has_tone(self.prefs) and self.prefs.tones:
            commands.append(Tone(ToneName.WRONG))

        if produced == "unknown":
            message = f"That was an unknown key. You need {spoken(expected)}."
        elif seen == 1:
            message = f"That was {spoken(produced)}. You need {spoken(expected)}."
        else:
            hint = KEY_HINTS.get(expected)
            if hint:
                message = f"{spoken(expected)} is {hint}."
            else:
                message = f"That was {spoken(produced)}. You need {spoken(expected)}."
        commands.append(Speak(message, interrupt=True))
        return commands

    def _handle_end_key(self, event: KeyEvent) -> list[Command]:
        wanted = Key.SPACE if self.lesson.end_key is EndKey.SPACE else Key.ENTER
        if event.key is wanted:
            return self._complete_repeat()
        self._errors += 1
        return [Speak(f"Press {self._end_key_name()} to finish the task.", interrupt=True)]

    def _complete_repeat(self) -> list[Command]:
        self.state = SessionState.TASK_DONE
        if self.current_repeat < self.lesson.repeat:
            self.current_repeat += 1
            self.position = 0
            self._first_try_at_position = 0
            self.state = SessionState.TYPING
            return [Speak(f"Again. {self._task_intro()}", interrupt=True)]

        self.task_index += 1
        self.position = 0
        self.current_repeat = 1
        self._first_try_at_position = 0
        if self.task_index >= len(self.lesson.tasks):
            self.state = SessionState.LESSON_DONE
            return [Tone(ToneName.LESSON_DONE), EndLesson()]
        self.state = SessionState.TASK_INTRO
        return [Speak(self._task_intro(), interrupt=True), Display("next task")]

    # -- read-only view -------------------------------------------------
    @property
    def metrics(self) -> Metrics:
        return Metrics(
            characters=self._characters(),
            keypresses=self._keypresses,
            errors=self._errors,
            first_try_correct=self._first_try_correct,
            active_seconds=self._active_seconds,
        )

    def _characters(self) -> int:
        total = 0
        for index, task in enumerate(self.lesson.tasks):
            if index < self.task_index:
                total += len(task.text) * self.lesson.repeat
            elif index == self.task_index:
                total += len(task.text) * (self.current_repeat - 1) + self.position
        return total
