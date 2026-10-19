"""Sign-in rules, kept out of the window so they can be tested."""

from __future__ import annotations

from steadytype_client.store import Account, Store


class SignInError(Exception):
    pass


class SignInPresenter:
    def __init__(self, store: Store) -> None:
        self.store = store

    def remembered(self) -> str | None:
        return self.store.remembered_username()

    def sign_in(self, username: str, password: str, remember: bool) -> Account:
        account = self.store.verify(username, password)
        if account is None:
            raise SignInError("That username and password do not match.")
        self.store.set_remember(account.username, remember)
        return account

    def create_account(self, username: str, password: str, display_name: str) -> Account:
        if len(password) < 10:
            raise SignInError("Use a password of at least ten characters.")
        try:
            return self.store.create_account(username, password, display_name)
        except ValueError as error:
            raise SignInError(str(error)) from error
