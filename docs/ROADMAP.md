# Roadmap

## Braille

Students who read braille should get the same lesson text, prompts and results on
their display as they hear in speech.

- **Output first.** Every spoken line should also go to braille: lesson intro,
  task text, key help, errors, lesson result, timed test passage and verdict.
  Add a braille call alongside speak in the presenter and the runners, not a
  separate copy of the text.
- **Windows:** Prism already reaches NVDA, JAWS, PC Talker, Window-Eyes, System
  Access and ZDSR. This is the only platform where Prism braille works today, so
  it is the first target and the one that can be tested here.
- **macOS:** find out what Prism's Apple backend exposes for braille. If it has
  nothing, the fallback is the braille display's own driver, which means the
  student's display speaks for itself and SteadyType only needs to keep the text
  flowing. Needs a real Mac and a display to test.
- **Linux:** Orca's braille support through BrlAPI. Needs a live desktop.
- **Keep output and input separate.** Nothing in the output work should assume
  where input comes from.
- **Keep lines short.** A 40-cell display cannot show a full sentence; wrap at
  the display width and never split a word across lines.

## Braille input

Students should be able to answer with a Perkins-style keyboard on their display,
not only with a computer keyboard. This is a different capture path on every
platform, and none of them look like ordinary key events.

### How each screen reader delivers it

- **Windows, NVDA:** braille input goes through the display driver into the
  focused control as text. Dots 7 and 8 are commands: dot 7 erases the last cell,
  dot 8 translates the pending cells and presses Enter, and dot 7 plus dot 8
  translates without adding a space. Contracted or uncontracted is a user
  setting. The low-level keyboard hook never sees these keys.
- **macOS, VoiceOver:** a display with a Perkins keyboard types into the focused
  control, with translation set in VoiceOver Utility (contracted or
  uncontracted). Again the app receives text, not key presses, and the Quartz
  event tap never sees them.
- **Linux, Orca:** BrlAPI delivers key events to Orca, which has its own bindings
  for braille commands. Unlike the other two, a program can read raw BrlAPI keys
  and cells itself, so per-cell timing is available if we use BrlAPI directly
  instead of going through Orca.

### What that means for timing

Some paths buffer a word and emit it as plain text when Space or dot 8 is
pressed. A lesson that scores per keystroke will see one event for a whole word,
so words per minute measured from key intervals is wrong in both directions: it
can look extremely fast when a buffered word lands, or stall while the student is
still entering cells.

- Measure braille attempts by elapsed time against characters actually entered,
  never by inter-key interval.
- Mark those attempts as braille in the record, and report braille speed
  separately from keyboard speed so a class average is not skewed.
- Do not count a dot 7 correction as an error until the cell is committed.
- Never infer accuracy from keystrokes that were never delivered.

### Capture design

- Add a real text entry path the screen reader can type into: a `TextCtrl` that
  holds the focused text, with the lesson surface mirroring it read-only. This is
  the only route that works on Windows and macOS.
- On Linux, optionally read BrlAPI directly for true per-cell timing, and fall
  back to the text path when BrlAPI is not available.
- Translation: use liblouis for uncontracted and contracted tables, per language,
  and let the student choose the table in preferences.
- Lessons need a braille mode: task text goes to the display, input comes from
  the display, and the keyboard remains available at the same time.
- Test on the NLS eReader, the Focus 14, and the Braille Edge 40, since the three
  report keys differently.

## Still open

- Purge students and attempts inactive five years or more, with a preview, typed
  confirmation and audit entry.
- Staff password reset, and audit entries for more than class, student and goal
  changes.
- Real deployment: DNS, a real certificate, and a backup that actually reaches
  the NAS.
- Wayland capture fallback, and a live test of the Mac and Linux hooks.
- Timed test options: duration, passage choice, and key-level errors.
- Accessibility pass on the dashboard with a screen reader and a braille display
  at 200 percent zoom.
- Race options: configurable pacer speed and passage.
