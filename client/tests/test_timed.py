from steadytype_client.timed import TimedTestRunner
from steadytype_engine.dictation import Passage
from steadytype_engine.keys import Key, KeyEvent

SAID = []


def event(char):
    return KeyEvent(kind="down", key=Key.SPACE, text=char, modifiers=frozenset(),
                    side=None, is_repeat=False, scan_code=0, timestamp=0.0)


def make(seconds=60):
    passage = Passage(title="Test", text="the quick brown fox")
    saved = []
    runner = TimedTestRunner(passage, seconds, save=saved.append,
                             speak=lambda text, interrupt=False: SAID.append(text),
                             now=lambda: CLOCK[0])
    return runner, saved


CLOCK = [0.0]


def test_a_finished_test_saves_one_record_and_says_the_verdict():
    global CLOCK
    CLOCK = [0.0]
    runner, saved = make()
    runner.start()
    for char in "the quick brown fox":
        runner.handle(event(char))
        CLOCK[0] += 0.1
    runner.handle(event(" "))
    assert len(saved) == 0
    runner.tick(CLOCK[0])
    assert len(saved) == 0 or runner.done
    runner.handle(KeyEvent(kind="down", key=Key.ESCAPE, text=None,
                           modifiers=frozenset(), side=None, is_repeat=False,
                           scan_code=0, timestamp=0.0))
    assert runner.done
    assert len(saved) == 1
    assert saved[0].kind == "timed_test"
    assert "not a certificate" in SAID[-1]


def test_time_running_out_finishes_the_test():
    global CLOCK
    CLOCK = [0.0]
    runner, saved = make(seconds=10)
    runner.start()
    CLOCK[0] = 11.0
    runner.tick(CLOCK[0])
    assert runner.done
    assert len(saved) == 1
