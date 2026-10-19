from steadytype_client.prefs_json import from_dict, to_dict
from steadytype_engine.preferences import Echo, Feedback, Preferences


def test_round_trip_keeps_enums_and_numbers():
    prefs = Preferences(feedback=Feedback.TONE, echo=Echo.OFF, double_press_ms=700,
                        tones=False, rate=0.7)
    restored = from_dict(to_dict(prefs))
    assert restored == prefs
