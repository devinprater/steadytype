"""Student preferences. Native controls, no custom drawing."""

from __future__ import annotations

import wx
from steadytype_engine.preferences import (
    Feedback,
    Preferences,
    TypingExperience,
    Verbosity,
)

EXPERIENCE = [("Little or none", TypingExperience.LITTLE),
              ("Some", TypingExperience.SOME), ("A lot", TypingExperience.A_LOT)]
FEEDBACK = [("Tone and word", Feedback.BOTH), ("Word only", Feedback.WORD),
            ("Tone only", Feedback.TONE)]
VERBOSITY = [("Standard", Verbosity.STANDARD), ("Brief", Verbosity.BRIEF),
             ("Detailed", Verbosity.DETAILED)]


class PreferencesDialog(wx.Dialog):
    def __init__(self, parent, prefs: Preferences) -> None:
        super().__init__(parent, title="Preferences")
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        def add_choice(label: str, values, current):
            sizer.Add(wx.StaticText(panel, label=label), 0, wx.LEFT | wx.TOP, 12)
            choice = wx.Choice(panel, choices=[name for name, _ in values])
            choice.SetName(label)
            choice.SetSelection([value for _, value in values].index(current))
            sizer.Add(choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
            return choice

        self.experience = add_choice("Typing experience", EXPERIENCE, prefs.typing_experience)
        self.feedback = add_choice("Feedback", FEEDBACK, prefs.feedback)
        self.verbosity = add_choice("How much detail", VERBOSITY, prefs.verbosity)

        sizer.Add(wx.StaticText(panel, label="Double press window in milliseconds"),
                  0, wx.LEFT | wx.TOP, 12)
        self.double_press = wx.SpinCtrl(panel, min=300, max=900, initial=prefs.double_press_ms)
        self.double_press.SetName("Double press window")
        sizer.Add(self.double_press, 0, wx.LEFT | wx.RIGHT, 12)

        self.tones = wx.CheckBox(panel, label="Play sounds")
        self.tones.SetValue(prefs.tones)
        sizer.Add(self.tones, 0, wx.ALL, 12)
        self.one_handed = wx.CheckBox(panel, label="One-handed typing")
        self.one_handed.SetValue(prefs.one_handed)
        sizer.Add(self.one_handed, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.laptop = wx.CheckBox(panel, label="Laptop keyboard with one Enter and one Control")
        self.laptop.SetValue(prefs.laptop_keyboard)
        sizer.Add(self.laptop, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        sizer.Add(wx.StaticText(panel, label="Speech rate"), 0, wx.LEFT, 12)
        self.rate = wx.Slider(panel, minValue=0, maxValue=100, value=int(prefs.rate * 100))
        self.rate.SetName("Speech rate")
        sizer.Add(self.rate, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        buttons = wx.StdDialogButtonSizer()
        buttons.AddButton(wx.Button(panel, wx.ID_OK))
        buttons.AddButton(wx.Button(panel, wx.ID_CANCEL))
        buttons.Realize()
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)

        panel.SetSizer(sizer)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(outer)

    def value(self) -> Preferences:
        return Preferences(
            typing_experience=EXPERIENCE[self.experience.GetSelection()][1],
            feedback=FEEDBACK[self.feedback.GetSelection()][1],
            verbosity=VERBOSITY[self.verbosity.GetSelection()][1],
            double_press_ms=self.double_press.GetValue(),
            tones=self.tones.GetValue(),
            one_handed=self.one_handed.GetValue(),
            laptop_keyboard=self.laptop.GetValue(),
            rate=self.rate.GetValue() / 100,
        )
