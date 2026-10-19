from datetime import date

import pytest

from steadytype_engine.commands import Speak
from steadytype_engine.practice import PracticeClock, summarize


def test_goal_announces_halfway_warning_and_finish_once():
    clock = PracticeClock(goal_minutes=40)
    clock.add_active_seconds(20 * 60)
    assert any("20" in c.text for c in clock.announcements())
    assert clock.announcements() == []
    clock.add_active_seconds(15 * 60)
    assert any("5 minutes" in c.text for c in clock.announcements())
    clock.add_active_seconds(5 * 60)
    assert any(isinstance(c, Speak) and "goal" in c.text for c in clock.announcements())
    assert clock.goal_reached
    assert clock.announcements() == []


def test_no_goal_never_announces():
    clock = PracticeClock(goal_minutes=None)
    clock.add_active_seconds(3600)
    assert clock.announcements() == []
    assert clock.minutes_today == 60


def test_summary_averages_the_last_ten_practice_attempts(attempts):
    summary = summarize(attempts, today=date(2026, 10, 19))
    assert summary.lessons_completed == 3
    assert summary.average_wpm == pytest.approx(30.0)
    assert summary.best_wpm == 45.0
    assert [key.key for key in summary.weakest_keys][:2] == ["p", "q"]
