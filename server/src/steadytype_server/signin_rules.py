"""The one username rule, shared by the dashboard and the API."""

from __future__ import annotations

import re

USERNAME = re.compile(r"^[a-z][a-z'\-]*\.[a-z][a-z'\-]*$")


class SignInError(Exception):
    pass


def check_username(username: str) -> str:
    if not USERNAME.match(username):
        raise SignInError("Use lastname.firstname, like prater.devin.")
    return username
