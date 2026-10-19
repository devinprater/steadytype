"""The daily practice clock and the student's own summary."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from .commands import Command, Speak, Tone, ToneName
from .scoring import AttemptRecord, KeyStat


@dataclass(frozen=True)
class StatsSummary:
    lessons_completed: int
    current_lesson: int
    average_accuracy: float
    average_wpm: float
    best_wpm: float
    minutes_today: float
    minutes_this_week: float
    weakest_keys: tuple[KeyStat, ...]


class PracticeClock:
    def __init__(self, goal_minutes: int | None) -> None:
        self.goal_minutes = goal_minutes
        self.active_seconds = 0.0
        self._announced: set[str] = set()

    @property
    def minutes_today(self) -> float:
        return self.active_seconds / 60

    @property
    def goal_reached(self) -> bool:
        return self.goal_minutes is not None and self.active_seconds >= self._goal_seconds()

    def add_active_seconds(self, seconds: float) -> None:
        if seconds > 0:
            self.active_seconds += seconds

    def announcements(self) -> list[Command]:
        if self.goal_minutes is None:
            return []
        goal_seconds = self._goal_seconds()
        halfway = goal_seconds / 2
        if self.goal_minutes <= 10:
            warning_at = goal_seconds * 0.8
            warning_text = f"You have {max(1, round(self.goal_minutes * 0.2))} minutes left."
        else:
            warning_at = goal_seconds - 5 * 60
            warning_text = "You have 5 minutes left of your practice goal."

        commands: list[Command] = []
        if self.active_seconds >= halfway and "halfway" not in self._announced:
            self._announced.add("halfway")
            commands.append(Speak(
                f"You have practiced {round(self.active_seconds / 60)} minutes "
                f"of {self.goal_minutes}.", interrupt=False))
        if self.active_seconds >= warning_at and "warning" not in self._announced:
            self._announced.add("warning")
            commands.append(Speak(warning_text, interrupt=False))
        if self.active_seconds >= goal_seconds and "goal" not in self._announced:
            self._announced.add("goal")
            commands.append(Tone(ToneName.LESSON_DONE))
            commands.append(Speak(
                f"You have reached your goal of {self.goal_minutes} minutes. "
                "You can keep practicing.", interrupt=False))
        return commands

    def _goal_seconds(self) -> float:
        return float((self.goal_minutes or 0) * 60)


def summarize(attempts: Sequence[AttemptRecord], today: date) -> StatsSummary:
    practice = [a for a in attempts if a.kind in ("practice", "race")]
    practice.sort(key=lambda attempt: attempt.started_at)
    recent = practice[-10:]

    lessons = {attempt.lesson_id for attempt in practice}
    average_accuracy = (sum(a.accuracy for a in recent) / len(recent)) if recent else 0.0
    average_wpm = (sum(a.wpm for a in recent) / len(recent)) if recent else 0.0
    best_wpm = max((a.wpm for a in practice), default=0.0)

    today_iso = today.isoformat()
    week_start = (today - timedelta(days=6)).isoformat()
    minutes_today = sum(
        a.active_seconds for a in practice if a.started_at[:10] == today_iso) / 60
    minutes_this_week = sum(
        a.active_seconds for a in practice
        if week_start <= a.started_at[:10] <= today_iso) / 60

    merged: dict[str, KeyStat] = {}
    for attempt in practice:
        for stat in attempt.key_stats:
            current = merged.get(stat.key, KeyStat(stat.key, 0, 0))
            merged[stat.key] = KeyStat(
                key=stat.key,
                presses=current.presses + stat.presses,
                errors=current.errors + stat.errors,
            )
    weakest = tuple(sorted(merged.values(),
                           key=lambda stat: (stat.errors, stat.presses), reverse=True)[:5])

    return StatsSummary(
        lessons_completed=len(lessons),
        current_lesson=max(lessons, default=0),
        average_accuracy=average_accuracy,
        average_wpm=average_wpm,
        best_wpm=best_wpm,
        minutes_today=minutes_today,
        minutes_this_week=minutes_this_week,
        weakest_keys=weakest,
    )
