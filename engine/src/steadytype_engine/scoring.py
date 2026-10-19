"""Attempt metrics, stars, and the saved attempt record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    characters: int
    keypresses: int
    errors: int
    first_try_correct: int
    active_seconds: float

    @property
    def wpm(self) -> float:
        if self.active_seconds <= 0:
            return 0.0
        return (self.characters / 5) / (self.active_seconds / 60)

    @property
    def accuracy(self) -> float:
        if self.keypresses <= 0:
            return 0.0
        return (self.keypresses - self.errors) / self.keypresses * 100

    @property
    def real_accuracy(self) -> float:
        if self.characters <= 0:
            return 0.0
        return self.first_try_correct / self.characters * 100


@dataclass(frozen=True)
class Goals:
    wpm_target: float = 20.0
    accuracy_target: float = 95.0


@dataclass(frozen=True)
class KeyStat:
    key: str
    presses: int
    errors: int


@dataclass(frozen=True)
class AttemptRecord:
    id: str
    lesson_id: int
    kind: str
    started_at: str
    ended_at: str
    active_seconds: float
    characters: int
    keypresses: int
    errors: int
    wpm: float
    accuracy: float
    real_accuracy: float
    stars: int
    key_stats: tuple[KeyStat, ...]
    device_id: str
    client_version: str


def accuracy_star(accuracy: float) -> int:
    if accuracy >= 98:
        return 5
    if accuracy >= 95:
        return 4
    if accuracy >= 90:
        return 3
    if accuracy >= 80:
        return 2
    return 1


def speed_star(wpm: float, target: float) -> int:
    if target <= 0:
        return 1
    if wpm >= target:
        return 5
    if wpm >= target * 0.9:
        return 4
    if wpm >= target * 0.75:
        return 3
    if wpm >= target * 0.5:
        return 2
    return 1


def stars(metrics: Metrics, goals: Goals) -> int:
    return min(accuracy_star(metrics.accuracy), speed_star(metrics.wpm, goals.wpm_target))
