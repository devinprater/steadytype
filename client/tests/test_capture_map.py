from steadytype_client.capture.windows import WM_KEYDOWN, WM_KEYUP, is_key_down, map_key
from steadytype_engine.keys import Key


def test_only_key_down_messages_become_events():
    assert is_key_down(WM_KEYDOWN)
    assert not is_key_down(WM_KEYUP)


def test_letters_and_shifted_letters():
    assert map_key(0x41, 0, False, False, False, False).text == "a"
    assert map_key(0x41, 0, False, True, False, False).text == "A"


def test_modifier_sides():
    assert map_key(0xA0, 0, False, False, False, False).key is Key.LEFT_SHIFT
    assert map_key(0xA1, 0, False, False, False, False).key is Key.RIGHT_SHIFT


def test_numpad_enter_and_arrows():
    assert map_key(0x0D, 0, True, False, False, False).key is Key.NUMPAD_ENTER
    assert map_key(0x25, 0, True, False, False, False).key is Key.LEFT


def test_punctuation_with_and_without_shift():
    assert map_key(0xBC, 0, False, False, False, False).text == ","
    assert map_key(0xBC, 0, False, True, False, False).text == "<"


def test_function_keys_and_space():
    assert map_key(0x70, 0, False, False, False, False).key is Key.F1
    assert map_key(0x20, 0, False, False, False, False).text == " "
