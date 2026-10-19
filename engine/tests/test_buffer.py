from steadytype_engine.buffer import TextBuffer
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def _key(key, text=None, mods=frozenset()):
    return KeyEvent(kind="down", key=key, text=text, modifiers=mods,
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_right_arrow_speaks_the_character_to_the_right():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.RIGHT))
    assert (buf.cursor, result.speech) == (1, "a")


def test_control_right_moves_by_word():
    buf = TextBuffer("one two")
    buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.CONTROL})))
    assert buf.cursor == 4


def test_shift_right_selects_and_speaks_the_selection():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    assert buf.selection() == (0, 1)
    assert result.speech == "c"


def test_delete_removes_to_the_right_and_speaks_the_word():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.DELETE))
    assert buf.text == "at"
    assert result.speech == "at"


def test_backspace_removes_to_the_left():
    buf = TextBuffer("cat")
    buf.handle(_key(Key.RIGHT))
    buf.handle(_key(Key.BACKSPACE))
    assert buf.text == "at"


def test_printable_key_replaces_the_selection():
    buf = TextBuffer("cat")
    buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    buf.handle(_key(Key.D, text="d"))
    assert buf.text == "dat"
