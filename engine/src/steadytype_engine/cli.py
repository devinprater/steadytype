"""Run a lesson from the terminal. The key names come from standard input."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .keys import Key, KeyEvent, Side
from .lesson import Lesson
from .loader import load_lesson
from .preferences import Preferences
from .session import LessonSession, SessionState
from .transcript import format_command

MODIFIERS = {
    "left_shift": Key.LEFT_SHIFT, "right_shift": Key.RIGHT_SHIFT,
    "left_control": Key.LEFT_CONTROL, "right_control": Key.RIGHT_CONTROL,
    "left_alt": Key.LEFT_ALT, "right_alt": Key.RIGHT_ALT,
}


def parse_key(name: str) -> KeyEvent | None:
    name = name.strip().lower()
    if not name:
        return None
    parts = name.split("+")
    base = parts[-1]
    modifiers = frozenset(p for p in parts[:-1])
    try:
        key = Key(base)
    except ValueError:
        if "=" in base:
            key, _, produced = base.partition("=")
            try:
                key_value = Key(key)
            except ValueError:
                return None
            return KeyEvent(kind="down", key=key_value, text=produced, modifiers=modifiers,
                            side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)
        return None
    text = key.value if len(key.value) == 1 else (" " if key is Key.SPACE else None)
    return KeyEvent(kind="down", key=key, text=text, modifiers=modifiers,
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def run(lesson: Lesson, prefs: Preferences, lines: Sequence[str]) -> int:
    session = LessonSession(lesson, prefs, now=lambda: 0.0)
    for command in session.start():
        print(format_command(command))
    escapes = 0
    for raw in lines:
        event = parse_key(raw)
        if event is None:
            print(f"ERROR: unknown key {raw.strip()}")
            continue
        if event.key is Key.ESCAPE:
            escapes += 1
        else:
            escapes = 0
        for command in session.handle(event):
            print(format_command(command))
        if session.state is SessionState.LESSON_DONE:
            print("LESSON COMPLETE")
            break
        if escapes >= 3:
            print("QUIT")
            break
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a SteadyType lesson in the terminal.")
    parser.add_argument("lesson", type=Path)
    parser.add_argument("--prefs", choices=["none", "one-handed", "laptop"], default="none")
    args = parser.parse_args(argv)

    prefs = Preferences(one_handed=args.prefs == "one-handed",
                        laptop_keyboard=args.prefs == "laptop")
    return run(load_lesson(args.lesson), prefs, sys.stdin.read().splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
