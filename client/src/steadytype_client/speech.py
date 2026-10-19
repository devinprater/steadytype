"""Speech through Prism, with a recording fake for tests."""

from __future__ import annotations

import queue
import threading
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
    reason: str = ""

    def __init__(self, backend=None) -> None:
        if backend is None:
            module = _load_prism()
            try:
                backend = module.Context().create_best()
            except Exception as error:
                PrismSpeech.reason = f"{type(error).__name__}: {error}"
                raise SpeechUnavailable(
                    "No screen reader or speech engine was found. "
                    "Start your screen reader, or install a speech voice, then try again."
                ) from error
            if backend is None:
                PrismSpeech.reason = "create_best() returned nothing"
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
    """macOS system voice, spoken one line at a time from a queue."""

    name = "macOS voice"

    def __init__(self, rate: float = 210.0) -> None:
        self._rate = rate
        self._voice: str | None = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._current = None
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def _spawn(self, text: str):
        import subprocess

        command = ["/usr/bin/say", "-r", str(int(self._rate))]
        if self._voice:
            command += ["-v", self._voice]
        return subprocess.Popen(command + [text])

    def _worker(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:
                return
            with self._lock:
                self._current = self._spawn(text)
                process = self._current
            try:
                process.wait()
            finally:
                with self._lock:
                    if self._current is process:
                        self._current = None

    def _ensure_worker(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def speak(self, text: str, interrupt: bool = False) -> None:
        if interrupt:
            self.stop()
        self._ensure_worker()
        self._queue.put(text)

    def braille(self, text: str) -> None:
        pass

    def configure(self, rate: float, pitch: float, volume: float,
                  voice: str | None) -> None:
        self._rate = max(120.0, min(400.0, 210.0 * float(rate or 1)))
        if voice:
            self._voice = voice

    def stop(self) -> None:
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            pass
        with self._lock:
            process = self._current
            if process is not None and process.poll() is None:
                process.terminate()
            self._current = None


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
