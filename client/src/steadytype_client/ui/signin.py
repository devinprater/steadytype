"""The sign-in window: a username for students, a password for staff."""

from __future__ import annotations

import wx

from steadytype_client.signin import SignInError, SignInPresenter


class SignInDialog(wx.Dialog):
    def __init__(self, parent, presenter: SignInPresenter, speak=None) -> None:
        super().__init__(parent, title="Sign in to SteadyType")
        self.presenter = presenter
        self.account = None
        self._speak = speak or (lambda text: None)
        self.staff_mode = False

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="Sign in")
        font = title.GetFont()
        font.SetPointSize(font.GetPointSize() + 6)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL, 12)

        self.hint = wx.StaticText(panel, label="Type your username, like prater.devin.")
        sizer.Add(self.hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        sizer.Add(wx.StaticText(panel, label="Username"), 0, wx.LEFT | wx.TOP, 12)
        self.username = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.username.SetName("Username")
        sizer.Add(self.username, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.password_label = wx.StaticText(panel, label="Password")
        self.password = wx.TextCtrl(panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password.SetName("Password")
        sizer.Add(self.password_label, 0, wx.LEFT | wx.TOP, 12)
        sizer.Add(self.password, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.password_label.Show(False)
        self.password.Show(False)

        self.remember = wx.CheckBox(panel, label="Remember my username")
        self.remember.SetValue(True)
        sizer.Add(self.remember, 0, wx.ALL, 12)

        self.error = wx.StaticText(panel, label="")
        sizer.Add(self.error, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        row = wx.BoxSizer(wx.HORIZONTAL)
        self.sign_in_button = wx.Button(panel, label="Sign in")
        self.staff_button = wx.Button(panel, label="Staff sign in")
        self.create_button = wx.Button(panel, label="Create this student")
        row.Add(self.sign_in_button, 0, wx.RIGHT, 8)
        row.Add(self.staff_button, 0, wx.RIGHT, 8)
        row.Add(self.create_button, 0)
        sizer.Add(row, 0, wx.ALL, 12)

        self.create_button.Show(not presenter.has_accounts())

        panel.SetSizer(sizer)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(outer)
        self.SetSize((480, -1))

        self.sign_in_button.SetDefault()
        remembered = presenter.remembered()
        if remembered:
            self.username.SetValue(remembered)
            self.sign_in_button.SetFocus()
        else:
            self.username.SetFocus()

        self.sign_in_button.Bind(wx.EVT_BUTTON, self._on_sign_in)
        self.staff_button.Bind(wx.EVT_BUTTON, self._toggle_staff)
        self.create_button.Bind(wx.EVT_BUTTON, self._on_create)
        self.username.Bind(wx.EVT_TEXT_ENTER, self._on_sign_in)
        self.password.Bind(wx.EVT_TEXT_ENTER, self._on_sign_in)

    def _fail(self, message: str) -> None:
        self.error.SetLabel(message)
        self.error.Wrap(440)
        self.Layout()
        self._speak(message)

    def _toggle_staff(self, event) -> None:
        self.staff_mode = not self.staff_mode
        self.password_label.Show(self.staff_mode)
        self.password.Show(self.staff_mode)
        self.hint.SetLabel(
            "Staff sign in. Use your staff username and password."
            if self.staff_mode else
            "Type your username, like prater.devin.")
        self.staff_button.SetLabel("Student sign in" if self.staff_mode else "Staff sign in")
        self.create_button.Show(False if self.staff_mode else not self.presenter.has_accounts())
        self.Layout()
        self.Fit()
        (self.password if self.staff_mode else self.username).SetFocus()

    def _on_sign_in(self, event) -> None:
        username = self.username.GetValue()
        remember = self.remember.GetValue()
        try:
            if self.staff_mode:
                self.account = self.presenter.sign_in_staff(
                    username, self.password.GetValue(), remember)
            else:
                self.account = self.presenter.sign_in_student(username, remember)
        except SignInError as error:
            self._fail(str(error))
            return
        self.EndModal(wx.ID_OK)

    def _on_create(self, event) -> None:
        try:
            self.account = self.presenter.create_student(self.username.GetValue())
        except SignInError as error:
            self._fail(str(error))
            return
        self.presenter.store.set_remember(self.account.username, self.remember.GetValue())
        self.EndModal(wx.ID_OK)
