import sys

import pytest
from steadytype_client.speech import FakeSpeech, SpeechUnavailable, create_speech


def test_fake_records_speech_and_interrupts():
    speech = FakeSpeech()
    speech.speak("right")
    speech.speak("you need d", interrupt=True)
    assert speech.spoken == [("right", False), ("you need d", True)]


@pytest.mark.skipif(sys.platform == "darwin",
                    reason="macOS falls back to the system voice")
def test_create_speech_reports_a_plain_failure(monkeypatch):
    def boom():
        raise SpeechUnavailable("No screen reader or speech engine was found.")
    monkeypatch.setattr("steadytype_client.speech._load_prism", boom)
    with pytest.raises(SpeechUnavailable, match="No screen reader"):
        create_speech()


class FakeBackend:
    name = "Fake reader"
    def __init__(self):
        self.said, self.brailled = [], []
        self.rate = self.pitch = self.volume = 0.5
        self.voice = None
    def speak(self, text, interrupt=False):
        self.said.append((text, interrupt))
    def braille(self, text):
        self.brailled.append(text)
    def stop(self):
        self.stopped = True


def test_prism_adapter_maps_every_call():
    from steadytype_client.speech import PrismSpeech
    backend = FakeBackend()
    speech = PrismSpeech(backend)
    speech.speak("right")
    speech.braille("right")
    speech.configure(rate=0.7, pitch=0.4, volume=0.9, voice="Alex")
    speech.stop()
    assert backend.said == [("right", False)]
    assert backend.brailled == ["right"]
    assert (backend.rate, backend.pitch, backend.volume, backend.voice) == (0.7, 0.4, 0.9, "Alex")
    assert backend.stopped
