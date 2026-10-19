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
- **Input later.** Braille keyboard entry is a separate feature: eight-key
  chording, translation through liblouis, and a per-lesson switch. Do not mix it
  into output work.
- **Keep lines short.** A 40-cell display cannot show a full sentence; wrap at
  the display width and never split a word across lines.

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
