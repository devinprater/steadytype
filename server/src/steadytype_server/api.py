"""The client API: sign in, fetch the course, upload attempts."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .db import utcnow
from .models import Attempt, Device, User
from .security import new_token, token_hash, verify_password

router = APIRouter(prefix="/api/v1")
TOKEN_DAYS = 30


class StudentLogin(BaseModel):
    username: str


class StaffLogin(BaseModel):
    username: str
    password: str


class AttemptIn(BaseModel):
    id: str
    lesson_id: int
    kind: str = "practice"
    started_at: str | None = None
    active_seconds: float = 0
    characters: int = 0
    keypresses: int = 0
    errors: int = 0
    wpm: float = 0
    accuracy: float = 0
    real_accuracy: float = 0
    stars: int = 0
    key_stats: list[dict[str, Any]] = Field(default_factory=list)


def _issue(request: Request, user: User) -> dict:
    token = new_token()
    with request.app.state.Session() as db:
        db.add(Device(user_id=user.id, token_hash=token_hash(token),
                      expires_at=utcnow() + timedelta(days=TOKEN_DAYS)))
        db.commit()
    return {"token": token,
            "user": {"id": user.id, "username": user.username,
                     "display_name": user.display_name, "role": user.role}}


def _parse(value: str | None):
    if not value:
        return None
    try:
        # Naive UTC: SQLite and PostgreSQL then compare the same way.
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)  # noqa: FURB162
    except ValueError:
        return None


def bearer_user(request: Request, authorization: str = Header("")) -> User:
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="A token is required.")
    with request.app.state.Session() as db:
        device = db.query(Device).filter(Device.token_hash == token_hash(token)).first()
        if device is None or device.expires_at < utcnow():
            raise HTTPException(status_code=401, detail="That token is not valid.")
        user = db.get(User, device.user_id)
        if user is None or user.disabled:
            raise HTTPException(status_code=401, detail="That account is not available.")
        device.last_seen_at = utcnow()
        db.commit()
    return user


@router.post("/auth/student")
def student_login(request: Request, body: StudentLogin):
    with request.app.state.Session() as db:
        user = (db.query(User)
                .filter(User.username == body.username.strip().lower(),
                        User.role == "student").first())
    if user is None or user.disabled:
        raise HTTPException(status_code=404, detail="That username was not found.")
    return _issue(request, user)


@router.post("/auth/staff")
def staff_login(request: Request, body: StaffLogin):
    with request.app.state.Session() as db:
        user = (db.query(User)
                .filter(User.username == body.username.strip().lower(),
                        User.role.in_(("teacher", "admin"))).first())
    if user is None or user.disabled or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="That username and password do not match.")
    return _issue(request, user)


@router.get("/me")
def me(user: User = Depends(bearer_user)):  # noqa: B008
    return {"id": user.id, "username": user.username,
            "display_name": user.display_name, "role": user.role}


def _course_path() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "content" / "course.yaml"
        if candidate.exists():
            return candidate
    return None


@router.get("/course")
def course(user: User = Depends(bearer_user)):  # noqa: B008
    path = _course_path()
    if path is None:
        raise HTTPException(status_code=404, detail="The course is not installed.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    lessons = []
    for entry in data.get("lessons", []):
        lesson_path = path.parent / entry if isinstance(entry, str) else None
        if lesson_path and lesson_path.exists():
            lesson = yaml.safe_load(lesson_path.read_text(encoding="utf-8")) or {}
            lessons.append({"id": lesson.get("id"), "ordinal": lesson.get("ordinal"),
                            "title": lesson.get("title"), "unit": lesson.get("unit")})
    return {"version": data.get("version", ""), "lessons": lessons}


@router.post("/attempts")
def upload(request: Request, attempts: list[AttemptIn],
           user: User = Depends(bearer_user)):  # noqa: B008
    accepted = ignored = 0
    with request.app.state.Session() as db:
        for item in attempts:
            if db.get(Attempt, item.id) is not None:
                ignored += 1
                continue
            body = item.model_dump()
            db.add(Attempt(
                id=item.id, student_id=user.id, lesson_id=item.lesson_id,
                kind=item.kind, started_at=_parse(item.started_at),
                active_seconds=item.active_seconds, characters=item.characters,
                keypresses=item.keypresses, errors=item.errors, wpm=item.wpm,
                accuracy=item.accuracy, real_accuracy=item.real_accuracy,
                stars=item.stars, body=body))
            accepted += 1
        db.commit()
    return {"accepted": accepted, "ignored": ignored}
