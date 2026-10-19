from steadytype_engine.commands import Speak, Tone, ToneName
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.lesson import Lesson
from steadytype_engine.preferences import Feedback, Preferences
from steadytype_engine.scoring import Goals
from steadytype_engine.session import LessonSession, SessionState

LESSON = Lesson.from_dict({
    "schema": 1, "id": 1, "unit": 1, "ordinal": 1, "title": "Home row",
    "teaches": ["a"], "kind": "keyboarding", "end_key": "space",
    "repeat": 2, "intro": "Type the letter a.",
    "tasks": [{"text": "a"}, {"text": "aa"}],
})


def press(char: str, *, repeat: bool = False) -> KeyEvent:
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=repeat, scan_code=0, timestamp=0.0)


def make_session(**prefs) -> LessonSession:
    return LessonSession(LESSON, Preferences(**prefs), Goals(), now=lambda: 0.0)


def test_start_speaks_the_intro_then_the_first_task():
    commands = make_session().start()
    assert isinstance(commands[0], Speak)
    assert "a" in commands[1].text


def test_correct_key_advances_with_a_tone():
    session = make_session(feedback=Feedback.TONE)
    session.start()
    commands = session.handle(press("a"))
    assert any(isinstance(c, Tone) and c.name == ToneName.CORRECT for c in commands)
    assert session.position == 1


def test_wrong_key_does_not_advance_and_says_the_right_key():
    session = make_session(feedback=Feedback.WORD)
    session.start()
    commands = session.handle(press("s"))
    assert session.position == 0
    assert any(isinstance(c, Speak) and "a" in c.text for c in commands)


def test_second_wrong_key_gives_the_location():
    session = make_session()
    session.start()
    session.handle(press("s"))
    commands = session.handle(press("s"))
    assert any(isinstance(c, Speak) and "home row" in c.text for c in commands)


def test_held_wrong_key_counts_once_and_speaks_once():
    session = make_session()
    session.start()
    session.handle(press("s"))
    repeated = session.handle(press("s", repeat=True))
    assert repeated == []
    assert session.metrics.errors == 1


def test_end_key_before_the_text_is_finished_does_not_complete_the_task():
    session = make_session()
    session.start()
    session.handle(KeyEvent(kind="down", key=Key.SPACE, text=" ", modifiers=frozenset(),
                            side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0))
    assert session.state is SessionState.TYPING
    assert session.position == 0


def test_a_wrong_key_at_the_final_character_does_not_complete_the_task():
    session = make_session()
    session.start()
    session.handle(press("a"))
    session.handle(press("s"))
    assert session.position == 1
    assert session.current_repeat == 1
    assert session.state is SessionState.TYPING


def test_two_correct_repetitions_advance_to_the_next_task():
    session = make_session()
    session.start()
    for _ in range(2):
        session.handle(press("a"))
        session.handle(press(" "))
    assert session.task_index == 1
    assert session.position == 0
    assert session.current_repeat == 1


def test_a_key_without_text_counts_as_a_miss_and_says_unknown():
    session = make_session()
    session.start()
    commands = session.handle(KeyEvent(
        kind="down", key=Key.UNKNOWN, text=None, modifiers=frozenset(),
        side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0))
    assert session.metrics.errors == 1
    assert any(isinstance(c, Speak) and "unknown" in c.text for c in commands)
