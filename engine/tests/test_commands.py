from steadytype_engine.commands import Speak, Tone, ToneName


def test_speak_is_value_equal():
    assert Speak("right") == Speak("right", interrupt=False)


def test_tone_names_are_stable():
    assert ToneName.CORRECT == "correct"
    assert Tone(ToneName.WRONG).name == "wrong"
