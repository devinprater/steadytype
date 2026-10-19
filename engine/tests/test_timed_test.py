from steadytype_engine.dictation import Passage
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.timed_test import TestState, TimedTest


def _key(char: str) -> KeyEvent:
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def make_test(**kwargs) -> TimedTest:
    return TimedTest(Passage("T", "the quick brown fox"), seconds=300, **kwargs)


def test_reading_the_passage_speaks_it_once():
    test = make_test()
    assert "the quick brown fox" in test.read_passage()[0].text


def test_a_wrong_character_is_accepted_without_feedback():
    test = make_test()
    test.start()
    commands = test.handle(_key("x"))
    assert test.typed == "x"
    assert commands == []


def test_backspace_is_ignored_when_not_allowed():
    test = make_test(allow_backspace=False)
    test.start()
    test.handle(_key("a"))
    test.handle(KeyEvent(kind="down", key=Key.BACKSPACE, text=None,
                         modifiers=frozenset(), side=Side.NONE,
                         is_repeat=False, scan_code=0, timestamp=0.0))
    assert test.typed == "a"


def test_one_minute_warning_is_spoken_once():
    test = TimedTest(Passage("T", "the quick brown fox"), seconds=300,
                     now=lambda: 0.0)
    test.start()
    assert any("one minute" in c.text for c in test.tick(240.0))
    assert test.tick(241.0) == []


def test_finishing_at_zero_scores_the_test():
    clock = {"now": 0.0}
    test = TimedTest(Passage("T", "the quick brown fox"), seconds=60,
                     now=lambda: clock["now"])
    test.start()
    for char in "the quick brown fox":
        test.handle(_key(char))
    clock["now"] = 60.0
    result = test.finish()
    assert test.state is TestState.FINISHED
    assert result.error_words == 0
