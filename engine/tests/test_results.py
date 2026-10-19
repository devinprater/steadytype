from steadytype_engine.commands import Speak
from steadytype_engine.preferences import Preferences
from steadytype_engine.scoring import AttemptRecord, KeyStat
from steadytype_engine.session import result_commands, tip_for


def test_tip_names_the_key_with_the_most_errors():
    stats = [KeyStat("a", 20, 1), KeyStat("p", 11, 6), KeyStat("s", 9, 2)]
    assert tip_for(stats) == (
        "Most of your misses were on p. On the top row, right hand, little finger.")


def test_tip_is_neutral_when_no_key_stands_out():
    stats = [KeyStat("a", 20, 0), KeyStat("s", 18, 1)]
    assert tip_for(stats) == "Keep your fingers on the home row."


def test_result_speech_has_no_joke_and_names_every_number():
    record = AttemptRecord(
        id="00000000-0000-0000-0000-000000000000", lesson_id=1, kind="practice",
        started_at="2026-10-19T14:00:00Z", ended_at="2026-10-19T14:01:36Z",
        active_seconds=96, characters=412, keypresses=430, errors=18,
        wpm=51.5, accuracy=95.81, real_accuracy=91.26, stars=4,
        key_stats=(KeyStat("p", 11, 6),), device_id="test",
        client_version="0.1.0",
    )
    text = " ".join(
        c.text for c in result_commands(record, Preferences()) if isinstance(c, Speak))
    assert "joke" not in text.lower()
    assert "accuracy" in text and "words per minute" in text and "stars" in text
