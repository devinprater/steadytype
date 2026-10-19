"""The main window: native menus, a status line, and the lesson surface."""

from __future__ import annotations

import wx

from steadytype_client.ui.keys import from_wx
from steadytype_client.ui.surface import LessonSurface


class MainFrame(wx.Frame):
    def __init__(self, controller) -> None:
        super().__init__(None, title="SteadyType")
        self.controller = controller
        controller.frame = self

        panel = wx.Panel(self)
        self.surface = LessonSurface(panel)
        self.status = wx.StaticText(panel, label="Ready")
        self.status.SetName("Status")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.surface, 1, wx.EXPAND | wx.ALL, 12)
        sizer.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        panel.SetSizer(sizer)

        self._build_menu()
        self.SetSize((900, 560))
        self.Centre()
        self.surface.SetFocus()

        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _build_menu(self) -> None:
        menu = wx.MenuBar()

        file_menu = wx.Menu()
        self._item(file_menu, "Switch student", self.controller.switch_student)
        file_menu.AppendSeparator()
        self._item(file_menu, "Quit", self.controller.quit)
        menu.Append(file_menu, "&File")

        lesson = wx.Menu()
        self._item(lesson, "Continue", lambda: self.controller.next_lesson())
        self._item(lesson, "Repeat this lesson", lambda: self.controller.repeat_lesson())
        self._item(lesson, "Pick a lesson...", self.controller.open_picker)
        lesson.AppendSeparator()
        self._item(lesson, "Dictation", lambda: self.controller.run_command("dictation"))
        self._item(lesson, "Timed test", lambda: self.controller.run_command("test"))
        self._item(lesson, "Race", lambda: self.controller.run_command("race"))
        menu.Append(lesson, "&Lesson")

        view = wx.Menu()
        self._item(view, "My progress", self.controller.show_progress)
        self._item(view, "Preferences", self.controller.open_preferences)
        menu.Append(view, "&View")

        help_menu = wx.Menu()
        self._item(help_menu, "Keyboard commands", self._show_help)
        menu.Append(help_menu, "&Help")

        self.SetMenuBar(menu)

    def _item(self, menu, label: str, action) -> None:
        item = menu.Append(wx.ID_ANY, label)
        self.Bind(wx.EVT_MENU, lambda event: action(), item)

    def _show_help(self) -> None:
        import wx

        text = (
            "F1 twice: repeat the instructions.\n"
            "F2 twice: next lesson. F2 three times: repeat this lesson.\n"
            "F3 twice: pick a lesson. F4 twice: dictation. F5 twice: race.\n"
            "F6 twice: timed test. F12 twice: my progress.\n"
            "Escape three times: leave the lesson and quit.\n"
            "Control Alt Shift X: leave any lesson, even the function key lesson.\n"
            "Every one of these is also in the menus.")
        self.controller.speech.speak(text)
        wx.MessageBox(text, "Keyboard commands", wx.OK | wx.ICON_INFORMATION, self)

    def set_status(self, text: str) -> None:
        self.status.SetLabel(text)
        self.status.GetParent().Layout()

    def _on_key(self, event) -> None:
        key_event = from_wx(event)
        if key_event is not None and self.controller.on_key(key_event):
            return
        event.Skip()

    def _on_close(self, event) -> None:
        self.controller.stop_lesson()
        event.Skip()
