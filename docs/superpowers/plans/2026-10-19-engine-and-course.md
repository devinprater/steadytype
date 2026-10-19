# SteadyType Engine and Course Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the speech-independent lesson engine, the course format, and a command-line harness that runs real lessons without a window or a screen reader.

**Architecture:** A pure Python package turns normalized key events into commands (speak, tone, display, save). Lessons are YAML files compiled into the package's data. A command-line harness feeds key names from standard input and prints the spoken lines, so every lesson is runnable and testable before any client work begins.

**Tech Stack:** Python 3.13, PyYAML, pytest, ruff, uv, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-19-steadytype-design.md`

**This is plan 1 of 3.** Plan 2 is the wxPython client. Plan 3 is the server and dashboard. This plan delivers milestone M1 and part of M5 (the seed lessons).

## Global Constraints

- Python 3.13 on Windows, macOS, and Linux. No platform-specific code in the engine.
- The engine package imports only the standard library and PyYAML. No network, no window toolkit, no database, no clock reads except the timestamp on an incoming event.
- Every user-facing string is spoken text: plain words, no abbreviations that a screen reader would spell out oddly, and no jokes.
- Every task's text uses only characters and keys taught by an earlier lesson or by the same lesson's `teaches` list.
- Games are deterministic: the random generator is seeded by the caller and the seed is recorded.
- Commits are small and follow `feat:` or `test:` prefixes.

## Review Focus

1. A printable key arrives with `text=None` because the platform could not map it. The engine must count it as a miss with a spoken "unknown key", never crash.
2. A wrong key is held down and auto-repeats. It must count as one error per physical press and must not repeat the same spoken correction on every repeat event.
3. An end key is pressed before the task text is finished, or the wrong key is pressed at the final character. The task must not advance or be recorded as complete.
4. A lesson file is missing a field, has `repeat: 3`, or has two lessons with the same ID. Loading must raise an error naming the field or the duplicate, never a bare traceback.
5. A task contains a character that has not been taught, or uses Enter as its end key while teaching Enter. The curriculum test must fail with the lesson ID and the offending task.

---

## File Structure

```
engine/
  pyproject.toml
  src/steadytype_engine/
    __init__.py          # version only
    keys.py              # Key, Modifier, Side, KeyEvent
    commands.py          # Speak, Tone, Display, SaveAttempt, EndLesson
    preferences.py       # Preferences and its enums
    lesson.py            # Task, Lesson, Course, LessonError, from_dict
    loader.py            # YAML file loading, duplicate checks
    hints.py             # spoken key locations
    scoring.py           # Metrics, Goals, stars
    session.py           # LessonSession state machine
    dictation.py         # DictationSession
    buffer.py            # TextBuffer with cursor and selection
    games/
      __init__.py
      base.py            # Game protocol, GamePrompt
      missing_letter.py
      wrong_letter.py
      select_delete.py
    transcript.py        # TranscriptRecorder for tests and the harness
    cli.py               # command-line harness
  tests/
    goldens/
content/
  course.yaml
  lessons/
    001-function-keys.yaml
    002-home-row-position.yaml
    003-home-row-letters.yaml
    004-home-row-words.yaml
    005-home-row-phrases.yaml
  words.yaml             # word pools for games and tasks
docs/
  content-authoring.md
```

---

### Task 1: Repository scaffold, license, and CI

**Files:**
- Create: `engine/pyproject.toml`
- Create: `engine/src/steadytype_engine/__init__.py`
- Create: `engine/tests/test_package.py`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: installable package `steadytype_engine` with `__version__: str`.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_package.py
import steadytype_engine


def test_package_reports_a_version():
    assert steadytype_engine.__version__ == "0.1.0"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'steadytype_engine'`.

- [ ] **Step 3: Create the package**

`engine/pyproject.toml`:

```toml
[project]
name = "steadytype-engine"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["PyYAML>=6.0,<7"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/steadytype_engine"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`engine/src/steadytype_engine/__init__.py`:

```python
__version__ = "0.1.0"
```

Add `LICENSE` with the full GPL-3.0 text, a `.gitignore` covering `__pycache__/`, `.venv/`, `*.egg-info/`, and a `README.md` naming the project, its license, and the three plans.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pip install -e ".[dev]" && python -m pytest -v`
Expected: PASS.

- [ ] **Step 5: Add CI and commit**

`.github/workflows/ci.yml` runs on push and pull request, on `ubuntu-latest`, `windows-latest`, and `macos-latest`, with Python 3.13: `pip install -e "./engine[dev]"`, `ruff check engine`, `pytest engine`.

```bash
git add engine .github LICENSE README.md .gitignore
git commit -m "feat: scaffold the engine package"
```

---

### Task 2: The key model

**Files:**
- Create: `engine/src/steadytype_engine/keys.py`
- Test: `engine/tests/test_keys.py`

**Interfaces:**
- Produces: `Key` enum with lowercase token values, `Modifier` enum, `Side` enum, and `KeyEvent` frozen dataclass with fields `kind: str`, `key: Key`, `text: str | None`, `modifiers: frozenset[Modifier]`, `side: Side`, `is_repeat: bool`, `scan_code: int`, `timestamp: float`.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_keys.py
import pytest

from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def test_letter_event_carries_the_produced_character():
    event = KeyEvent(
        kind="down", key=Key.A, text="a", modifiers=frozenset(),
        side=Side.NONE, is_repeat=False, scan_code=30, timestamp=0.0,
    )
    assert event.text == "a"


@pytest.mark.parametrize(
    ("name", "token"),
    [("COMMA", "comma"), ("SPACE", "space"), ("NUMPAD_ENTER", "numpad_enter"),
     ("LEFT_SHIFT", "left_shift"), ("PAGE_UP", "page_up"), ("F12", "f12")],
)
def test_key_tokens_are_stable(name, token):
    assert Key[token.upper()].value == token


def test_every_course_key_exists():
    names = [
        *(chr(c) for c in range(ord("a"), ord("z") + 1)),
        *(str(d) for d in range(10)),
        "space", "enter", "numpad_enter", "tab", "escape", "backspace", "delete",
        "insert", "home", "end", "page_up", "page_down", "up", "down", "left",
        "right", *(f"f{n}" for n in range(1, 13)), "left_shift", "right_shift",
        "left_control", "right_control", "left_alt", "right_alt", "left_meta",
        "right_meta", "caps_lock", "num_lock", "comma", "period", "slash",
        "semicolon", "apostrophe", "left_bracket", "right_bracket", "backslash",
        "grave", "minus", "equals", *(f"numpad_{d}" for d in range(10)),
        "numpad_add", "numpad_subtract", "numpad_multiply", "numpad_divide",
        "numpad_decimal", "unknown",
    ]
    for name in names:
        assert Key(name) is not None
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_keys.py -v`
Expected: FAIL with `ModuleNotFoundError: steadytype_engine.keys`.

- [ ] **Step 3: Implement `keys.py`**

Define `Side(Enum)` with `LEFT`, `RIGHT`, `NONE`; `Modifier(Enum)` with `SHIFT`, `CONTROL`, `ALT`, `META`, `CAPS_LOCK`, `NUM_LOCK`; `Key(str, Enum)` whose member name is the upper-case token and whose value is the lower-case token. Generate the members from the list in the test so names and values cannot drift. `KeyEvent` is a frozen dataclass with the fields above and a `with_repeat()` helper that returns a copy with `is_repeat=True`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_keys.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/keys.py engine/tests/test_keys.py
git commit -m "feat: add the normalized key model"
```

---

### Task 3: Commands and preferences

**Files:**
- Create: `engine/src/steadytype_engine/commands.py`
- Create: `engine/src/steadytype_engine/preferences.py`
- Test: `engine/tests/test_commands.py`
- Test: `engine/tests/test_preferences.py`

**Interfaces:**
- Produces: `Speak(text: str, interrupt: bool = False)`, `Tone(name: str)`, `Display(state: str)`, `SaveAttempt(record: object)`, `EndLesson` as frozen dataclasses; `Command` as their union. `Feedback` enum `TONE | WORD | BOTH`, `Verbosity` enum `BRIEF | STANDARD | DETAILED`, `TypingExperience` enum `LITTLE | SOME | A_LOT`, `Echo` enum `OFF | WORDS | EVERY_KEY`, `Pitch` enum `HIGH | LOW`, and `Preferences` dataclass.
- Produces: `ToneName` constants `CORRECT`, `WRONG`, `RACE_START`, `RACE_WARNING`, `RACE_END`, `LESSON_DONE`.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_commands.py
from steadytype_engine.commands import Speak, Tone, ToneName


def test_speak_is_value_equal():
    assert Speak("right") == Speak("right", interrupt=False)


def test_tone_names_are_stable():
    assert ToneName.CORRECT == "correct"
    assert Tone(ToneName.WRONG).name == "wrong"
```

```python
# engine/tests/test_preferences.py
from steadytype_engine.preferences import Echo, Feedback, Pitch, Preferences, TypingExperience, Verbosity


def test_defaults_match_the_spec():
    prefs = Preferences()
    assert prefs.double_press_ms == 500
    assert prefs.feedback is Feedback.BOTH
    assert prefs.verbosity is Verbosity.STANDARD
    assert prefs.typing_experience is TypingExperience.SOME
    assert prefs.echo is Echo.WORDS
    assert prefs.echo_pitch is Pitch.HIGH
    assert prefs.one_handed is False
    assert prefs.laptop_keyboard is False
    assert prefs.tones is True


def test_double_press_window_is_bounded():
    with pytest.raises(ValueError, match="double_press_ms"):
        Preferences(double_press_ms=200)
    with pytest.raises(ValueError, match="double_press_ms"):
        Preferences(double_press_ms=1000)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_commands.py tests/test_preferences.py -v`
Expected: FAIL with module-not-found errors.

- [ ] **Step 3: Implement both modules**

`commands.py` holds the five frozen dataclasses and `Command = Speak | Tone | Display | SaveAttempt | EndLesson`. `ToneName` is a class of string constants. `preferences.py` holds the enums and a frozen dataclass whose `__post_init__` rejects a `double_press_ms` outside 300 to 900 with a `ValueError` whose message contains the field name.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_commands.py tests/test_preferences.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/commands.py engine/src/steadytype_engine/preferences.py engine/tests/test_commands.py engine/tests/test_preferences.py
git commit -m "feat: add commands and student preferences"
```

---

### Task 4: Lesson model and YAML loader

**Files:**
- Create: `engine/src/steadytype_engine/lesson.py`
- Create: `engine/src/steadytype_engine/loader.py`
- Test: `engine/tests/test_lesson.py`

**Interfaces:**
- Produces: `TaskKind` enum `TEXT | KEY | COMBO | GAME`; `EndKey` enum `SPACE | ENTER | NONE`; `Task(text: str, help: str | None = None, kind: TaskKind = TEXT)`; `Lesson(id, unit, ordinal, title, teaches, kind, end_key, repeat, intro, tasks)`; `Course(schema: int, version: str, lessons: tuple[Lesson, ...])`; `LessonError(Exception)`.
- Produces: `Lesson.from_dict(data: Mapping[str, object]) -> Lesson`; `Course.from_dict(data: Mapping[str, object]) -> Course`; `load_lesson(path: Path) -> Lesson`; `load_course(path: Path) -> Course`.
- Rule: `repeat` must be 2 or 4; `kind` must be `keyboarding`, `game`, `dictation`, or `race`; task `kind` must be one of the four `TaskKind` values; lesson IDs must be unique within a course.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_lesson.py
from pathlib import Path

import pytest

from steadytype_engine.lesson import Course, EndKey, Lesson, LessonError, TaskKind

VALID = {
    "schema": 1,
    "id": 14,
    "unit": 2,
    "ordinal": 14,
    "title": "New letters: U I O P",
    "teaches": ["u", "i", "o", "p"],
    "kind": "keyboarding",
    "end_key": "space",
    "repeat": 4,
    "intro": "These four letters are typed with the right hand.",
    "tasks": [{"text": "u", "help": "U is above J."}, {"text": "juju"}],
}


def test_minimal_lesson_loads():
    lesson = Lesson.from_dict(VALID)
    assert lesson.id == 14
    assert lesson.end_key is EndKey.SPACE
    assert lesson.tasks[1].kind is TaskKind.TEXT
    assert lesson.tasks[1].help is None


@pytest.mark.parametrize(
    ("change", "message"),
    [({"repeat": 3}, "repeat"), ({"kind": "quiz"}, "kind"),
     ({"title": ""}, "title"), ({"tasks": []}, "tasks")],
)
def test_bad_lesson_names_the_field(change, message):
    data = {**VALID, **change}
    with pytest.raises(LessonError, match=message):
        Lesson.from_dict(data)


def test_duplicate_ids_are_rejected():
    with pytest.raises(LessonError, match="duplicate"):
        Course.from_dict({"schema": 1, "version": "1", "lessons": [VALID, VALID]})


def test_course_orders_lessons_by_ordinal():
    second = {**VALID, "id": 2, "ordinal": 2, "title": "Two"}
    first = {**VALID, "id": 1, "ordinal": 1, "title": "One"}
    course = Course.from_dict({"schema": 1, "version": "1", "lessons": [second, first]})
    assert [lesson.id for lesson in course.lessons] == [1, 2]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_lesson.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `lesson.py` and `loader.py`**

`from_dict` validates each field and raises `LessonError(f"{field}: {reason}")`. An empty string for `title` or `intro` is invalid; `teaches` may be empty only for game lessons. `loader.py` reads UTF-8, parses with `yaml.safe_load`, rejects a non-mapping root, and wraps `yaml.YAMLError` in `LessonError` with the file name and line.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_lesson.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/lesson.py engine/src/steadytype_engine/loader.py engine/tests/test_lesson.py
git commit -m "feat: add the lesson model and YAML loader"
```

---

### Task 5: Scoring

**Files:**
- Create: `engine/src/steadytype_engine/scoring.py`
- Test: `engine/tests/test_scoring.py`

**Interfaces:**
- Produces: `Metrics(characters: int, keypresses: int, errors: int, first_try_correct: int, active_seconds: float)` with `wpm`, `accuracy`, `real_accuracy` properties; `Goals(wpm_target: float = 20.0, accuracy_target: float = 95.0)`; `stars(metrics: Metrics, goals: Goals) -> int`.
- Produces: `accuracy_star(accuracy: float) -> int` and `speed_star(wpm: float, target: float) -> int`.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_scoring.py
import pytest

from steadytype_engine.scoring import Goals, Metrics, accuracy_star, speed_star, stars


def test_wpm_uses_five_characters_per_word():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.wpm == pytest.approx(51.5, abs=0.05)


def test_accuracy_counts_corrected_mistakes():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.accuracy == pytest.approx(95.81, abs=0.01)


def test_real_accuracy_counts_first_try_characters():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.real_accuracy == pytest.approx(91.26, abs=0.01)


@pytest.mark.parametrize(
    ("accuracy", "expected"), [(98, 5), (97.9, 4), (95, 4), (90, 3), (80, 2), (79.9, 1)],
)
def test_accuracy_star_boundaries(accuracy, expected):
    assert accuracy_star(accuracy) == expected


@pytest.mark.parametrize(
    ("wpm", "expected"), [(20, 5), (18, 4), (15, 3), (10, 2), (9.9, 1)],
)
def test_speed_star_boundaries(wpm, expected):
    assert speed_star(wpm, 20) == expected


def test_stars_take_the_lower_of_accuracy_and_speed():
    fast_and_sloppy = Metrics(characters=500, keypresses=600, errors=100,
                              first_try_correct=400, active_seconds=60)
    assert stars(fast_and_sloppy, Goals()) == 2
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_scoring.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `scoring.py`**

Use the thresholds from the spec. Guard against a zero denominator by returning `0.0` for the rate properties, which `stars` treats as one star.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_scoring.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/scoring.py engine/tests/test_scoring.py
git commit -m "feat: add attempt scoring and stars"
```

---

### Task 6: The keyboarding session

**Files:**
- Create: `engine/src/steadytype_engine/hints.py`
- Create: `engine/src/steadytype_engine/session.py`
- Test: `engine/tests/test_session.py`

**Interfaces:**
- Consumes: `Key`, `KeyEvent`, `Side`, `Modifier` from Task 2; `Speak`, `Tone`, `ToneName`, `Display` from Task 3; `Lesson`, `TaskKind`, `EndKey` from Task 4; `Metrics` from Task 5.
- Produces: `SessionState` enum `INTRO | TASK_INTRO | TYPING | TASK_DONE | LESSON_DONE`; `LessonSession(lesson, prefs, goals: Goals | None = None, now: Callable[[], float] = time.monotonic)` with `start()`, `handle(event)`, `tick(now)`, `repeat_instructions()`, `finish()`, and the read-only properties `state`, `position`, `task_index`, `current_repeat`, and `metrics`.
- Produces: `KEY_HINTS: dict[str, str]` with lower-case hints, for example `"d": "on the home row, left hand, middle finger"`.
- Rule: a wrong key does not advance. An auto-repeated wrong key counts once and does not repeat the spoken correction. The end key only completes a task when the task text is finished.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_session.py
from steadytype_engine.commands import Speak, Tone, ToneName
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.lesson import Lesson
from steadytype_engine.preferences import Feedback, Preferences
from steadytype_engine.scoring import Goals
from steadytype_engine.session import LessonSession, SessionState

LESSON = Lesson.from_dict({
    "schema": 1, "id": 1, "unit": 1, "ordinal": 1, "title": "Home row",
    "teaches": ["a"], "kind": "keyboarding", "end_key": "space",
    "repeat": 2, "intro": "Type the letter a.",
    "tasks": [{"text": "a"}, {"text": "aa"}],
})


def press(char: str, *, repeat: bool = False) -> KeyEvent:
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=repeat, scan_code=0, timestamp=0.0)


def make_session(**prefs) -> LessonSession:
    return LessonSession(LESSON, Preferences(**prefs), Goals(), now=lambda: 0.0)


def test_start_speaks_the_intro_then_the_first_task():
    commands = make_session().start()
    assert isinstance(commands[0], Speak)
    assert "a" in commands[1].text


def test_correct_key_advances_with_a_tone():
    session = make_session(feedback=Feedback.TONE)
    session.start()
    commands = session.handle(press("a"))
    assert any(isinstance(c, Tone) and c.name == ToneName.CORRECT for c in commands)
    assert session.position == 1


def test_wrong_key_does_not_advance_and_says_the_right_key():
    session = make_session(feedback=Feedback.WORD)
    session.start()
    commands = session.handle(press("s"))
    assert session.position == 0
    assert any(isinstance(c, Speak) and "a" in c.text for c in commands)


def test_second_wrong_key_gives_the_location():
    session = make_session()
    session.start()
    session.handle(press("s"))
    commands = session.handle(press("s"))
    assert any(isinstance(c, Speak) and "home row" in c.text for c in commands)


def test_held_wrong_key_counts_once_and_speaks_once():
    session = make_session()
    session.start()
    session.handle(press("s"))
    repeated = session.handle(press("s", repeat=True))
    assert repeated == []
    assert session.metrics.errors == 1


def test_end_key_before_the_text_is_finished_does_not_complete_the_task():
    session = make_session()
    session.start()
    session.handle(KeyEvent(kind="down", key=Key.SPACE, text=" ", modifiers=frozenset(),
                            side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0))
    assert session.state is SessionState.TYPING
    assert session.position == 0


def test_a_wrong_key_at_the_final_character_does_not_complete_the_task():
    session = make_session()
    session.start()
    session.handle(press("a"))
    session.handle(press("s"))
    assert session.position == 1
    assert session.current_repeat == 1
    assert session.state is SessionState.TYPING


def test_two_correct_repetitions_advance_to_the_next_task():
    session = make_session()
    session.start()
    for _ in range(2):
        session.handle(press("a"))
        session.handle(press(" "))
    assert session.task_index == 1
    assert session.position == 0
    assert session.current_repeat == 1


def test_a_key_without_text_counts_as_a_miss_and_says_unknown():
    session = make_session()
    session.start()
    commands = session.handle(KeyEvent(
        kind="down", key=Key.UNKNOWN, text=None, modifiers=frozenset(),
        side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0))
    assert session.metrics.errors == 1
    assert any(isinstance(c, Speak) and "unknown" in c.text for c in commands)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_session.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `hints.py` and `session.py`**

`hints.py` maps every letter, digit, and punctuation character to a spoken location, plus named keys: space, enter, tab, escape, backspace, delete, the arrows, and the function keys.

`session.py` holds the state machine. `start()` returns `[Speak(intro), Speak(task_intro)]` and sets `TASK_INTRO`. The first printable key moves to `TYPING`. Character comparison uses `event.text`; key tasks use `event.key`. Track `position`, `current_repeat`, `errors_this_key`, and held-key state. `tick` is a no-op in this task.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_session.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/hints.py engine/src/steadytype_engine/session.py engine/tests/test_session.py
git commit -m "feat: add the keyboarding session state machine"
```

---

### Task 7: Results, tips, and the attempt record

**Files:**
- Modify: `engine/src/steadytype_engine/session.py`
- Modify: `engine/src/steadytype_engine/scoring.py`
- Test: `engine/tests/test_results.py`

**Interfaces:**
- Produces: `AttemptRecord` dataclass with the fields in the spec's attempt example, plus `key_stats: tuple[KeyStat, ...]` where `KeyStat(key: str, presses: int, errors: int)`.
- Produces: `LessonSession.finish() -> AttemptRecord` and `result_commands(record, prefs) -> list[Command]`.
- Produces: `tip_for(key_stats: Sequence[KeyStat]) -> str`. It uses the lower-case hint from `KEY_HINTS` and capitalizes its first letter, so the tip reads as a new sentence.
- Rule: active seconds exclude any gap longer than 5 seconds.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_results.py
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_results.py -v`
Expected: FAIL with import errors for `tip_for`, `KeyStat`, `result_commands`.

- [ ] **Step 3: Implement**

Add `KeyStat` and `AttemptRecord` to `scoring.py`. `tip_for` returns the hint for the highest-error key when its errors are at least 2 and at least twice the next key's errors; otherwise the neutral line. `finish()` freezes the metrics, computes stars, and returns the record. `result_commands` speaks, in order: accuracy, real accuracy, speed, time, stars, tip; then "Press Enter for the next lesson, or F3 twice to choose another."

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_results.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/scoring.py engine/src/steadytype_engine/session.py engine/tests/test_results.py
git commit -m "feat: report results, stars, and a tip"
```

---

### Task 8: Dictation

**Files:**
- Create: `engine/src/steadytype_engine/dictation.py`
- Test: `engine/tests/test_dictation.py`

**Interfaces:**
- Consumes: `KeyEvent`, `Speak`, `Tone`, `Preferences.echo`, `Preferences.echo_pitch`.
- Produces: `Passage(title: str, text: str)`; `chunk_text(text: str, size: int = 3) -> tuple[str, ...]`; `DictationSession(passage, prefs)` with `start()`, `handle(event)`, `finish() -> DictationResult`; `DictationResult(accuracy: float, wpm: float, misspelled: tuple[str, ...])`.
- Rule: dictation never corrects during typing. A chunk advances when the typed character count reaches the chunk's length, or when Enter is pressed. Escape ends the task.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_dictation.py
from steadytype_engine.dictation import DictationSession, Passage, chunk_text
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.preferences import Echo, Preferences


def _key(char: str) -> KeyEvent:
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_chunks_are_three_words_then_the_remainder():
    assert chunk_text("one two three four five") == ("one two three", "four five")


def test_first_chunk_is_spoken_on_start():
    session = DictationSession(Passage("t", "one two three four"), Preferences())
    commands = session.start()
    assert "one two three" in commands[0].text


def test_typing_the_whole_chunk_speaks_the_next_one_without_correcting():
    session = DictationSession(Passage("t", "one two three four"), Preferences())
    session.start()
    spoken = []
    for char in "one two three":
        spoken.extend(c for c in session.handle(_key(char)) if hasattr(c, "text"))
    assert any("four" in c.text for c in spoken)


def test_escape_ends_and_reports_misspelled_words():
    session = DictationSession(Passage("t", "cat sat"), Preferences(echo=Echo.OFF))
    session.start()
    for char in "cot sat":
        session.handle(_key(char))
    result = session.finish()
    assert result.misspelled == ("cat",)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_dictation.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `dictation.py`**

Split the passage on whitespace, group three words per chunk. Track the typed text and the current chunk. Echo a word when a space is typed and `echo` is `WORDS`; echo every character when it is `EVERY_KEY`; stay silent when `OFF`. `finish()` compares typed words with expected words using a simple case-sensitive comparison and returns the mismatches.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_dictation.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/dictation.py engine/tests/test_dictation.py
git commit -m "feat: add dictation"
```

---

### Task 9: The text buffer for games and editing drills

**Files:**
- Create: `engine/src/steadytype_engine/buffer.py`
- Test: `engine/tests/test_buffer.py`

**Interfaces:**
- Produces: `BufferResult(changed: bool, speech: str)`; `TextBuffer(text: str)` with `handle(event: KeyEvent) -> BufferResult`, `text` property, `cursor`, `selection() -> tuple[int, int] | None`.
- Rule: arrows move by character; Control with arrows moves by word; Shift with arrows extends a selection; Home and End move to the ends; Delete removes the character to the right; Backspace removes the character to the left; a printable key replaces the selection or inserts at the cursor.

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_buffer.py
from steadytype_engine.buffer import TextBuffer
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def _key(key, text=None, mods=frozenset()):
    return KeyEvent(kind="down", key=key, text=text, modifiers=mods,
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_right_arrow_speaks_the_character_to_the_right():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.RIGHT))
    assert (buf.cursor, result.speech) == (1, "a")


def test_control_right_moves_by_word():
    buf = TextBuffer("one two")
    buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.CONTROL})))
    assert buf.cursor == 4


def test_shift_right_selects_and_speaks_the_selection():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    assert buf.selection() == (0, 1)
    assert result.speech == "c"


def test_delete_removes_to_the_right_and_speaks_the_word():
    buf = TextBuffer("cat")
    result = buf.handle(_key(Key.DELETE))
    assert buf.text == "at"
    assert result.speech == "at"


def test_backspace_removes_to_the_left():
    buf = TextBuffer("cat")
    buf.handle(_key(Key.RIGHT))
    buf.handle(_key(Key.BACKSPACE))
    assert buf.text == "at"


def test_printable_key_replaces_the_selection():
    buf = TextBuffer("cat")
    buf.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    buf.handle(_key(Key.D, text="d"))
    assert buf.text == "dat"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd engine && python -m pytest tests/test_buffer.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `buffer.py`**

Keep `chars` as a list, `cursor` as an index, and `anchor` as `None` or an index. Speech after a move is the character under the cursor or "end of line". Speech after an edit is the current word containing the cursor. Selection returns a sorted pair.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd engine && python -m pytest tests/test_buffer.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/buffer.py engine/tests/test_buffer.py
git commit -m "feat: add the editable text buffer"
```

---

### Task 10: The missing-letter game

**Files:**
- Create: `engine/src/steadytype_engine/games/base.py`
- Create: `engine/src/steadytype_engine/games/missing_letter.py`
- Create: `engine/src/steadytype_engine/games/__init__.py`
- Test: `engine/tests/test_game_missing_letter.py`

**Interfaces:**
- Consumes: `TextBuffer`, `KeyEvent`, `Speak`, `Tone`.
- Produces: `GamePrompt(intro: str, buffer: TextBuffer, target: str, help: str)`; `Game` protocol with `make(rng: random.Random, words: Sequence[str]) -> GamePrompt` and `is_complete(buffer: TextBuffer) -> bool`; `MissingLetterGame`.
- Rule: the game is deterministic for a given seed.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_game_missing_letter.py
import random

from steadytype_engine.games.missing_letter import MissingLetterGame
from steadytype_engine.keys import Key, KeyEvent, Side


def _key(char: str) -> KeyEvent:
    return KeyEvent(kind="down", key=Key(char), text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_removes_exactly_one_letter_and_keeps_the_target():
    game = MissingLetterGame()
    prompt = game.make(random.Random(1), ["add", "dad", "sad"])
    assert len(prompt.buffer.text) == len(prompt.target) - 1
    assert prompt.target in {"add", "dad", "sad"}
    assert not game.is_complete(prompt.buffer)


def test_typing_the_missing_letter_completes_the_game():
    game = MissingLetterGame()
    prompt = game.make(random.Random(1), ["add"])
    index = next(i for i in range(len(prompt.target))
                 if i >= len(prompt.buffer.text)
                 or prompt.buffer.text[i] != prompt.target[i])
    prompt.buffer.cursor = index
    prompt.buffer.handle(_key(prompt.target[index]))
    assert game.is_complete(prompt.buffer)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_game_missing_letter.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `base.py` and `missing_letter.py`**

`base.py` holds `GamePrompt` and the `Game` protocol. `missing_letter.py` picks a word, picks a letter index, removes that character, and sets the cursor to the start. `is_complete` compares the buffer text with the target.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_game_missing_letter.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/games engine/tests/test_game_missing_letter.py
git commit -m "feat: add the missing-letter game"
```

---

### Task 11: The wrong-letter repair game

**Files:**
- Create: `engine/src/steadytype_engine/games/wrong_letter.py`
- Test: `engine/tests/test_game_wrong_letter.py`

**Interfaces:**
- Produces: `WrongLetterGame` implementing the same protocol as Task 10. The prompt replaces one letter with a wrong letter and places the cursor at the start.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_game_wrong_letter.py
import random

from steadytype_engine.games.wrong_letter import WrongLetterGame
from steadytype_engine.keys import Key, KeyEvent, Side


def _key(key: Key, text: str | None = None) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=text, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_has_one_wrong_letter_and_a_different_character():
    game = WrongLetterGame()
    prompt = game.make(random.Random(2), ["cat"])
    assert len(prompt.buffer.text) == 3
    assert prompt.buffer.text != prompt.target
    assert sum(a != b for a, b in zip(prompt.buffer.text, prompt.target)) == 1


def test_deleting_and_retyping_the_letter_completes_the_game():
    game = WrongLetterGame()
    prompt = game.make(random.Random(2), ["cat"])
    index = next(i for i in range(len(prompt.target))
                 if prompt.buffer.text[i] != prompt.target[i])
    prompt.buffer.cursor = index
    prompt.buffer.handle(_key(Key.DELETE))
    prompt.buffer.handle(_key(Key(prompt.target[index]), text=prompt.target[index]))
    assert game.is_complete(prompt.buffer)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_game_wrong_letter.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `wrong_letter.py`**

Choose an index and a replacement character from the same word's taught set, never equal to the original. `is_complete` compares with the target.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_game_wrong_letter.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/games/wrong_letter.py engine/tests/test_game_wrong_letter.py
git commit -m "feat: add the wrong-letter repair game"
```

---

### Task 12: The select-and-delete game

**Files:**
- Create: `engine/src/steadytype_engine/games/select_delete.py`
- Test: `engine/tests/test_game_select_delete.py`

**Interfaces:**
- Produces: `SelectDeleteGame`. The prompt inserts one extra word into a sentence and sets the cursor to the start. Completion is a buffer equal to the target sentence.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_game_select_delete.py
import random

from steadytype_engine.games.select_delete import SelectDeleteGame
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def _key(key: Key, mods: frozenset = frozenset()) -> KeyEvent:
    return KeyEvent(kind="down", key=key, text=None, modifiers=mods,
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def test_prompt_has_exactly_one_extra_word():
    game = SelectDeleteGame()
    prompt = game.make(random.Random(3), ["the cat sat on the mat"])
    assert len(prompt.buffer.text.split()) == len(prompt.target.split()) + 1


def test_selecting_the_extra_word_and_deleting_it_completes_the_game():
    game = SelectDeleteGame()
    prompt = game.make(random.Random(3), ["the cat sat on the mat"])
    extra = next(w for w in prompt.buffer.text.split() if w not in prompt.target.split())
    start = prompt.buffer.text.index(extra)
    prompt.buffer.cursor = start
    for _ in range(len(extra)):
        prompt.buffer.handle(_key(Key.RIGHT, mods=frozenset({Modifier.SHIFT})))
    prompt.buffer.handle(_key(Key.DELETE))
    assert game.is_complete(prompt.buffer)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_game_select_delete.py -v`
Expected: FAIL with module-not-found.

- [ ] **Step 3: Implement `select_delete.py`**

Pick a sentence, pick a word from `words.yaml`, insert it at a random position between words. `is_complete` normalizes runs of whitespace before comparing.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_game_select_delete.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/games/select_delete.py engine/tests/test_game_select_delete.py
git commit -m "feat: add the select-and-delete game"
```

---

### Task 13: Transcript harness and golden files

**Files:**
- Create: `engine/src/steadytype_engine/transcript.py`
- Create: `engine/tests/goldens/lesson_001.txt`
- Test: `engine/tests/test_transcript.py`

**Interfaces:**
- Produces: `TranscriptRecorder` with `record(commands: Iterable[Command]) -> None` and `lines() -> list[str]`; `format_command(command) -> str` rendering `SPEAK: text`, `TONE: name`, `DISPLAY: state`, `END`.
- Produces: `run_script(lesson: Lesson, keys: Sequence[KeyEvent], prefs: Preferences | None = None) -> list[str]`.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_transcript.py
from pathlib import Path

from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.lesson import EndKey, TaskKind
from steadytype_engine.loader import load_lesson
from steadytype_engine.transcript import run_script

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = Path(__file__).parent / "goldens" / "lesson_001.txt"


def _keys_for(lesson):
    keys = []
    for task in lesson.tasks:
        for _ in range(lesson.repeat):
            keys.append(KeyEvent(
                kind="down", key=Key(task.text), text=task.text,
                modifiers=frozenset(), side=Side.NONE, is_repeat=False,
                scan_code=0, timestamp=0.0))
            if lesson.end_key is EndKey.SPACE:
                keys.append(KeyEvent(
                    kind="down", key=Key.SPACE, text=" ", modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0))
    return keys


def test_lesson_one_matches_its_golden_transcript():
    lesson = load_lesson(ROOT / "content" / "lessons" / "001-function-keys.yaml")
    lines = run_script(lesson, _keys_for(lesson))
    assert "\n".join(lines) == GOLDEN.read_text(encoding="utf-8").strip()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_transcript.py -v`
Expected: FAIL because `transcript` does not exist.

- [ ] **Step 3: Implement `transcript.py` and generate the golden**

Add a `--update` path: `python -m steadytype_engine.transcript <lesson.yaml> --update`. Run it once, read the output aloud to check wording, then commit the file.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_transcript.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/transcript.py engine/tests/goldens engine/tests/test_transcript.py
git commit -m "test: pin lesson one to a golden transcript"
```

---

### Task 14: The command-line harness

**Files:**
- Create: `engine/src/steadytype_engine/cli.py`
- Test: `engine/tests/test_cli.py`

**Interfaces:**
- Produces: `python -m steadytype_engine.cli <lesson.yaml> [--prefs none|one-handed|laptop]`, which reads one key name per line from standard input, accepts `a`, `space`, `enter`, `f1`, `left_shift+a`, prints each command on its own line, and exits on `escape` three times or end of input.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_cli.py
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cli_runs_a_lesson_from_stdin():
    script = "a\nspace\na\nspace\n"
    result = subprocess.run(
        [sys.executable, "-m", "steadytype_engine.cli",
         str(ROOT / "content" / "lessons" / "003-home-row-letters.yaml")],
        input=script, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "SPEAK:" in result.stdout
    assert "TONE: correct" in result.stdout
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_cli.py -v`
Expected: FAIL with a non-zero return code.

- [ ] **Step 3: Implement `cli.py`**

Parse arguments with `argparse`, load the lesson, build preferences from the flag, run the session, and print commands with `format_command`. Read standard input line by line; map names to `KeyEvent`s; a name containing `+` splits into modifiers and a key. Unknown names print `ERROR: unknown key <name>` and continue.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd engine && python -m pytest tests/test_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/src/steadytype_engine/cli.py engine/tests/test_cli.py
git commit -m "feat: add the command-line lesson harness"
```

---

### Task 15: Seed lessons, the course file, and the curriculum test

**Files:**
- Create: `content/course.yaml`
- Create: `content/lessons/001-function-keys.yaml` through `005-home-row-phrases.yaml`
- Create: `content/words.yaml`
- Create: `docs/content-authoring.md`
- Test: `engine/tests/test_curriculum.py`

**Interfaces:**
- Consumes: `load_course`, `Lesson`, `TaskKind`, `EndKey`.
- Produces: a course of five lessons that the CLI can run end to end.

- [ ] **Step 1: Write the failing test**

```python
# engine/tests/test_curriculum.py
from pathlib import Path

from steadytype_engine.lesson import EndKey, TaskKind
from steadytype_engine.loader import load_course

ROOT = Path(__file__).resolve().parents[2]
COURSE = load_course(ROOT / "content" / "course.yaml")


def test_course_has_five_seed_lessons():
    assert [lesson.id for lesson in COURSE.lessons] == [1, 2, 3, 4, 5]


def test_no_task_uses_an_untaught_character():
    taught: set[str] = {" "}
    for lesson in COURSE.lessons:
        taught.update(lesson.teaches)
        for task in lesson.tasks:
            if task.kind is not TaskKind.TEXT:
                continue
            unknown = set(task.text) - taught
            assert not unknown, f"lesson {lesson.id}: {sorted(unknown)} in {task.text!r}


def test_a_task_teaching_enter_does_not_use_enter_as_its_end_key():
    for lesson in COURSE.lessons:
        for task in lesson.tasks:
            if task.kind is TaskKind.KEY and task.text == "enter":
                assert lesson.end_key is EndKey.NONE, f"lesson {lesson.id}"


def test_every_lesson_declares_what_it_teaches():
    for lesson in COURSE.lessons:
        assert lesson.teaches, f"lesson {lesson.id}"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd engine && python -m pytest tests/test_curriculum.py -v`
Expected: FAIL because `content/course.yaml` does not exist.

- [ ] **Step 3: Write the five lessons and the course file**

- Lesson 1 teaches the function keys F1 to F4 and Escape with `TaskKind.KEY` tasks and `end_key: none`.
- Lesson 2 teaches hand position and the F and J bumps, using `TaskKind.KEY` tasks for the position and `TaskKind.TEXT` tasks for `f` and `j`.
- Lesson 3 teaches A S D F J K L, with single letters, then pairs, then `asdf`, `jkl`.
- Lesson 4 teaches home-row words: `add`, `dad`, `sad`, `fall`, `lads`, `flask`.
- Lesson 5 teaches home-row phrases: `a lad`, `all fall`, `dad adds`.

`content/course.yaml` lists the five files with `schema: 1` and `version: "0.1.0"`. `docs/content-authoring.md` explains the fields, the teach-before-use rule, and how to run the curriculum test.

- [ ] **Step 4: Run the whole suite**

Run: `cd engine && python -m pytest -v`
Expected: all tests PASS, including the curriculum test.

- [ ] **Step 5: Commit**

```bash
git add content docs/content-authoring.md engine/tests/test_curriculum.py
git commit -m "feat: add the five seed lessons and the curriculum test"
```

---

## Self-Review

**Spec coverage for this plan:** C-8 to C-15 (lesson flow and results), C-16 to C-19 partially (the engine side of repeat and next; command handling belongs to the client), C-20 to C-25 (the engine emits speech and tones; the client speaks), §5.1 to §5.3 (content format, three games, dictation), §6.1 to §6.5 (engine boundary, keys, format, scoring, attempt record), §13 engine, curriculum, and capture-independent tests. The client, capture, server, dashboard, deployment, and the remaining 67 lessons belong to plans 2 and 3.

**Gaps found and fixed while writing:** the spec's YAML example has no way to express a key target such as F1, so `TaskKind.KEY` and `TaskKind.COMBO` were added here; the spec's engine rule "standard library only" is amended to "standard library and PyYAML" because lessons are YAML; and the spec's game descriptions implied a cursor, so `TextBuffer` became its own task.

**Type check:** `KeyEvent`, `Preferences`, `Lesson`, `Task`, `Metrics`, `KeyStat`, `AttemptRecord`, and `Command` are used with the same field names in every task.

## Execution Handoff

Plans 2 and 3 are written after this one lands, because the client and server both consume the engine's types.
