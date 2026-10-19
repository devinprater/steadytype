"""Speech through Prism, with a recording fake for tests."""

from __future__ import annotations

from typing import Protocol


class SpeechUnavailable(Exception):
    """Raised when neither a screen reader nor a speech engine can be reached."""


class SpeechEngine(Protocol):
    name: str

    def speak(self, text: str, interrupt: bool = False) -> None: ...
    def braille(self, text: str) -> None: ...
    def configure(self, rate: float, pitch: float, volume: float, voice: str | None) -> None: ...
    def stop(self) -> None: ...


class FakeSpeech:
    name = "silent"

    def __init__(self) -> None:
        self.spoken: list[tuple[str, bool]] = []
        self.brailled: list[str] = []

    def speak(self, text: str, interrupt: bool = False) -> None:
        self.spoken.append((text, interrupt))

    def braille(self, text: str) -> None:
        self.brailled.append(text)

    def configure(self, rate: float, pitch: float, volume: float, voice: str | None) -> None:
        pass

    def stop(self) -> None:
        pass


def _load_prism():
    import prism

    return prism


class PrismSpeech:
    def __init__(self, backend=None) -> None:
        if backend is None:
            module = _load_prism()
            try:
                backend = module.Context().create_best()
            except Exception as error:
                raise SpeechUnavailable(
                    "No screen reader or speech engine was found. "
                    "Start your screen reader, or install a speech voice, then try again."
                ) from error
            if backend is None:
                raise SpeechUnavailable(
                    "No screen reader or speech engine was found. "
                    "Start your screen reader, or install a speech voice, then try again."
                )
        self._backend = backend

    @property
    def name(self) -> str:
        return self._backend.name

    def speak(self, text: str, interrupt: bool = False) -> None:
        self._backend.speak(text, interrupt)

    def braille(self, text: str) -> None:
        try:
            self._backend.braille(text)
        except Exception:  # noqa: BLE001, S110 - a backend without braille must not stop speech
            pass

    def configure(self, rate: float, pitch: float, volume: float,
                  voice: str | None) -> None:
        self._backend.rate = rate
        self._backend.pitch = pitch
        self._backend.volume = volume
        if voice is not None:
            self._backend.voice = voice

    def stop(self) -> None:
        self._backend.stop()


class SaySpeech:
    """macOS always has the system voice, even with no screen reader running."""

    name = "macOS voice"

    def __init__(self, rate: float = 180.0) -> None:
        self._rate = rate
        self._process = None

    def speak(self, text: str, interrupt: bool = False) -> None:
        import subprocess

        if interrupt:
            self.stop()
        self._process = subprocess.Popen(["/usr/bin/say", "-r", str(int(self._rate)), text])

    def braille(self, text: str) -> None:
        pass

    def configure(self, rate: float, pitch: float, volume: float,
                  voice: str | None) -> None:
        self._rate = max(80.0, min(400.0, 180.0 * float(rate or 1)))

    def stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
        self._process = None


def create_speech() -> SpeechEngine:
    try:
        return PrismSpeech()
    except Exception as error:
        import sys

        if sys.platform == "darwin":
            return SaySpeech()
        raise SpeechUnavailable(
            "No screen reader or speech engine was found. "
            "Start your screen reader, or install a speech voice, then try again."
        ) from error
