"""Sign-in rules, kept out of the window so they can be tested.

Students sign in with a username only, in the form lastname.firstname.
Staff sign in with a username and a password.
"""

from __future__ import annotations

import re

from steadytype_client.store import Account, Store
from steadytype_client.sync import normalize_server, remote_staff_token, remote_token

USERNAME = re.compile(r"^[a-z][a-z'\-]*\.[a-z][a-z'\-]*$")


class SignInError(Exception):
    pass


def normalize_username(username: str) -> str:
    return username.strip().lower()


def check_username(username: str) -> str:
    normalized = normalize_username(username)
    if not USERNAME.match(normalized):
        raise SignInError("Use lastname.firstname, like prater.devin.")
    return normalized


class SignInPresenter:
    def __init__(self, store: Store, remote=None, remote_staff=None) -> None:
        self.store = store
        self._remote = remote or remote_token
        self._remote_staff = remote_staff or remote_staff_token

    # -- the school server ----------------------------------------------
    def server_address(self) -> str:
        return self.store.get_setting("server") or ""

    def set_server_address(self, raw: str) -> str:
        try:
            server = normalize_server(raw)
        except ValueError as error:
            raise SignInError(str(error)) from error
        self.store.set_setting("server", server)
        return server

    def _remember_token(self, server: str, token: str) -> None:
        self.store.set_setting("sync_server", server)
        self.store.set_setting("sync_token", token)

    def remembered(self) -> str | None:
        return self.store.remembered_username()

    def has_accounts(self) -> bool:
        return self.store.has_accounts()

    def sign_in_student(self, username: str, remember: bool = True) -> Account:
        normalized = check_username(username)
        account = self.store.find_student(normalized)
        server = self.server_address()
        if account is None and server:
            token = self._remote(server, normalized)
            if token:
                account = self.store.create_student(normalized)
                self._remember_token(server, token)
        if account is None:
            raise SignInError("That username was not found. Ask your teacher.")
        self.store.set_remember(account.username, remember)
        return account

    def sign_in_staff(self, username: str, password: str,
                      remember: bool = True) -> Account:
        normalized = normalize_username(username)
        account = self.store.verify_staff(normalized, password)
        server = self.server_address()
        if account is None and server:
            token = self._remote_staff(server, normalized, password)
            if token:
                try:
                    account = self.store.create_staff(normalized, password)
                except ValueError:
                    account = self.store.verify_staff(normalized, password)
                self._remember_token(server, token)
        if account is None:
            raise SignInError("That staff username and password do not match.")
        self.store.set_remember(account.username, remember)
        return account

    def create_student(self, username: str) -> Account:
        normalized = check_username(username)
        try:
            return self.store.create_student(normalized)
        except ValueError as error:
            raise SignInError(str(error)) from error

    def create_staff(self, username: str, password: str, display_name: str) -> Account:
        if len(password) < 10:
            raise SignInError("Use a staff password of at least ten characters.")
        try:
            return self.store.create_staff(username, password, display_name)
        except ValueError as error:
            raise SignInError(str(error)) from error
