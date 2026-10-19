"""My progress: a summary line and a list of finished lessons."""

from __future__ import annotations

import wx


def summary_line(attempts: list[dict]) -> str:
    if not attempts:
        return "You have no saved lessons yet."
    lessons = {attempt.get("lesson_id") for attempt in attempts}
    minutes = sum(attempt.get("active_seconds", 0) for attempt in attempts) / 60
    best = max(attempts, key=lambda attempt: attempt.get("wpm", 0))
    return (f"{len(lessons)} lessons finished, {minutes:.0f} minutes practiced, "
            f"best speed {best.get('wpm', 0):.0f} words per minute.")


def attempt_line(attempt: dict) -> str:
    return (f"Lesson {attempt.get('lesson_id', '?')}: "
            f"{attempt.get('stars', 0)} stars, "
            f"{attempt.get('accuracy', 0):.0f} percent, "
            f"{attempt.get('wpm', 0):.0f} words per minute, "
            f"{(attempt.get('ended_at') or '')[:10]}")


class ProgressDialog(wx.Dialog):
    def __init__(self, parent, attempts: list[dict]) -> None:
        super().__init__(parent, title="My progress")
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        summary = wx.StaticText(panel, label=summary_line(attempts))
        summary.SetName("Summary")
        sizer.Add(summary, 0, wx.ALL, 12)
        sizer.Add(wx.StaticText(panel, label="Finished lessons"), 0, wx.LEFT | wx.TOP, 12)
        self.list = wx.ListBox(panel, choices=[attempt_line(a) for a in reversed(attempts)])
        self.list.SetName("Finished lessons")
        sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 12)
        buttons = wx.StdDialogButtonSizer()
        buttons.AddButton(wx.Button(panel, wx.ID_OK))
        buttons.Realize()
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(sizer)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(outer)
        self.SetSize((560, 420))
        self.list.SetFocus()

    def close(self) -> None:
        self.EndModal(wx.ID_OK)
