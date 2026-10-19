from steadytype_engine.names import key_name, localize


def test_option_is_not_called_alt_on_a_mac():
    assert key_name("alt", "darwin") == "Option"
    assert key_name("alt", "win32") == "Alt"
    assert key_name("alt", "linux") == "Alt"


def test_the_meta_key_has_three_names():
    assert key_name("meta", "darwin") == "Command"
    assert key_name("meta", "linux") == "Super"
    assert key_name("meta", "win32") == "Windows key"


def test_spoken_text_uses_the_local_names():
    text = "Control Alt Shift X also leaves."
    assert localize(text, "darwin") == "Control Option Shift X also leaves."
    assert localize(text, "linux") == text
    assert localize("Hold Super and press Tab.", "darwin") == "Hold Command and press Tab."
    assert localize("Press Alt once.", "linux") == "Press Alt once."
