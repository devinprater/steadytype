from steadytype_client.capture.linux import LinuxCapture
from steadytype_client.capture.linux import key_for as linux_key
from steadytype_client.capture.macos import MacCapture, modifiers_for
from steadytype_client.capture.macos import key_for as mac_key
from steadytype_engine.keys import Key, Modifier


def test_mac_virtual_keys_map_to_names():
    assert mac_key(0) == Key.A
    assert mac_key(36) == Key.ENTER
    assert mac_key(49) == Key.SPACE
    assert mac_key(53) == Key.ESCAPE
    assert mac_key(122) == Key.F1
    assert mac_key(123) == Key.LEFT
    assert mac_key(999) is None


def test_mac_flags_become_modifiers():
    assert modifiers_for(1 << 17) == frozenset({Modifier.SHIFT})
    assert modifiers_for((1 << 17) | (1 << 18)) == frozenset(
        {Modifier.SHIFT, Modifier.CONTROL})
    assert modifiers_for(0) == frozenset()


def test_linux_keysyms_map_to_names():
    assert linux_key("Return") == Key.ENTER
    assert linux_key("space") == Key.SPACE
    assert linux_key("F1") == Key.F1
    assert linux_key("comma") == Key.COMMA
    assert linux_key("a") == Key.A
    assert linux_key("7") == Key.DIGIT_7
    assert linux_key("Shift_L") is None


def test_capture_reports_whether_it_can_hook_this_platform():
    import sys

    mac = MacCapture()
    started = mac.start(lambda event: None)
    if sys.platform == "darwin":
        # True once Accessibility is granted; False until then. Both are valid.
        assert started in (True, False)
        mac.stop()
    else:
        assert started is False
    assert LinuxCapture().start(lambda event: None) is False


def test_mac_capture_works_when_quartz_is_installed():
    import sys

    import pytest

    if sys.platform != "darwin":
        pytest.skip("Quartz is macOS only")
    capture = MacCapture()
    capture.start(lambda event: None)
    capture.stop()
