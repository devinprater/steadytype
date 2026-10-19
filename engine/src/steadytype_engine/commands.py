"""What the engine asks the client to do. The engine never performs these itself."""

from __future__ import annotations

from dataclasses import dataclass


class ToneName:
    CORRECT = "correct"
    WRONG = "wrong"
    RACE_START = "race_start"
    RACE_WARNING = "race_warning"
    RACE_END = "race_end"
    LESSON_DONE = "lesson_done"
    GOAL_REACHED = "goal_reached"


@dataclass(frozen=True)
class Speak:
    text: str
    interrupt: bool = False


@dataclass(frozen=True)
class Tone:
    name: str


@dataclass(frozen=True)
class Display:
    state: str


@dataclass(frozen=True)
class SaveAttempt:
    record: object


@dataclass(frozen=True)
class EndLesson:
    pass


Command = Speak | Tone | Display | SaveAttempt | EndLesson
