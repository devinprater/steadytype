"""Regression tests for findings from the whole-branch review."""

from steadytype_engine.commands import Speak
from steadytype_engine.dictation import DictationSession, Passage
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.lesson import Lesson
from steadytype_engine.practice import PracticeClock
from steadytype_engine.preferences import Echo, Preferences
from steadytype_engine.scoring import Goals
from steadytype_engine.session import LessonSession, SessionState
from steadytype_engine.timed_test import TestState, TimedTest


def _press(key: Key, text: str | None = None) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=text, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def _chars(text: str) -> list[KeyEvent]:
    return [_press(Key.SPACE if c == " " else Key(c), c) for c in text]


def _lesson(end_key: str = "space") -> Lesson:
    return Lesson.from_dict({
        "schema": 1, "id": 99, "unit": 1, "ordinal": 99, "title": "Test",
        "teaches": ["a"], "kind": "keyboarding", "end_key": end_key,
        "repeat": 2, "intro": "Type a.", "tasks": [{"text": "a"}],
    })


# 1. Dictation advanced on a cumulative count compared with one chunk's length.
def test_dictation_speaks_every_chunk_in_order():
    session = DictationSession(Passage("t", "one two three four five six seven"),
                               Preferences(echo=Echo.OFF))
    session.start()
    spoken = []
    for event in _chars("one two three four five six seven"):
        spoken.extend(c.text for c in session.handle(event) if isinstance(c, Speak))
    assert any("four five six" in text for text in spoken)
    assert any("seven" in text for text in spoken)


def test_dictation_does_not_end_before_the_passage_is_typed():
    session = DictationSession(Passage("t", "one two three four five six seven"),
                               Preferences(echo=Echo.OFF))
    session.start()
    for event in _chars("one two three four"):
        session.handle(event)
    assert not session.finished


# 2. The timed test never ended at zero or on Escape.
def test_escape_finishes_the_timed_test():
    test = TimedTest(Passage("T", "the quick brown fox"), seconds=300,
                     now=lambda: 0.0)
    test.start()
    test.handle(_press(Key.ESCAPE))
    assert test.state is TestState.FINISHED


def test_tick_at_zero_finishes_the_timed_test():
    test = TimedTest(Passage("T", "the quick brown fox"), seconds=60,
                     now=lambda: 0.0)
    test.start()
    test.tick(60.0)
    assert test.state is TestState.FINISHED


# 3. Repeating instructions after the last task raised IndexError.
def test_repeat_instructions_after_the_lesson_does_not_crash():
    session = LessonSession(_lesson(), Preferences(), Goals(), now=lambda: 0.0)
    session.start()
    for _ in range(2):
        session.handle(_press(Key.A, "a"))
        session.handle(_press(Key.SPACE, " "))
    assert session.state is SessionState.LESSON_DONE
    commands = session.repeat_instructions()
    assert any(isinstance(c, Speak) and "finished" in c.text for c in commands)


# 4. Numpad Enter was rejected as the end key.
def test_numpad_enter_finishes_a_task_that_ends_with_enter():
    session = LessonSession(_lesson("enter"), Preferences(), Goals(), now=lambda: 0.0)
    session.start()
    session.handle(_press(Key.A, "a"))
    session.handle(_press(Key.NUMPAD_ENTER))
    assert session.current_repeat == 2


# 5. A single jump past the goal announced a false five-minute warning.
def test_a_jump_past_the_goal_does_not_warn_about_five_minutes():
    clock = PracticeClock(goal_minutes=40)
    clock.add_active_seconds(45 * 60)
    texts = [c.text for c in clock.announcements() if isinstance(c, Speak)]
    assert not any("5 minutes left" in text for text in texts)
    assert any("goal" in text for text in texts)


# 6. Shift and Caps Lock counted as wrong keys.
def test_modifier_and_lock_keys_are_ignored():
    session = LessonSession(_lesson(), Preferences(), Goals(), now=lambda: 0.0)
    session.start()
    assert session.handle(_press(Key.LEFT_SHIFT)) == []
    assert session.handle(_press(Key.CAPS_LOCK)) == []
    assert session.metrics.errors == 0
    assert session.position == 0
