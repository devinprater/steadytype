# SteadyType client

The desktop client: speech through Prism, full keyboard capture during a lesson,
local accounts and progress.

## Run from source

```
cd client
../.venv/Scripts/python.exe -m pip install -e ".[dev,speech]"
../.venv/Scripts/python.exe -m steadytype_client
```

On first run, type a username in the form lastname.firstname, like prater.devin, then
press **Create this student**. Students have no password. The next run remembers the
username and puts focus on **Sign in**, so Enter is enough.

Staff press **Staff sign in** and use their staff username and password. Staff can take
lessons too, for testing or practice.

`--no-speech` runs silently, which is useful for testing the windows.
`--data-dir PATH` keeps the database somewhere else.

## Keys

- F1 twice: repeat the instructions.
- F2 twice: next lesson. F2 three times: repeat this lesson.
- F3 twice: pick a lesson and a task.
- F12 twice: my progress.
- Escape three times: leave the lesson.
- Control Alt Shift X: leave any lesson, including the function-key lesson.
- Every command is also in the menus.

The first lesson teaches the function keys, so its commands are switched off while it
runs; use the menus there.

## What is not here yet

HTTP sign-in and sync wait for the server. Dictation, races, and the timed test are
in the engine but not yet given their own windows. macOS and Linux capture layers
come after the server.

## Build

```
pyinstaller steadytype.spec
```

The spec bundles `assets/sounds` and `content` beside the executable.
