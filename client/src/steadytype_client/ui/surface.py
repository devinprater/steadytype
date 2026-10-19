"""The one custom-drawn control: the lesson text. It exposes no children."""

from __future__ import annotations

import wx


class LessonSurface(wx.Panel):
    def __init__(self, parent) -> None:
        super().__init__(parent, style=wx.WANTS_CHARS)
        self.text = ""
        self.position = 0
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetName("Lesson text")
        self.Bind(wx.EVT_PAINT, self._paint)

    def show(self, text: str, position: int) -> None:
        self.text = text
        self.position = max(0, min(position, len(text)))
        self.Refresh()

    def _paint(self, event) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        font = wx.Font(wx.FontInfo(30).Family(wx.FONTFAMILY_TELETYPE))
        dc.SetFont(font)
        x, y = 24, 24
        done, rest = self.text[:self.position], self.text[self.position:]
        dc.SetTextForeground(wx.Colour(20, 20, 20))
        width_done, height = dc.GetTextExtent(done)
        dc.DrawText(done, x, y)
        dc.SetTextForeground(wx.Colour(20, 20, 20))
        dc.DrawText(rest, x + width_done, y)
        if self.position < len(self.text):
            char_width, _ = dc.GetTextExtent(self.text[self.position])
            pen = wx.Pen(wx.Colour(20, 20, 120), 3)
            dc.SetPen(pen)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(x + width_done - 2, y - 3, max(char_width, 6) + 4, height + 6)
        elif self.text:
            dc.SetPen(wx.Pen(wx.Colour(20, 20, 120), 3))
            dc.DrawLine(x + width_done + 4, y - 3, x + width_done + 4, y + height + 3)
