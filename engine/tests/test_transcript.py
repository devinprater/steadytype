from pathlib import Path

from steadytype_engine.commands import Speak, Tone
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.loader import load_lesson
from steadytype_engine.transcript import format_command, run_script

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = Path(__file__).parent / "goldens" / "lesson_001.txt"


def _press(key: Key) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=None, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_commands_render_as_one_line_each():
    assert format_command(Speak("right")) == "SPEAK: right"
    assert format_command(Tone("correct")) == "TONE: correct"


def test_lesson_one_matches_its_golden_transcript():
    lesson = load_lesson(ROOT / "engine" / "tests" / "fixtures" / "lesson_one.yaml")
    keys = [_press(Key.F1), _press(Key.F1), _press(Key.F2), _press(Key.F2)]
    lines = run_script(lesson, keys)
    assert "\n".join(lines) == GOLDEN.read_text(encoding="utf-8").strip()
