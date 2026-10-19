"""Dictation: speak a chunk, let the student type it, never correct mid-word."""

from __future__ import annotations

from dataclasses import dataclass

from .commands import Command, Speak
from .keys import Key, KeyEvent
from .preferences import Echo, Preferences


@dataclass(frozen=True)
class Passage:
    title: str
    text: str


@dataclass(frozen=True)
class DictationResult:
    accuracy: float
    wpm: float
    misspelled: tuple[str, ...]


def chunk_text(text: str, size: int = 3) -> tuple[str, ...]:
    words = text.split()
    if not words:
        return ()
    return tuple(" ".join(words[i:i + size]) for i in range(0, len(words), size))


class DictationSession:
    def __init__(self, passage: Passage, prefs: Preferences) -> None:
        self.passage = passage
        self.prefs = prefs
        self.chunks = chunk_text(passage.text)
        self.chunk_index = 0
        self.typed = ""
        self._done = False
        self._started_timestamp: float | None = None
        self._last_timestamp: float | None = None
        self._active_seconds = 0.0

    def start(self) -> list[Command]:
        return [Speak(self.chunks[0], interrupt=True)]

    def handle(self, event: KeyEvent) -> list[Command]:
        if event.kind != "down" or self._done or event.is_repeat:
            return []
        if event.key is Key.ESCAPE:
            self._done = True
            return [Speak("Dictation finished.", interrupt=True)]

        self._account_time(event.timestamp)
        if event.key is Key.ENTER:
            return self._advance()
        if event.text is None:
            return []
        self.typed += event.text
        commands = self._echo(event.text)
        if len(self.typed) >= len(self._current_chunk()):
            commands.extend(self._advance())
        return commands

    def finish(self) -> DictationResult:
        expected = self.passage.text.split()
        typed = self.typed.split()
        misspelled = tuple(
            want for index, want in enumerate(expected)
            if index >= len(typed) or typed[index] != want
        )
        correct = len(expected) - len(misspelled)
        accuracy = correct / len(expected) * 100 if expected else 0.0
        minutes = self._active_seconds / 60
        wpm = (len(self.typed) / 5) / minutes if minutes > 0 else 0.0
        return DictationResult(accuracy=accuracy, wpm=wpm, misspelled=misspelled)

    # -- internals ------------------------------------------------------
    def _current_chunk(self) -> str:
        return self.chunks[min(self.chunk_index, len(self.chunks) - 1)]

    def _advance(self) -> list[Command]:
        self.chunk_index += 1
        if self.chunk_index >= len(self.chunks):
            self._done = True
            return [Speak("Dictation complete.", interrupt=True)]
        return [Speak(self.chunks[self.chunk_index], interrupt=True)]

    def _echo(self, char: str) -> list[Command]:
        if self.prefs.echo is Echo.OFF:
            return []
        if self.prefs.echo is Echo.EVERY_KEY:
            return [Speak(char)]
        if char == " ":
            word = self.typed.split()[-1] if self.typed.split() else ""
            if word:
                return [Speak(word)]
        return []

    def _account_time(self, timestamp: float) -> None:
        if self._started_timestamp is None:
            self._started_timestamp = timestamp
        if self._last_timestamp is not None:
            gap = timestamp - self._last_timestamp
            if 0 < gap <= 5:
                self._active_seconds += gap
        self._last_timestamp = timestamp
