from steadytype_engine.keys import Key, KeyEvent
from steadytype_engine.timed_test import TimedTest


class Passage:
    text = "the quick brown fox jumps over the lazy dog"


def test_a_finished_test_produces_a_timed_test_record():
    clock = [0.0]
    test = TimedTest(Passage(), seconds=60, now=lambda: clock[0])
    test.start()
    for char in test.passage.text:
        test.handle(KeyEvent(kind="down", key=Key.SPACE, text=char, modifiers=frozenset(),
                            side=None, is_repeat=False, scan_code=0, timestamp=0.0))
        clock[0] += 0.05
    record = test.attempt_record(lesson_id=72)
    assert record.kind == "timed_test"
    assert record.lesson_id == 72
    assert record.wpm > 0
    assert record.errors == 0


def test_a_test_that_never_finished_still_records_what_was_typed():
    clock = [0.0]
    test = TimedTest(Passage(), seconds=60, now=lambda: clock[0])
    test.start()
    for char in "the quick":
        test.handle(KeyEvent(kind="down", key=Key.SPACE, text=char, modifiers=frozenset(),
                            side=None, is_repeat=False, scan_code=0, timestamp=0.0))
    clock[0] = 30.0
    record = test.attempt_record()
    assert record.kind == "timed_test"
    assert 0 <= record.active_seconds <= 60
