from steadytype_client.dictation_runner import PASSAGES, DictationRunner
from steadytype_engine.keys import Key, KeyEvent
from steadytype_engine.preferences import Preferences


def event(char, key=None):
    return KeyEvent(kind="down", key=key or Key.SPACE, text=char,
                    modifiers=frozenset(), side=None, is_repeat=False,
                    scan_code=0, timestamp=0.0)


def test_typing_the_passage_saves_one_dictation_record():
    saved, said = [], []
    runner = DictationRunner(PASSAGES[0], Preferences(), save=saved.append,
                             speak=lambda text, interrupt=False: said.append(text))
    runner.start()
    for char in runner.passage.text:
        runner.handle(event(char))
    assert runner.done
    assert len(saved) == 1
    assert saved[0].kind == "dictation"
    assert saved[0].accuracy > 90
    assert "Dictation finished" in said[-1]


def test_escape_finishes_dictation_early():
    saved = []
    runner = DictationRunner(PASSAGES[1], Preferences(), save=saved.append,
                             speak=lambda text, interrupt=False: None)
    runner.start()
    runner.handle(event("set", key=Key.ESCAPE))
    assert runner.done
    assert len(saved) == 1
