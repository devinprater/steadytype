"""Send finished attempts to the SteadyType server. Best effort, never blocking."""

from __future__ import annotations

import httpx


class SyncUnavailable(Exception):
    pass


def remote_token(base_url: str, username: str, client=None) -> str | None:
    """Students sign in with a username; a failure means practice offline."""
    try:
        poster = client.post if client is not None else httpx.post
        response = poster(f"{base_url.rstrip('/')}/api/v1/auth/student",
                          json={"username": username}, timeout=10)
        if response.status_code != 200:
            return None
        return response.json().get("token")
    except Exception:  # noqa: BLE001 - the server may simply be unreachable
        return None


class SyncClient:
    def __init__(self, base_url: str, token: str, client=None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._client = client

    def upload(self, attempts: list[dict]) -> int:
        if not attempts:
            return 0
        headers = {"Authorization": f"Bearer {self.token}"}
        poster = self._client.post if self._client is not None else httpx.post
        try:
            response = poster(f"{self.base_url}/api/v1/attempts", json=attempts,
                              headers=headers, timeout=15)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise SyncUnavailable(str(error)) from error
        return int(response.json().get("accepted", 0))
