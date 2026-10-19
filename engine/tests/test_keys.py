import pytest
from steadytype_engine.keys import Key, KeyEvent, Side


def test_letter_event_carries_the_produced_character():
    event = KeyEvent(
        kind="down", key=Key.A, text="a", modifiers=frozenset(),
        side=Side.NONE, is_repeat=False, scan_code=30, timestamp=0.0,
    )
    assert event.text == "a"


@pytest.mark.parametrize(
    ("name", "token"),
    [("COMMA", "comma"), ("SPACE", "space"), ("NUMPAD_ENTER", "numpad_enter"),
     ("LEFT_SHIFT", "left_shift"), ("PAGE_UP", "page_up"), ("F12", "f12")],
)
def test_key_tokens_are_stable(name, token):
    assert Key[token.upper()].value == token


def test_every_course_key_exists():
    names = [
        *(chr(c) for c in range(ord("a"), ord("z") + 1)),
        *(str(d) for d in range(10)),
        "space", "enter", "numpad_enter", "tab", "escape", "backspace", "delete",
        "insert", "home", "end", "page_up", "page_down", "up", "down", "left",
        "right", *(f"f{n}" for n in range(1, 13)), "left_shift", "right_shift",
        "left_control", "right_control", "left_alt", "right_alt", "left_meta",
        "right_meta", "caps_lock", "num_lock", "comma", "period", "slash",
        "semicolon", "apostrophe", "left_bracket", "right_bracket", "backslash",
        "grave", "minus", "equals", *(f"numpad_{d}" for d in range(10)),
        "numpad_add", "numpad_subtract", "numpad_multiply", "numpad_divide",
        "numpad_decimal", "unknown",
    ]
    for name in names:
        assert Key(name) is not None
