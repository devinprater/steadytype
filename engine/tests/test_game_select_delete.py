import random

from steadytype_engine.games.select_delete import SelectDeleteGame
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def _key(key: Key, mods: frozenset = frozenset()) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=None, modifiers=mods,
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_has_exactly_one_extra_word():
    game = SelectDeleteGame()
    prompt = game.make(random.Random(3), ["the cat sat on the mat"])
    assert len(prompt.buffer.text.split()) == len(prompt.target.split()) + 1


def test_selecting_the_extra_word_and_deleting_it_completes_the_game():
    game = SelectDeleteGame()
    prompt = game.make(random.Random(3), ["the cat sat on the mat"])
    extra = next(w for w in prompt.buffer.text.split() if w not in prompt.target.split())
    start = prompt.buffer.text.index(extra)
    prompt.buffer.cursor = start
    for _ in range(len(extra)):
        prompt.buffer.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    prompt.buffer.handle(_key(Key.DELETE))
    assert game.is_complete(prompt.buffer)
