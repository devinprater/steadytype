import random

from steadytype_engine.games.missing_letter import MissingLetterGame
from steadytype_engine.keys import Key, KeyEvent, Side


def _key(char: str) -> KeyEvent:
    return KeyEvent(kind="down", key=Key(char), text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_removes_exactly_one_letter_and_keeps_the_target():
    game = MissingLetterGame()
    prompt = game.make(random.Random(1), ["add", "dad", "sad"])
    assert len(prompt.buffer.text) == len(prompt.target) - 1
    assert prompt.target in {"add", "dad", "sad"}
    assert not game.is_complete(prompt.buffer)


def test_typing_the_missing_letter_completes_the_game():
    game = MissingLetterGame()
    prompt = game.make(random.Random(1), ["add"])
    index = next(i for i in range(len(prompt.target))
                 if i >= len(prompt.buffer.text)
                 or prompt.buffer.text[i] != prompt.target[i])
    prompt.buffer.cursor = index
    prompt.buffer.handle(_key(prompt.target[index]))
    assert game.is_complete(prompt.buffer)
