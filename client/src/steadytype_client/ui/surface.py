"""The lesson text: a native read-only field, so magnifiers can follow the caret.

Nothing is custom drawn here any more. A native text control keeps a real text
caret and insertion point, which is what Windows Magnifier and VoiceOver's zoom
follow. It also inherits system colours, so Windows high contrast and macOS
Increase Contrast are respected without us guessing at a palette.
"""

from __future__ import annotations

import wx


class LessonSurface(wx.TextCtrl):
    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            value="",
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_NOHIDESEL,
        )
        self.SetName("Lesson text")
        font = self.GetFont()
        font.SetPointSize(font.GetPointSize() + 14)
        font.SetFamily(wx.FONTFAMILY_TELETYPE)
        self.SetFont(font)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        self.SetInsertionPoint(0)

    def show(self, text: str, position: int) -> None:
        """Put the lesson text on screen with the caret where the student is."""
        if self.GetValue() != text:
            self.ChangeValue(text)
        position = max(0, min(position, len(text)))
        self.SetInsertionPoint(position)
        self.ShowPosition(position)
        self.Refresh()
