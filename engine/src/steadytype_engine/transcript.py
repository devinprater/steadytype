"""Turn a lesson run into text, for tests and for the command-line harness."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from .commands import Command, Display, EndLesson, SaveAttempt, Speak, Tone
from .commands import ToneName
from .keys import Key, KeyEvent, Side
from .lesson import EndKey, Lesson, TaskKind
from .loader import load_lesson
from .preferences import Preferences
from .scoring import Goals
from .session import LessonSession, SessionState, result_commands


def format_command(command: Command) -> str:
    if isinstance(command, Speak):
        return f"SPEAK: {command.text}"
    if isinstance(command, Tone):
        return f"TONE: {command.name}"
    if isinstance(command, Display):
        return f"DISPLAY: {command.state}"
    if isinstance(command, SaveAttempt):
        return "SAVE"
    if isinstance(command, EndLesson):
        return "END"
    return f"UNKNOWN: {command!r}"


class TranscriptRecorder:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def record(self, commands: Iterable[Command]) -> None:
        for command in commands:
            self._lines.append(format_command(command))

    def lines(self) -> list[str]:
        return list(self._lines)


def run_script(lesson: Lesson, keys: Sequence[KeyEvent],
               prefs: Preferences | None = None) -> list[str]:
    prefs = prefs or Preferences()
    session = LessonSession(lesson, prefs, Goals())
    recorder = TranscriptRecorder()
    recorder.record(session.start())
    for event in keys:
        recorder.record(session.handle(event))
    if session.state is SessionState.LESSON_DONE:
        recorder.record(result_commands(session.finish(), prefs))
    return recorder.lines()


def keys_for(lesson: Lesson) -> list[KeyEvent]:
    """The keys that complete a lesson exactly, for generating a transcript."""
    keys: list[KeyEvent] = []
    for task in lesson.tasks:
        for _ in range(lesson.repeat):
            if task.kind is TaskKind.TEXT:
                for char in task.text:
                    keys.append(_event(Key.SPACE if char == " " else Key(char), char))
            else:
                keys.append(_event(Key(task.text.lower()), None))
            if lesson.end_key is EndKey.SPACE:
                keys.append(_event(Key.SPACE, " "))
            elif lesson.end_key is EndKey.ENTER:
                keys.append(_event(Key.ENTER, None))
    return keys


def _event(key: Key, text: str | None) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=text, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a lesson and print what it says.")
    parser.add_argument("lesson", type=Path)
    parser.add_argument("--update", type=Path, help="write the transcript to this file")
    args = parser.parse_args(argv)

    lesson = load_lesson(args.lesson)
    text = "\n".join(run_script(lesson, keys_for(lesson)))
    if args.update:
        args.update.parent.mkdir(parents=True, exist_ok=True)
        args.update.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.update}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
