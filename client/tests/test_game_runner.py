from steadytype_client.game_runner import GameRunner
from steadytype_engine.buffer import TextBuffer
from steadytype_engine.games.base import GamePrompt
from steadytype_engine.keys import Key, KeyEvent


class Once:
    """A game whose answer is always the word ab."""

    def make(self, rng, words):
        buffer = TextBuffer("a")
        buffer.cursor = 1
        return GamePrompt(intro="Type ab.", buffer=buffer, target="ab", help="")

    def is_complete(self, buffer):
        return buffer.text == "ab"


def event(char):
    return KeyEvent(kind="down", key=Key.SPACE, text=char, modifiers=frozenset(),
                    side=None, is_repeat=False, scan_code=0, timestamp=0.0)


def test_five_correct_rounds_save_one_game_record():
    saved, said = [], []
    runner = GameRunner(Once(), save=saved.append,
                        speak=lambda text, interrupt=False: said.append(text), rounds=5)
    runner.start()
    for _ in range(5):
        runner.handle(event("b"))
    assert runner.done
    assert runner.completed == 5
    assert len(saved) == 1
    assert saved[0].kind == "game"


def test_escape_ends_the_game_early():
    saved = []
    runner = GameRunner(Once(), save=saved.append,
                        speak=lambda text, interrupt=False: None, rounds=5)
    runner.start()
    runner.handle(event("x"))
    runner.handle(KeyEvent(kind="down", key=Key.ESCAPE, text=None,
                           modifiers=frozenset(), side=None, is_repeat=False,
                           scan_code=0, timestamp=0.0))
    assert runner.done
    assert len(saved) == 1
