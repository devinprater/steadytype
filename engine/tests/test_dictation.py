from steadytype_engine.dictation import DictationSession, Passage, chunk_text
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.preferences import Echo, Preferences


def _key(char: str) -> KeyEvent:
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_chunks_are_three_words_then_the_remainder():
    assert chunk_text("one two three four five") == ("one two three", "four five")


def test_first_chunk_is_spoken_on_start():
    session = DictationSession(Passage("t", "one two three four"), Preferences())
    commands = session.start()
    assert "one two three" in commands[0].text


def test_typing_the_whole_chunk_speaks_the_next_one_without_correcting():
    session = DictationSession(Passage("t", "one two three four"), Preferences())
    session.start()
    spoken = []
    for char in "one two three":
        spoken.extend(c for c in session.handle(_key(char)) if hasattr(c, "text"))
    assert any("four" in c.text for c in spoken)


def test_escape_ends_and_reports_misspelled_words():
    session = DictationSession(Passage("t", "cat sat"), Preferences(echo=Echo.OFF))
    session.start()
    for char in "cot sat":
        session.handle(_key(char))
    result = session.finish()
    assert result.misspelled == ("cat",)
