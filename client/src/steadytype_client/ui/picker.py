"""Choose a lesson, then a task to start from. Two native lists."""

from __future__ import annotations

import wx
from steadytype_engine.lesson import Course


class LessonPicker(wx.Dialog):
    def __init__(self, parent, course: Course) -> None:
        super().__init__(parent, title="Pick a lesson")
        self.course = course
        self.lesson = None
        self.start_task = 0

        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.HORIZONTAL)

        left = wx.BoxSizer(wx.VERTICAL)
        left.Add(wx.StaticText(panel, label="Lessons"), 0, wx.BOTTOM, 4)
        self.lessons = wx.ListBox(panel, choices=[
            f"{lesson.ordinal}. {lesson.title}" for lesson in course.lessons])
        self.lessons.SetName("Lessons")
        left.Add(self.lessons, 1, wx.EXPAND)
        outer.Add(left, 1, wx.EXPAND | wx.ALL, 12)

        right = wx.BoxSizer(wx.VERTICAL)
        right.Add(wx.StaticText(panel, label="Start at"), 0, wx.BOTTOM, 4)
        self.tasks = wx.ListBox(panel)
        self.tasks.SetName("Tasks")
        right.Add(self.tasks, 1, wx.EXPAND)
        outer.Add(right, 1, wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, 12)

        buttons = wx.StdDialogButtonSizer()
        ok = wx.Button(panel, wx.ID_OK, "Start")
        cancel = wx.Button(panel, wx.ID_CANCEL)
        buttons.AddButton(ok)
        buttons.AddButton(cancel)
        buttons.Realize()

        column = wx.BoxSizer(wx.VERTICAL)
        column.Add(outer, 1, wx.EXPAND)
        column.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(column)
        size = wx.BoxSizer(wx.VERTICAL)
        size.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(size)
        self.SetSize((620, 420))

        self.lessons.Bind(wx.EVT_LISTBOX, self._fill_tasks)
        self.lessons.SetSelection(0)
        self._fill_tasks(None)
        self.lessons.SetFocus()

    def _fill_tasks(self, event) -> None:
        index = self.lessons.GetSelection()
        if index == wx.NOT_FOUND:
            return
        lesson = self.course.lessons[index]
        self.tasks.Set([f"Task {number + 1}: {task.text}" for number, task in enumerate(lesson.tasks)])
        self.tasks.SetSelection(0)

    def selected(self) -> tuple:
        index = self.lessons.GetSelection()
        if index == wx.NOT_FOUND:
            return None, 0
        return self.course.lessons[index], max(0, self.tasks.GetSelection())
