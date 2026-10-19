# SteadyType — design specification

- **Status:** draft for review
- **Date:** 2026-10-19
- **Name:** SteadyType
- **License:** GPL-3.0-or-later
- **Repository:** public on GitHub under `devinprater/steadytype`

---

## 1. Problem

TypingClub is built as a visual game with narration added afterwards. The lesson
surface, the star animations, and the dashboard all assume sight, and the "full
narration" mode talks over the screen reader rather than replacing it.

TypeAbility is the opposite: speech-first, keyboard-first, and built around a
screen reader from the start. But it exists only on Windows, only through JAWS or
Fusion, has no staff dashboard, and its records are files on one computer.

SteadyType takes TypeAbility's teaching method and TypingClub's staff tools, and
builds them as one modern cross-platform system.

## 2. Who it is for

| Role | Description |
|---|---|
| Student | Blind, low-vision, or sighted adult learning to touch type. May be one-handed. May use a laptop keyboard without a numpad. |
| Teacher | Runs classes, adds students, sets goals, reads progress. May be blind and use a screen reader herself. |
| Admin | Manages teachers, the school settings, and the audit log. |

A student may use a screen reader, magnification, or neither. The program is
speech-first, but every screen is also a normal accessible window.

## 3. Scope of the first release

**In scope**

- A desktop client for Windows, then macOS, then Linux.
- A built-in course of 72 lessons, including 9 game lessons built from 3 game types.
- Dictation lessons, races, and per-attempt scoring.
- Speech through Prism, tones for non-speech cues.
- Full keyboard capture during lessons, including modifier sides and system keys.
- Sign-in with username and password, with two levels of remembering.
- A server with a staff dashboard, and offline-tolerant sync.
- WCAG 2.1 AA for both the client and the dashboard.
- Deployment on Ubuntu 24.04 with Docker, Caddy, and optional NAS backups.

**Out of scope for the first release**

- A browser practice page. Planned as the next milestone.
- Teacher-authored lessons. The built-in course only.
- Academic quizzes such as the ones in TypeAbility.
- Braille keyboard input.
- School single sign-on.
- Mobile clients.
- Translation into other languages.

## 4. Client requirements

### 4.1 Sign-in

- **C-1** The client signs in with a username and password over HTTPS.
- **C-2** The sign-in screen offers two remembered states: remember the username
  only, or keep the user signed in.
- **C-3** When a session is remembered, launching the client places focus on the
  Sign in button, so a single Enter signs in.
- **C-4** A **Switch student** action appears in the File menu and on the sign-in
  screen. It ends the session and keeps the saved username.
- **C-5** Credentials are never stored. The refresh token is stored in the
  operating system credential store: Credential Manager on Windows, Keychain on
  macOS, Secret Service on Linux.
- **C-6** The client works offline after a successful sign-in for 30 days. The
  countdown resets on every successful sync.
- **C-7** Failed sign-in is reported in words, never by a sound alone, and never
  reveals whether the username exists.

### 4.2 The lesson experience

- **C-8** Every lesson announces its title, what it teaches, its task count, the
  ending key, and the repeat count before the first task.
- **C-9** A task is spoken before typing begins. The student can replay it at any
  time with F1 twice.
- **C-10** Feedback follows every key press:
  - correct: a tone, the word "right", or both, per preference;
  - wrong, first time: the key pressed and the key required;
  - wrong, second time on the same key: the key's location, hand, and finger;
  - wrong again: the same, slower, plus the target repeated.
- **C-11** Keyboarding lessons do not advance past a wrong key. Dictation never
  corrects during typing.
- **C-12** Each task is typed 2 or 4 times, then the next task is announced.
- **C-13** At the end of a lesson the student hears accuracy, real accuracy, words
  per minute, elapsed active time, stars, and one tip derived from the student's own
  errors.
- **C-14** No jokes are told. The lesson ends with the result and the tip.
- **C-15** After the result the student is told how to continue: Enter for the next
  lesson, F3 twice to choose another.

### 4.3 Commands

- **C-16** The following work at all times outside a text field. Double press means
  two presses within the configured window, default 500 ms.
  - F1 twice: repeat instructions.
  - F2 twice: next lesson; three times: repeat this lesson.
  - F3 twice: lesson picker, a list of lessons with their task counts; choosing a
    lesson shows its tasks in a second list.
  - F4 twice: dictation picker.
  - F5 twice: race on the current task.
  - F12 twice: session report; three times: full history.
  - Escape once: cancel a dialog; three times: save and quit.
  - Control U: preferences. Control Shift U: speak the current preferences.
- **C-17** Every command above also exists as a menu item, so a double press is
  never the only way to reach a function.
- **C-18** The double-press window is adjustable from 300 to 900 ms.
- **C-19** During the lesson that teaches the function keys, function-key commands
  are switched off. Single presses are lesson input, and navigation is available
  from the menu. This avoids a fast pair of inputs being read as a command.

### 4.4 Speech, braille, and sound

- **C-20** Speech goes through Prism, preferring the running screen reader, then a
  speech engine: NVDA or JAWS, then OneCore or SAPI on Windows; VoiceOver on
  macOS; Orca or Speech Dispatcher on Linux.
- **C-21** Lesson prompts queue. Navigation and errors interrupt.
- **C-22** Rate, pitch, volume, and voice are per-student preferences and sync
  across machines where the backend supports them.
- **C-23** Where the backend supports braille, Prism sends the current line to the
  display.
- **C-24** Tones mark correct, incorrect, race start, ten seconds remaining, race
  end, and lesson complete. Tones can be turned off.
- **C-25** If no speech backend is available, the client says so in a dialog with
  instructions and refuses to start a lesson silently.

### 4.5 Preferences

Stored per student and synced:

- typing experience: little, some, a lot (controls how much key-location help is
  given);
- feedback: tone, word, both;
- verbosity: brief, standard, detailed;
- speech rate, pitch, volume, voice;
- double-press window;
- one-handed typing: accept either modifier side;
- laptop keyboard: one Enter and one Control;
- dictation echo: off, words, every key;
- dictation echo pitch: high or low;
- tones on or off;
- keep me signed in.

### 4.6 Visual surface

- **C-26** The lesson area shows the target text in large monospace type, the
  current position marked by a caret shape and not color alone, and errors marked
  by an underline plus a symbol.
- **C-27** All text meets 4.5:1 contrast and all non-text indicators meet 3:1.
- **C-28** The window is fully usable with the screen off. No information exists
  only on screen.
- **C-29** Every window and dialog uses native controls with real labels. There are
  no custom-drawn lists, trees, or buttons. The lesson surface is the only
  custom-drawn control, and it exposes no accessible children, so the screen reader
  does not echo lesson text over Prism.
- **C-30** Caps Lock and Num Lock states are read when a lesson starts and announced
  when they would change what the student types.
- **C-31** WCAG 2.1 AA is applied to every client window and dialog, using the
  criteria that apply to desktop software.

## 5. Course content

The order follows the common published progressions for the rows and the keys, and
TypeAbility for the function-key start and the navigation and editing work.

- Row order: home row first, then the top row, then the bottom row, then capitals,
  punctuation, numbers, symbols, and sentences.
- Home row starts with F and J at the bumps, then D and K, S and L, A and
  semicolon, then G and H.
- Every lesson introduces a key and then uses it in words, phrases, and sentences.
- No task contains a character or key that has not been taught. An automated test
  enforces this.

### 5.1 Units

| Unit | Lessons | Contents |
|---|---:|---|
| 1. Getting started | 4 | Finding the keyboard, the function keys F1–F4 and Escape, the home row position and the F and J bumps, the home row letters |
| 2. Top row, left hand | 7 | Q W E R, words, left-hand words, phrases, one game |
| 3. Top row, right hand | 7 | U I O P, right-hand words, both hands, phrases, one game |
| 4. G and H, capitals, Enter | 8 | G and H, words with each, Shift with the opposite hand, capitalized names, the main Enter key |
| 5. T and Y | 6 | T, TH words, Y, phrases, one game |
| 6. Navigation and editing | 10 | Arrows, Home, End, Page Up and Down, Delete and Backspace, Tab and Caps Lock, dialogs, list boxes and radio buttons and check boxes, selecting text, Control with arrows, cut, copy and paste, two games |
| 7. Numbers and punctuation | 10 | Number row by hand, all digits, comma, period, slash, question mark, exclamation, apostrophe, quotes, Shift with the number row, sentences, arithmetic, two games |
| 8. Bottom row | 10 | Z, X, C, V, B, M, N, words and sentences using every letter, one game |
| 9. Numpad and fluency | 10 | Numpad layout and Num Lock, numpad navigation keys, numpad digits and operators, numbers in context, common-word speed drill, tricky-pair accuracy drill, paragraph typing, timed test, one game |

Each lesson has 6 to 16 tasks. Each task is typed 2 or 4 times.

### 5.2 The three games

1. **Missing letter.** A word or sentence is shown with one letter removed. The
   student finds the gap and types the letter.
2. **Wrong letter repair.** A word contains one wrong letter. The student navigates
   to it, deletes it, and types the right one.
3. **Select and delete.** A sentence contains an extra or wrong word. The student
   selects it with Control Shift Right Arrow and deletes it.

Games never correct during the task; they report at the end, like dictation.

### 5.3 Dictation

Dictation lessons use original passages of 40 to 120 words. The engine splits each
into chunks of 3 or 4 words, speaks a chunk, waits for the student, then continues.
Escape ends the task. The report gives accuracy, speed, and a spelling note for each
word that came out wrong.

## 6. Lesson engine

### 6.1 Boundary

The engine is a separate Python package with no window toolkit, no operating system
calls, and no network. It converts key events into commands. Everything else,
including speech, sound, drawing, saving, and syncing, is done by the client in
response to those commands.

```python
class LessonSession:
    def __init__(self, lesson: Lesson, prefs: Preferences, goals: Goals): ...
    def start(self) -> list[Command]: ...
    def handle(self, event: KeyEvent) -> list[Command]: ...
    def tick(self, now: float) -> list[Command]: ...
    def finish(self) -> AttemptRecord: ...
```

```python
KeyEvent(kind: down|up, key: Key, text: str|None, modifiers: frozenset[Modifier],
         side: Side, is_repeat: bool, scan_code: int, timestamp: float)

Command = Speak(text, interrupt) | Tone(name) | Display(state)
        | SaveAttempt(record) | EndLesson()
```

### 6.2 Keys

`Key` covers every key the course teaches: A–Z, 0–9, punctuation, Space, Enter and
Numpad Enter, Tab, Escape, Backspace, Delete, Insert, Home, End, Page Up, Page Down,
four arrows, F1–F12, left and right Shift, Control, and Alt, left and right Windows
or Command, Caps Lock, Num Lock, and the numpad digits and operators. Anything else
maps to `Unknown` with a platform name, so a lesson can still say what was pressed.

### 6.3 Lesson format

YAML, versioned, valid against a schema, packaged with the client and refreshed
from the server.

```yaml
schema: 1
id: 14
unit: 2
ordinal: 14
title: "New letters: U I O P"
teaches: [u, i, o, p]
kind: keyboarding      # keyboarding | game | dictation | race
end_key: space         # space | enter | none
repeat: 4
intro: "These four letters are typed with the right hand, above the home row."
tasks:
  - text: "u"
    help: "U is above J. Right hand, index finger."
  - text: "juju"
```

Task kinds: single key, word, phrase, sentence, key combination, navigation drill,
editing drill, game.

Lesson IDs are stable. Ordinals may change when a course is reordered; attempts
always reference the lesson ID, never its position.

A game is a rule object with `prompt(task)` and `check(state, key_event)`. The three
games are separate modules with their own tests.

### 6.4 Scoring

- `characters` is the number of characters in the completed target text, including
  spaces.
- `active_seconds` counts time while typing. A gap longer than 5 seconds is idle and
  does not count.
- `wpm = (characters / 5) / (active_seconds / 60)`.
- `accuracy = (keypresses - errors) / keypresses * 100`. A corrected mistake still
  lowers this.
- `real_accuracy = characters correct on their first attempt / characters * 100`.
- Stars, from 1 to 5, are the lower of the accuracy star and the speed star.

| Accuracy star | Requires |
|---|---|
| 5 | 98% or better |
| 4 | 95% |
| 3 | 90% |
| 2 | 80% |
| 1 | below 80% |

| Speed star | Requires |
|---|---|
| 5 | at or above the class goal |
| 4 | 90% of the goal |
| 3 | 75% of the goal |
| 2 | 50% of the goal |
| 1 | below half the goal |

The default goal is 20 words per minute. A class can change it, and can change the
accuracy needed for each star.

### 6.5 Attempt record

Saved locally first, uploaded later:

```json
{
  "id": "uuid generated by the client",
  "lesson_id": 14,
  "kind": "practice",
  "started_at": "2026-10-19T14:02:11Z",
  "ended_at": "2026-10-19T14:04:03Z",
  "active_seconds": 96,
  "characters": 412,
  "keypresses": 430,
  "errors": 18,
  "wpm": 51.5,
  "accuracy": 95.8,
  "real_accuracy": 91.2,
  "stars": 4,
  "key_stats": [{"key": "p", "presses": 31, "errors": 5}],
  "device_id": "uuid",
  "client_version": "0.1.0"
}
```

## 7. Keyboard capture

Capture runs only while a lesson is active. It is off during sign-in, dialogs, and
menus. If capture fails to start, the lesson runs inside the window and says so
before the first task.

```python
class KeyCapture(Protocol):
    def start(self, callback: Callable[[KeyEvent], None]) -> bool: ...
    def stop(self) -> None: ...
    @property
    def active(self) -> bool: ...
```

### 7.1 Windows

A `WH_KEYBOARD_LL` hook on a dedicated thread with its own message loop. No
administrator rights. Virtual-key codes plus scan codes distinguish left and right
Shift, Control, and Alt, and mark extended keys. Returning 1 swallows the key.
Ctrl Alt Delete is never delivered to hooks and Windows L is always passed through;
both are named in the lesson help. The active keyboard layout is checked at startup
and a non-US layout produces a spoken warning.

### 7.2 macOS

A `CGEventTap` at the HID level, returning NULL to swallow. Requires the
Accessibility permission. The client checks `AXIsProcessTrusted` and, when it is
false, shows a setup screen that explains the exact System Settings path. Command
Tab and Command Q can be swallowed. The screen lock shortcut cannot.

### 7.3 Linux

Under X11, `XGrabKeyboard` on the lesson window. Under Wayland a global grab is not
possible, so capture stays inside the window and some compositor shortcuts still
fire. The client detects Wayland at startup and says so in the lesson introduction.

### 7.4 Always-available exits

- Escape three times ends the lesson and releases the keyboard within one second.
- Control Alt Shift X does the same and is never taught.
- A watchdog thread releases the keyboard if the lesson window loses focus or the
  program stops responding.
- Both exits are named when a lesson starts.

### 7.5 Normalization

Auto-repeat is marked, not dropped, because holding a key is a legitimate mistake
to report. Modifier state is tracked from key down and key up events. Layout
mapping happens in the platform layer so the engine only ever sees normalized keys.

## 8. Server

### 8.1 Stack

FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, Jinja2 templates, Uvicorn. Caddy in
front terminates TLS with a certificate from Let's Encrypt and applies security
headers. Everything runs under Docker Compose on Ubuntu 24.04 LTS.

### 8.2 Authentication

- Username and password for students and staff. No second factor.
- Argon2id, 64 MiB memory, 3 iterations, parallelism 4.
- Minimum length 10, no composition rules, checked against a list of common
  passwords. Passphrases are encouraged in the help text.
- Rate limits: 5 failures per username in 15 minutes triggers a lockout that
  doubles each time, to a maximum of 1 hour. 20 failures per address per hour
  blocks that address for 15 minutes.
- Sign-in never reveals whether a username exists.
- Sessions are server-side. The cookie is `__Host-sk_session`, Secure, HttpOnly,
  SameSite=Lax. Without Remember Me it expires when the browser closes. With it, it
  lasts 30 days and is renewed on use.
- Every state-changing form carries a CSRF token.
- Admins and teachers can see the audit log.
- Teachers create student accounts and reset student passwords. Admins reset
  teacher passwords. No email address is needed anywhere in the system.
- A password reset revokes every session and device for that user.
- Everyone can sign out everywhere from the account page.

### 8.3 Roles and permissions

| Action | Student | Teacher | Admin |
|---|---|---|---|
| Read own progress | yes | yes | yes |
| Read a class in their charge | no | yes | yes |
| Create or reset a student password | no | own classes | yes |
| Change class goals | no | own classes | yes |
| Create a teacher | no | no | yes |
| Read the audit log | no | no | yes |

### 8.4 Sync

- The client writes attempts to a local SQLite database first.
- Upload is a batch POST with client-generated attempt IDs. The server inserts or
  ignores; a retry never duplicates.
- The course is fetched with an ETag, so an unchanged course is not downloaded
  again.
- Preferences are last-write-wins with a version counter.
- After 30 days offline the client requires a sign-in before saving new attempts.
  Existing queued attempts are not discarded.

### 8.5 Data model

`users` — id, role, username (unique, case-insensitive), password_hash,
display_name, disabled_at, must_change_password, created_at, last_login_at.

`classes` — id, name, teacher_id, archived_at, created_at.

`enrollments` — class_id, student_id, created_at. Primary key on both.

`courses` — id, slug, title, version, published.

`lessons` — id, course_id, ordinal, slug, title, kind, teaches (text array), body
(JSONB).

`class_courses` — id, class_id, course_id, start_ordinal, end_ordinal, goals
(JSONB: wpm_target, accuracy_target, allow_backspace, star_thresholds).

`attempts` — id (UUID, client-generated), student_id, lesson_id, kind, started_at,
ended_at, active_seconds, characters, keypresses, errors, wpm, accuracy,
real_accuracy, stars, device_id, client_version, synced_at, raw (JSONB).

`key_stats` — attempt_id, key, presses, errors. Primary key on attempt_id and key.

`devices` — id, user_id, name, refresh_token_hash, created_at, last_seen_at,
revoked_at.

`sessions` — id, user_id, token_hash, created_at, last_seen_at, expires_at, ip,
user_agent, revoked_at.

`audit_log` — id, actor_id, action, target_type, target_id, at, ip, detail (JSONB).

`user_preferences` — user_id, version, body (JSONB), updated_at.

### 8.6 API

All under `/api/v1`, JSON, HTTPS only.

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/login` | username, password, remember, device name → access token, refresh token |
| POST | `/auth/refresh` | rotate the refresh token |
| POST | `/auth/logout` | revoke this device |
| GET | `/me` | profile and preferences |
| PUT | `/me/preferences` | save preferences |
| GET | `/me/progress` | current lesson and recent attempts |
| GET | `/course` | course and lessons, with ETag |
| POST | `/attempts` | batch upload, idempotent |

Errors are `{"error": {"code": "...", "message": "..."}}` with a stable code and a
message written for a person, never a stack trace.

## 9. Dashboard

Server-rendered HTML. JavaScript is limited to small progressive enhancements; every
task works with it disabled.

### 9.1 Pages

- **Sign in.**
- **Classes:** every class the user may see, with student count and last activity.
- **Class scoreboard:** one row per student — lessons completed, stars, average
  accuracy, average speed, practice time this week, last active. Sortable by link.
- **Progress grid:** students down the side, lessons across the top. Each cell reads
  as text, for example "4 stars, 92 percent, 18 words per minute". A legend explains
  the pattern without relying on color.
- **Student page:** current lesson, a table of every lesson with best attempt and
  attempt count, the full attempt history, and a per-key error table.
- **Reports:** daily and weekly practice time over a chosen date range, with CSV
  export. Charts carry the same numbers in a table. Dates are stored in UTC and
  shown in the school's timezone.
- **Class settings:** goals for speed, accuracy, Backspace, and star thresholds;
  lesson range; archive.
- **People:** add a student, reset a password, disable an account, move a student,
  add a teacher (admin only). The form suggests a username from the display name
  and a number, and the teacher may change it before saving.
- **Audit log** (admin).
- **Account:** change own password, sign out everywhere.

### 9.2 Accessibility requirements

- **A-1** Semantic landmarks, one `h1` per page, a skip link as the first focusable
  element, and a meaningful page title.
- **A-2** Every input has a visible, programmatically associated label. Errors are
  text, placed next to the field, and linked with `aria-describedby`.
- **A-3** Tables have a caption and `scope` on header cells. The progress grid is a
  table, not an image.
- **A-4** No meaning depends on color alone. Stars, errors, and status carry text.
- **A-5** Focus is always visible and in a logical order. No keyboard traps. No
  drag-only interaction.
- **A-6** Works at 200 percent zoom and at 320 CSS pixels wide without loss of
  content or function.
- **A-7** Text contrast at least 4.5:1; interface components at least 3:1.
- **A-8** Status messages use a polite live region.
- **A-9** `prefers-reduced-motion` is respected; nothing essential animates.
- **A-10** The page language is declared, and every page has a unique title.
- **A-11** Session timeout is warned and can be extended.
- **A-12** axe-core reports no serious or critical issues on any page, and a manual
  NVDA pass finds no blockers.

## 10. Architecture

```
steadytype/
  engine/                  # pure Python, no I/O
    steadytype_engine/
      keys.py  events.py  lesson.py  session.py
      scoring.py  dictation.py  games/
    tests/
  client/
    steadytype_client/
      app.py                 # wx application and frame
      ui/                    # sign-in, lesson surface, pickers, preferences
      speech/                # Prism wrapper, tone player
      capture/               # windows.py, macos.py, x11.py, window_only.py
      store/                 # local SQLite, outbox
      sync/                  # API client, retry, tokens
    tests/
  server/
    app/
      main.py  models.py  auth.py  routes/  templates/  static/
    migrations/
    tests/
  content/
    course.yaml
    lessons/*.yaml
    dictation/*.yaml
  deploy/
    docker-compose.yml  Caddyfile  backup.sh  restore.md
  docs/
```

Dependency rules: the engine imports only the standard library. The client imports
the engine. The server imports neither. Content is data, validated by the engine's
schema.

## 11. Security and privacy

- **S-1** HTTPS only, HSTS for one year, redirect all plain HTTP.
- **S-2** Security headers: `default-src 'self'` content policy, `frame-ancestors
  'none'`, `X-Content-Type-Options: nosniff`, a referrer policy, and no inline
  script.
- **S-3** Containers run as non-root. PostgreSQL is not published outside the
  Compose network. Caddy is the only exposed service.
- **S-4** Uploads are size-limited and validated against the schema.
- **S-5** Student data is a display name, a username, and typing results. No email,
  no address, no date of birth.
- **S-6** A teacher can delete a student and all their attempts; an admin can purge
  a class or a year.
- **S-7** A student's data can be exported as CSV by their teacher.
- **S-8** Dependency scanning runs in CI. Prism is pinned, because it is pre-1.0.
- **S-9** Failed sign-ins, password resets, account changes, and exports are
  audited.

## 12. Deployment and operations

- Ubuntu 24.04 LTS, Docker Engine and the Compose plugin.
- `deploy/docker-compose.yml` with `web`, `db`, `caddy`, and `backup`.
- The domain and an email address are the only required settings, in `.env`.
- Caddy obtains and renews the certificate automatically.
- Nightly `pg_dump` at 02:00, compressed, kept 30 days. If `NAS_PATH` is set during
  setup, the dump is copied there; otherwise it stays on the server and the setup
  prints a warning.
- Restore steps are documented and tested once before the first class uses the
  system.
- `/healthz` checks the database. Logs are structured JSON and rotated.
- Updates are `git pull` and `docker compose up -d`, with a database backup taken
  first by the deploy script.
- The client checks a version endpoint at sign-in and tells the user when a newer
  installer is available. It does not update itself in the first release.

## 13. Testing

- **Engine:** scripted key input produces a transcript of spoken lines and tones,
  stored as golden files. Any change to wording appears in a diff. Scoring is unit
  tested with boundary cases. Each game has its own tests.
- **Curriculum:** a test walks every lesson and fails if a task uses a character or
  key that is not yet taught.
- **Server:** sign-in, lockout, reset, permissions across teachers, sync
  idempotency, offline queue replay, CSV export, and rate limits.
- **Dashboard accessibility:** axe-core through Playwright on every route, plus a
  contrast check and a keyboard-only pass.
- **Client:** a harness injects key events so nearly all behavior is tested without
  a real keyboard. wx smoke tests launch the app and sign in against a test server.
- **Manual matrix:** NVDA and JAWS on Windows, VoiceOver on macOS, Orca on Linux;
  one-handed mode; laptop keyboard; 200 percent zoom.
- **Capture checklist:** every function key, both Shift keys, both Control keys,
  both Alt keys, Tab, Escape, Caps Lock, numpad, Alt Tab, the Windows or Command
  key, and both escape routes.

**Release criteria**

1. A blind student signs in, completes lesson one, and hears a correct result with
   no sighted help.
2. A teacher creates a class, adds a student, and reads that student's progress.
3. Every dashboard page passes axe-core with no serious issues and a manual NVDA
   pass.
4. A network drop mid-lesson loses nothing and syncs on reconnect.
5. The keyboard is released within one second of Escape three times, on every
   platform.

## 14. Milestones

| Milestone | Deliverable | Done when |
|---|---|---|
| M1 | Repository, CI, engine, five lessons, command-line harness | Transcript tests pass; a lesson runs without a UI |
| M2 | Client shell: sign-in, lesson surface, Prism speech, preferences | A lesson is playable with speech on Windows |
| M3 | Windows keyboard capture | Capture checklist passes on Windows |
| M4 | Server, sync, dashboard core | A teacher sees a student's attempt from the client |
| M5 | Full course, three games, dictation, races | Curriculum test passes on all 72 lessons |
| M6 | macOS and Linux capture, accessibility audit, release | Release criteria all pass |

## 15. Open questions

1. **Retention.** How long should attempts be kept before an admin purge is
   suggested? Three years is the default assumption.
2. **Braille keyboard input.** Out of scope now. Revisit when a student needs it.
3. **Academic quizzes.** Out of scope now. Revisit after the browser practice page.
4. **Screen reader key lesson.** TypeAbility taught the JAWS key. A lesson that
   teaches the screen reader's own modifier key would need to detect the reader.
   Later.
5. **Browser practice page.** Next milestone after the first release. Keyboard
   lessons only.
6. **Staff roles.** Admin and teacher are enough for now. A "distance learning
   coordinator" role can wait.

## 16. Risks

| Risk | Mitigation |
|---|---|
| macOS event tap permission confuses users | Detect the permission and show a guided setup screen before the first lesson |
| Antivirus flags the Windows hook | Sign the installer; keep the hook active only during a lesson; document it for school IT |
| Wayland cannot grab the keyboard | Detect Wayland and say so; recommend an X11 session for Linux students |
| wxPython draws some controls itself | Use native lists, choices, and text fields; test each screen with a reader |
| Prism API changes before 1.0 | Pin the version; isolate it behind a small speech adapter |
| Public server is attacked | Rate limits, lockout, no user enumeration, Caddy, fail2ban on the host |
| Content quality slips | Curriculum test, golden transcripts, and a read-through of every lesson |
