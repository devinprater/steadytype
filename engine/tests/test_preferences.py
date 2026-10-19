import pytest

from steadytype_engine.preferences import Echo, Feedback, Pitch, Preferences, TypingExperience, Verbosity


def test_defaults_match_the_spec():
    prefs = Preferences()
    assert prefs.double_press_ms == 500
    assert prefs.feedback is Feedback.BOTH
    assert prefs.verbosity is Verbosity.STANDARD
    assert prefs.typing_experience is TypingExperience.SOME
    assert prefs.echo is Echo.WORDS
    assert prefs.echo_pitch is Pitch.HIGH
    assert prefs.one_handed is False
    assert prefs.laptop_keyboard is False
    assert prefs.tones is True


def test_double_press_window_is_bounded():
    with pytest.raises(ValueError, match="double_press_ms"):
        Preferences(double_press_ms=200)
    with pytest.raises(ValueError, match="double_press_ms"):
        Preferences(double_press_ms=1000)
