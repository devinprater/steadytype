from steadytype_client.race import RACE_PASSAGE, RaceRunner
from steadytype_engine.keys import Key, KeyEvent

CLOCK = [0.0]


def event(char):
    return KeyEvent(kind="down", key=Key.SPACE, text=char, modifiers=frozenset(),
                    side=None, is_repeat=False, scan_code=0, timestamp=0.0)


def test_beating_the_pacer_is_said_plainly():
    global CLOCK
    CLOCK = [0.0]
    said, saved = [], []
    race = RaceRunner(save=saved.append,
                      speak=lambda text, interrupt=False: said.append(text),
                      target_wpm=10, seconds=60, now=lambda: CLOCK[0])
    race.start()
    for char in RACE_PASSAGE.text:
        race.handle(event(char))
        CLOCK[0] += 0.04
    CLOCK[0] = 61.0
    race.tick(CLOCK[0])
    assert race.done
    assert len(saved) == 1
    assert saved[0].kind == "timed_test"
    assert "beat the pacer" in said[-1]
