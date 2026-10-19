import random

from steadytype_engine.games.wrong_letter import WrongLetterGame
from steadytype_engine.keys import Key, KeyEvent, Side


def _key(key: Key, text: str | None = None) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=text, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_has_one_wrong_letter_and_a_different_character():
    game = WrongLetterGame()
    prompt = game.make(random.Random(2), ["cat"])
    assert len(prompt.buffer.text) == 3
    assert prompt.buffer.text != prompt.target
    assert sum(a != b for a, b in zip(prompt.buffer.text, prompt.target)) == 1


def test_deleting_and_retyping_the_letter_completes_the_game():
    game = WrongLetterGame()
    prompt = game.make(random.Random(2), ["cat"])
    index = next(i for i in range(len(prompt.target))
                 if prompt.buffer.text[i] != prompt.target[i])
    prompt.buffer.cursor = index
    prompt.buffer.handle(_key(Key.DELETE))
    prompt.buffer.handle(_key(Key(prompt.target[index]), text=prompt.target[index]))
    assert game.is_complete(prompt.buffer)
