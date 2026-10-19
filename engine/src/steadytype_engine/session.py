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
from .scoring import AttemptRecord, Goals, KeyStat, Metrics

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
        self._presses_at_key: dict[str, int] = {}
        self._first_try_at_position = 0
        self._keypresses = 0
        self._errors = 0
        self._first_try_correct = 0
        self._active_seconds = 0.0
        self._last_timestamp: float | None = None
        self._started_at = None
        self.device_id = ""
        self.client_version = "0.1.0"

    # -- inputs ---------------------------------------------------------
    def start(self) -> list[Command]:
        from datetime import datetime, timezone

        self._started_at = datetime.now(timezone.utc)
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
        self._presses_at_key[expected] = self._presses_at_key.get(expected, 0) + 1

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

    # -- results --------------------------------------------------------
    def finish(self) -> "AttemptRecord":
        import uuid
        from datetime import datetime, timezone

        from .scoring import AttemptRecord, KeyStat, stars

        metrics = self.metrics
        ended = datetime.now(timezone.utc)
        record = AttemptRecord(
            id=str(uuid.uuid4()),
            lesson_id=self.lesson.id,
            kind="practice",
            started_at=self._started_at.isoformat() if self._started_at else ended.isoformat(),
            ended_at=ended.isoformat(),
            active_seconds=round(metrics.active_seconds, 2),
            characters=metrics.characters,
            keypresses=metrics.keypresses,
            errors=metrics.errors,
            wpm=round(metrics.wpm, 2),
            accuracy=round(metrics.accuracy, 2),
            real_accuracy=round(metrics.real_accuracy, 2),
            stars=stars(metrics, self.goals),
            key_stats=tuple(
                KeyStat(key=key, presses=self._presses_at_key.get(key, 0), errors=errors)
                for key, errors in sorted(self._errors_at_key.items())
            ),
            device_id=self.device_id,
            client_version=self.client_version,
        )
        return record

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


def tip_for(key_stats) -> str:
    """One tip drawn from the student's own errors, or a neutral line."""
    stats = [stat for stat in key_stats if stat.presses >= 0]
    if not stats:
        return "Keep your fingers on the home row."
    ranked = sorted(stats, key=lambda stat: stat.errors, reverse=True)
    best = ranked[0]
    runner_up = ranked[1].errors if len(ranked) > 1 else 0
    if best.errors >= 2 and best.errors >= runner_up * 2:
        hint = KEY_HINTS.get(best.key)
        if hint:
            return f"Most of your misses were on {best.key}. {hint[0].upper()}{hint[1:]}."
    return "Keep your fingers on the home row."


def result_commands(record: AttemptRecord, prefs: Preferences | None = None) -> list[Command]:
    """What the student hears when a lesson ends. No jokes, by design."""
    minutes = record.active_seconds / 60
    return [
        Speak(f"Your accuracy was {record.accuracy:.0f} percent. "
              f"Real accuracy, before corrections, was {record.real_accuracy:.0f} percent."),
        Speak(f"You typed {record.wpm:.0f} words per minute, "
              f"in {minutes:.1f} minutes."),
        Speak(f"You earned {record.stars} out of 5 stars."),
        Speak(tip_for(record.key_stats)),
        Speak("Press Enter for the next lesson, or F3 twice to choose another."),
    ]
