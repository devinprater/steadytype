# Writing lessons

Lessons are YAML files under `content/lessons/`, listed in `content/course.yaml`.

## Fields

- `id` — permanent. Never reuse or renumber an ID.
- `unit`, `ordinal` — where it sits in the course. Ordinals may change.
- `title`, `intro` — spoken to the student before the first task.
- `teaches` — every character or key this lesson introduces or practices.
- `kind` — `keyboarding`, `game`, `dictation`, or `race`.
- `end_key` — `space`, `enter`, or `none`. Use `none` when the task itself ends with Enter.
- `repeat` — 2 or 4.
- `tasks` — each has `text`, an optional `help`, and an optional `kind`:
  `text` for characters, `key` for one key such as `f1`, `combo` for a key combination.

## The one rule

A task may use only characters and keys declared in its own `teaches` list or in an
earlier lesson. `engine/tests/test_curriculum.py` fails with the lesson ID and the
offending text when this is broken.

## Checking

```
.venv/Scripts/python.exe -m pytest engine/tests/test_curriculum.py -q
.venv/Scripts/python.exe -m steadytype_engine.cli content/lessons/003-home-row-letters.yaml
```

The second command runs a lesson in the terminal. Type one key name per line:
`a`, `space`, `enter`, `f1`.
