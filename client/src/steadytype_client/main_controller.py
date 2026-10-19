"""Connect the windows to the lesson presenter, the keyboard, and the store."""

from __future__ import annotations

import os
from dataclasses import asdict, replace

from steadytype_engine.keys import Key, KeyEvent, Modifier
from steadytype_engine.lesson import Course, Lesson
from steadytype_engine.names import localize
from steadytype_engine.preferences import Preferences
from steadytype_engine.scoring import Goals

from steadytype_client.capture import make_capture
from steadytype_client.prefs_json import from_dict, to_dict
from steadytype_client.presenter import LessonPresenter
from steadytype_client.router import FUNCTION_KEYS, CommandRouter
from steadytype_client.sync import SyncClient, remote_token


def is_panic(event: KeyEvent) -> bool:
    """Control Alt Shift X leaves any lesson, including the function-key lesson."""
    return (event.key is Key.X
            and Modifier.CONTROL in event.modifiers
            and Modifier.ALT in event.modifiers
            and Modifier.SHIFT in event.modifiers)


class AppController:
    def __init__(self, store, account, paths, speech, player, course: Course) -> None:
        self.store = store
        self.account = account
        self.paths = paths
        self.speech = speech
        self.player = player
        self.course = course
        self.prefs = self._load_preferences()
        self._apply_speech()
        self.router = CommandRouter(self.prefs.double_press_ms)
        self.presenter: LessonPresenter | None = None
        self.lesson_index = 0
        self.capture = make_capture()
        self.capture_ok = False
        self.frame = None
        self.switch_requested = False
        self.sync = None
        self.test_runner = None
        self.dictation_runner = None
        self.game_runner = None
        self.game_index = 0
        self.next_ready = False
        self.dictation_index = 0
        self.test_timer = None
        server = os.environ.get("STEADYTYPE_SERVER") or self.store.get_setting("server")
        if server:
            token = self.store.get_setting("sync_token")
            if self.store.get_setting("sync_server") != server:
                token = None
            if not token:
                token = remote_token(server, account.username)
            if token:
                self.sync = SyncClient(server, token)
                try:
                    self.sync.upload(self.store.attempts(account.id))
                except Exception:  # noqa: BLE001, S110 - offline is a normal state
                    pass

    # -- preferences ----------------------------------------------------
    def _load_preferences(self) -> Preferences:
        body = self.store.load_preferences(self.account.id)
        return from_dict(body) if body else Preferences()

    def _save_preferences(self) -> None:
        self.store.save_preferences(self.account.id, to_dict(self.prefs))

    def _apply_speech(self) -> None:
        try:
            self.speech.configure(self.prefs.rate, self.prefs.pitch,
                                  self.prefs.volume, self.prefs.voice)
        except Exception:  # noqa: BLE001, S110 - a backend may not support every voice setting
            pass

    def begin(self) -> None:
        """Speak a welcome and start where the student left off."""
        done = {a.get("lesson_id") for a in self.store.attempts(self.account.id)
                if a.get("kind") in ("practice", "race")}
        index = next((i for i, lesson in enumerate(self.course.lessons)
                      if lesson.id not in done), 0)
        self.lesson_index = index
        lesson = self.course.lessons[index]
        welcome = (f"Signed in as {self.account.display_name}. "
                   f"Lesson {lesson.id}, {lesson.title}.")
        self.speech.speak(welcome, True)
        import wx

        # Give the welcome time to be heard before the lesson starts speaking.
        wx.CallLater(max(1500, len(welcome) * 55), self.start_lesson, lesson)

    # -- lessons --------------------------------------------------------
    def start_lesson(self, lesson: Lesson, start_task: int = 0) -> None:
        self.stop_lesson()
        if start_task > 0:
            lesson = replace(lesson, tasks=lesson.tasks[start_task:])
        self.next_ready = False
        self.router.reset()
        self.router.enabled = "f1" not in lesson.teaches
        self.presenter = LessonPresenter(
            lesson, self.prefs, Goals(), self.speech, self.player,
            save=self._save_attempt, display=self.frame.surface, later=self._later)
        self.capture_ok = False
        if self.capture is not None:
            self.capture_ok = self.capture.start(self._from_capture)
        if self.capture_ok:
            if self.router.enabled:
                self.speech.speak("Keyboard captured. Press Escape three times to leave. "
                                  + localize("Control Alt Shift X also leaves."))
            else:
                self.speech.speak("Keyboard captured. Function key commands are off in "
                                  "this lesson. Press "
                                  + localize("Control Alt Shift X") + " to leave.")
        else:
            self.speech.speak("The keyboard is not captured. Keep this window in front.")
        if self.frame is not None:
            self.frame.set_status(lesson.title)
        self.presenter.start()

    def next_lesson(self) -> None:
        if not self.course.lessons:
            return
        self.lesson_index = min(self.lesson_index + 1, len(self.course.lessons) - 1)
        self.start_lesson(self.course.lessons[self.lesson_index])

    def repeat_lesson(self) -> None:
        self.start_lesson(self.course.lessons[self.lesson_index])

    def stop_lesson(self) -> None:
        if self.capture is not None:
            self.capture.stop()
        self.capture_ok = False
        self.presenter = None

    def _save_attempt(self, record) -> None:
        self.store.save_attempt(self.account.id, record)
        if self.sync is not None:
            try:
                self.sync.upload([asdict(record)])
            except Exception:  # noqa: BLE001, S110 - the local copy is the source of truth
                pass

    def _from_capture(self, event) -> None:
        if self.frame is not None:
            self.frame.CallAfter(self.on_key, event)

    # -- keys -----------------------------------------------------------
    def on_key(self, event) -> bool:
        if is_panic(event):
            self.quit()
            return True
        if self.game_runner is not None and not self.game_runner.done:
            self.game_runner.handle(event)
            if self.game_runner.done:
                self._end_game()
            return True
        if self.dictation_runner is not None and not self.dictation_runner.done:
            self.dictation_runner.handle(event)
            if self.dictation_runner.done:
                self._end_dictation()
            return True
        if self.test_runner is not None and not self.test_runner.done:
            self.test_runner.handle(event)
            if self.test_runner.done:
                self._end_timed_test()
            return True
        if self.presenter is None:
            if self.next_ready and event.key is Key.ENTER:
                self.next_ready = False
                self.next_lesson()
                return True
            return False
        if not self.router.enabled:
            self.presenter.handle(event)
            return True
        command = self.router.feed(event)
        if command:
            self.run_command(command)
            return True
        if event.key in FUNCTION_KEYS or event.key is Key.ESCAPE:
            return True
        self.presenter.handle(event)
        if self.presenter.finished:
            self._lesson_finished()
        return True

    def _later(self, milliseconds: int, action) -> None:
        import wx

        wx.CallLater(milliseconds, action)

    def _lesson_finished(self) -> None:
        self.next_ready = True
        self.stop_lesson()
        if self.frame is not None:
            self.frame.set_status("Lesson complete")

    def run_command(self, name: str) -> None:
        if name == "quit":
            self.quit()
        elif name == "repeat" and self.presenter is not None:
            self.presenter.repeat()
        elif name == "next":
            self.next_lesson()
        elif name == "pick":
            self.open_picker()
        elif name == "progress":
            self.show_progress()
        elif name == "preferences":
            self.open_preferences()
        elif name == "test":
            self.start_timed_test()
        elif name == "dictation":
            self.start_dictation()
        elif name == "game":
            self.start_game()
        elif name == "race":
            self.start_race()

    # -- windows --------------------------------------------------------
    # -- games ----------------------------------------------------------
    def start_game(self) -> None:
        from steadytype_engine.games.missing_letter import MissingLetterGame
        from steadytype_engine.games.select_delete import SelectDeleteGame
        from steadytype_engine.games.wrong_letter import WrongLetterGame

        from steadytype_client.game_runner import GameRunner

        games = (MissingLetterGame(), WrongLetterGame(), SelectDeleteGame())
        game = games[self.game_index % len(games)]
        self.game_index += 1
        self.stop_lesson()
        surface = self.frame.surface if self.frame is not None else None
        self.game_runner = GameRunner(
            game, save=self._save_attempt, speak=self.speech.speak,
            display=surface.show if surface is not None else None)
        self.capture_ok = False
        if self.capture is not None:
            self.capture_ok = self.capture.start(self._from_capture)
        if self.frame is not None:
            self.frame.set_status("Game")
        if not self.capture_ok:
            self.speech.speak("The keyboard is not captured. Keep this window in front.")
        self.game_runner.start()

    def _end_game(self) -> None:
        self.stop_lesson()
        self.game_runner = None
        if self.frame is not None:
            self.frame.set_status("Game over")

    # -- dictation ------------------------------------------------------
    def start_dictation(self) -> None:
        from steadytype_client.dictation_runner import PASSAGES, DictationRunner

        self.stop_lesson()
        passage = PASSAGES[self.dictation_index % len(PASSAGES)]
        self.dictation_index += 1
        surface = self.frame.surface if self.frame is not None else None
        self.dictation_runner = DictationRunner(
            passage, self.prefs, save=self._save_attempt, speak=self.speech.speak,
            display=surface.show if surface is not None else None)
        self.capture_ok = False
        if self.capture is not None:
            self.capture_ok = self.capture.start(self._from_capture)
        if self.frame is not None:
            self.frame.set_status(f"Dictation: {passage.title}")
        if not self.capture_ok:
            self.speech.speak("The keyboard is not captured. Keep this window in front.")
        self.dictation_runner.start()

    def _end_dictation(self) -> None:
        self.stop_lesson()
        self.dictation_runner = None
        if self.frame is not None:
            self.frame.set_status("Dictation complete")

    # -- timed test -----------------------------------------------------
    TEST_PASSAGE = (
        "A steady hand and an even pace will carry you through the whole page. "
        "Read a few words ahead and let your fingers follow what your eyes have "
        "already seen. If you make a mistake, keep going, because the clock "
        "does not stop for corrections."
    )

    def start_timed_test(self, seconds: int = 300) -> None:
        import wx
        from steadytype_engine.dictation import Passage

        from steadytype_client.timed import TimedTestRunner

        self.stop_lesson()
        passage = Passage(title="Certification practice", text=self.TEST_PASSAGE)
        surface = self.frame.surface if self.frame is not None else None
        self.test_runner = TimedTestRunner(
            passage, seconds, save=self._save_attempt, speak=self.speech.speak,
            display=surface.show if surface is not None else None)
        self.capture_ok = False
        if self.capture is not None:
            self.capture_ok = self.capture.start(self._from_capture)
        if self.frame is not None:
            self.frame.set_status("Timed test")
            self.test_timer = wx.Timer(self.frame)
            self.frame.Bind(wx.EVT_TIMER, self._on_test_tick, self.test_timer)
            self.test_timer.Start(500)
        if not self.capture_ok:
            self.speech.speak("The keyboard is not captured. Keep this window in front.")
        self.test_runner.start()

    def start_race(self) -> None:
        import wx

        from steadytype_client.race import RaceRunner

        self.stop_lesson()
        surface = self.frame.surface if self.frame is not None else None
        self.test_runner = RaceRunner(
            save=self._save_attempt, speak=self.speech.speak,
            display=surface.show if surface is not None else None)
        self.capture_ok = False
        if self.capture is not None:
            self.capture_ok = self.capture.start(self._from_capture)
        if self.frame is not None:
            self.frame.set_status("Race")
            self.test_timer = wx.Timer(self.frame)
            self.frame.Bind(wx.EVT_TIMER, self._on_test_tick, self.test_timer)
            self.test_timer.Start(500)
        if not self.capture_ok:
            self.speech.speak("The keyboard is not captured. Keep this window in front.")
        self.test_runner.start()

    def _on_test_tick(self, event) -> None:
        import time as _time

        if self.test_runner is not None:
            self.test_runner.tick(_time.monotonic())
            if self.test_runner.done:
                self._end_timed_test()

    def _end_timed_test(self) -> None:
        if self.test_timer is not None:
            import wx

            self.test_timer.Stop()
            if self.frame is not None:
                self.frame.Unbind(wx.EVT_TIMER, handler=self._on_test_tick)
            self.test_timer = None
        self.stop_lesson()
        self.test_runner = None
        if self.frame is not None:
            self.frame.set_status("Timed test complete")

    def open_picker(self) -> None:
        import wx

        from steadytype_client.ui.picker import LessonPicker

        dialog = LessonPicker(self.frame, self.course)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                lesson, task = dialog.selected()
                if lesson is not None:
                    self.lesson_index = self.course.lessons.index(lesson)
                    self.start_lesson(lesson, task)
        finally:
            dialog.Destroy()

    def open_preferences(self) -> None:
        import wx

        from steadytype_client.ui.preferences import PreferencesDialog

        dialog = PreferencesDialog(self.frame, self.prefs)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.prefs = dialog.value()
                self._save_preferences()
                self._apply_speech()
                self.router.window = self.prefs.double_press_ms / 1000
                self.speech.speak("Preferences saved.")
        finally:
            dialog.Destroy()

    def show_progress(self) -> None:

        from steadytype_client.ui.progress import ProgressDialog, summary_line

        attempts = self.store.attempts(self.account.id)
        message = summary_line(attempts)
        self.speech.speak(message)
        dialog = ProgressDialog(self.frame, attempts)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def switch_student(self) -> None:
        import wx

        from steadytype_client.signin import SignInPresenter
        from steadytype_client.ui.signin import SignInDialog

        self.stop_lesson()
        self.switch_requested = True
        if self.frame is not None:
            self.frame.Hide()
        dialog = SignInDialog(None, SignInPresenter(self.store), speak=self.speech.speak)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.account = dialog.account
                self.prefs = self._load_preferences()
                self.router = CommandRouter(self.prefs.double_press_ms)
                self._apply_speech()
                self.switch_requested = False
                if self.frame is not None:
                    self.frame.Show()
                return
        finally:
            dialog.Destroy()
        self.quit()

    def quit(self) -> None:
        self.stop_lesson()
        if self.frame is not None:
            self.frame.Close()
