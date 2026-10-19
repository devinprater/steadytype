"""An editable text buffer with a cursor and a selection, for games and drills."""

from __future__ import annotations

from dataclasses import dataclass

from .keys import Key, KeyEvent, Modifier


@dataclass(frozen=True)
class BufferResult:
    changed: bool
    speech: str


class TextBuffer:
    def __init__(self, text: str) -> None:
        self.chars = list(text)
        self.cursor = 0
        self.anchor: int | None = None

    @property
    def text(self) -> str:
        return "".join(self.chars)

    def selection(self) -> tuple[int, int] | None:
        if self.anchor is None or self.anchor == self.cursor:
            return None
        return (min(self.anchor, self.cursor), max(self.anchor, self.cursor))

    def handle(self, event: KeyEvent) -> BufferResult:
        if event.kind != "down":
            return BufferResult(False, self._speak_position())

        mods = event.modifiers
        shift = Modifier.SHIFT in mods
        control = Modifier.CONTROL in mods

        if event.key is Key.LEFT:
            return self._move(-1, shift, control)
        if event.key is Key.RIGHT:
            return self._move(1, shift, control)
        if event.key is Key.HOME:
            return self._jump(0, shift)
        if event.key is Key.END:
            return self._jump(len(self.chars), shift)
        if event.key is Key.DELETE:
            return self._delete(forward=True)
        if event.key is Key.BACKSPACE:
            return self._delete(forward=False)
        if event.text:
            return self._insert(event.text)
        return BufferResult(False, self._speak_position())

    # -- movement -------------------------------------------------------
    def _move(self, direction: int, shift: bool, control: bool) -> BufferResult:
        if shift and self.anchor is None:
            self.anchor = self.cursor
        elif not shift:
            self.anchor = None

        if control:
            self.cursor = self._word_target(direction)
        else:
            self.cursor = max(0, min(len(self.chars), self.cursor + direction))
        return BufferResult(False, self._speak_position())

    def _jump(self, index: int, shift: bool) -> BufferResult:
        if shift and self.anchor is None:
            self.anchor = self.cursor
        elif not shift:
            self.anchor = None
        self.cursor = index
        return BufferResult(False, self._speak_position())

    def _word_target(self, direction: int) -> int:
        index = self.cursor
        if direction > 0:
            while index < len(self.chars) and not self.chars[index].isspace():
                index += 1
            while index < len(self.chars) and self.chars[index].isspace():
                index += 1
            return index
        index -= 1
        while index > 0 and self.chars[index].isspace():
            index -= 1
        while index > 0 and not self.chars[index - 1].isspace():
            index -= 1
        return max(0, index)

    # -- editing --------------------------------------------------------
    def _delete(self, forward: bool) -> BufferResult:
        span = self.selection()
        if span:
            start, end = span
            del self.chars[start:end]
            self.cursor = start
            self.anchor = None
            return BufferResult(True, self._speak_word())
        if forward:
            if self.cursor >= len(self.chars):
                return BufferResult(False, "end of line")
            del self.chars[self.cursor]
        else:
            if self.cursor == 0:
                return BufferResult(False, "beginning of line")
            del self.chars[self.cursor - 1]
            self.cursor -= 1
        return BufferResult(True, self._speak_word())

    def _insert(self, text: str) -> BufferResult:
        span = self.selection()
        if span:
            start, end = span
            del self.chars[start:end]
            self.cursor = start
            self.anchor = None
        self.chars[self.cursor:self.cursor] = list(text)
        self.cursor += len(text)
        return BufferResult(True, self._speak_word())

    # -- speech ---------------------------------------------------------
    def _speak_position(self) -> str:
        span = self.selection()
        if span:
            start, end = span
            selected = "".join(self.chars[start:end])
            return selected if selected else "blank"
        if self.cursor >= len(self.chars):
            return "end of line"
        char = self.chars[self.cursor]
        return "space" if char == " " else char

    def _speak_word(self) -> str:
        if not self.chars:
            return "blank"
        index = min(self.cursor, len(self.chars) - 1)
        start = index
        while start > 0 and not self.chars[start - 1].isspace():
            start -= 1
        end = index
        while end < len(self.chars) and not self.chars[end].isspace():
            end += 1
        word = "".join(self.chars[start:end])
        return word or "blank"
