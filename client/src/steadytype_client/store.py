"""Local accounts, preferences, and attempts in SQLite."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1


@dataclass(frozen=True)
class Account:
    id: int
    username: str
    display_name: str


class Store:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        with self._db:
            self._db.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL,
                    salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS preferences (
                    account_id INTEGER PRIMARY KEY,
                    body TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY,
                    account_id INTEGER NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

    # -- accounts -------------------------------------------------------
    def create_account(self, username: str, password: str, display_name: str) -> Account:
        username = username.strip()
        if not username or not password:
            raise ValueError("A username and a password are required.")
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=SCRYPT_N,
                                r=SCRYPT_R, p=SCRYPT_P, dklen=32)
        try:
            with self._lock, self._db:
                cursor = self._db.execute(
                    "INSERT INTO accounts (username, display_name, salt, password_hash, created_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (username, display_name or username, salt, digest,
                     datetime.now(UTC).isoformat()))
        except sqlite3.IntegrityError as error:
            raise ValueError("That username is already taken.") from error
        return Account(id=cursor.lastrowid, username=username,
                       display_name=display_name or username)

    def verify(self, username: str, password: str) -> Account | None:
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM accounts WHERE username = ?", (username.strip(),)).fetchone()
        if row is None:
            return None
        digest = hashlib.scrypt(password.encode("utf-8"), salt=row["salt"], n=SCRYPT_N,
                                r=SCRYPT_R, p=SCRYPT_P, dklen=32)
        if not hmac.compare_digest(digest, row["password_hash"]):
            return None
        return Account(id=row["id"], username=row["username"],
                       display_name=row["display_name"])

    # -- remembering ----------------------------------------------------
    def set_remember(self, username: str | None, remember: bool) -> None:
        value = username if remember and username else ""
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO settings (key, value) VALUES ('remembered_username', ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value", (value,))

    def remembered_username(self) -> str | None:
        with self._lock:
            row = self._db.execute(
                "SELECT value FROM settings WHERE key = 'remembered_username'").fetchone()
        if row is None or not row["value"]:
            return None
        return row["value"]

    # -- preferences ----------------------------------------------------
    def save_preferences(self, account_id: int, body: dict) -> None:
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO preferences (account_id, body) VALUES (?, ?)"
                " ON CONFLICT(account_id) DO UPDATE SET body = excluded.body",
                (account_id, json.dumps(body)))

    def load_preferences(self, account_id: int) -> dict:
        with self._lock:
            row = self._db.execute(
                "SELECT body FROM preferences WHERE account_id = ?", (account_id,)).fetchone()
        return json.loads(row["body"]) if row else {}

    # -- attempts -------------------------------------------------------
    def save_attempt(self, account_id: int, record) -> None:
        import dataclasses
        body = dataclasses.asdict(record) if dataclasses.is_dataclass(record) else dict(record)
        attempt_id = str(body.get("id", ""))
        with self._lock, self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO attempts (id, account_id, body, created_at)"
                " VALUES (?, ?, ?, ?)",
                (attempt_id, account_id, json.dumps(body, default=str),
                 datetime.now(UTC).isoformat()))

    def attempts(self, account_id: int) -> list[dict]:
        with self._lock:
            rows = self._db.execute(
                "SELECT body FROM attempts WHERE account_id = ? ORDER BY created_at",
                (account_id,)).fetchall()
        return [json.loads(row["body"]) for row in rows]
