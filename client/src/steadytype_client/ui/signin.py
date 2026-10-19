"""The sign-in window. Native controls, focus in the right place."""

from __future__ import annotations

import wx

from steadytype_client.signin import SignInError, SignInPresenter


class SignInDialog(wx.Dialog):
    def __init__(self, parent, presenter: SignInPresenter, speak=None) -> None:
        super().__init__(parent, title="Sign in to SteadyType")
        self.presenter = presenter
        self.account = None
        self._speak = speak or (lambda text: None)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="Sign in")
        title_font = title.GetFont()
        title_font.SetPointSize(title_font.GetPointSize() + 6)
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL, 12)

        sizer.Add(wx.StaticText(panel, label="Username"), 0, wx.LEFT | wx.TOP, 12)
        self.username = wx.TextCtrl(panel)
        self.username.SetName("Username")
        sizer.Add(self.username, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        sizer.Add(wx.StaticText(panel, label="Password"), 0, wx.LEFT | wx.TOP, 12)
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password.SetName("Password")
        sizer.Add(self.password, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.remember = wx.CheckBox(panel, label="Remember my username")
        sizer.Add(self.remember, 0, wx.ALL, 12)

        self.error = wx.StaticText(panel, label="")
        sizer.Add(self.error, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        row = wx.BoxSizer(wx.HORIZONTAL)
        self.sign_in_button = wx.Button(panel, label="Sign in")
        self.create_button = wx.Button(panel, label="Create a local account")
        row.Add(self.sign_in_button, 0, wx.RIGHT, 8)
        row.Add(self.create_button, 0)
        sizer.Add(row, 0, wx.ALL, 12)

        panel.SetSizer(sizer)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(outer)
        self.SetSize((460, -1))

        self.sign_in_button.SetDefault()
        remembered = presenter.remembered()
        if remembered:
            self.username.SetValue(remembered)
            self.remember.SetValue(True)
            self.sign_in_button.SetFocus()
        else:
            self.username.SetFocus()

        self.sign_in_button.Bind(wx.EVT_BUTTON, self._on_sign_in)
        self.create_button.Bind(wx.EVT_BUTTON, self._on_create)
        self.password.Bind(wx.EVT_TEXT_ENTER, self._on_sign_in)

    def _fail(self, message: str) -> None:
        self.error.SetLabel(message)
        self.error.Wrap(420)
        self.Layout()
        self._speak(message)

    def _on_sign_in(self, event) -> None:
        try:
            self.account = self.presenter.sign_in(
                self.username.GetValue(), self.password.GetValue(),
                self.remember.GetValue())
        except SignInError as error:
            self._fail(str(error))
            self.password.SetFocus()
            self.password.SelectAll()
            return
        self.EndModal(wx.ID_OK)

    def _on_create(self, event) -> None:
        name = wx.GetTextFromUser("What should the teacher call you?",
                                  "Create a local account", parent=self)
        if not name:
            return
        try:
            self.account = self.presenter.create_account(
                self.username.GetValue(), self.password.GetValue(), name)
        except SignInError as error:
            self._fail(str(error))
            return
        self.EndModal(wx.ID_OK)
