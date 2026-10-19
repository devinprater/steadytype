"""Who is asking, and what may they see."""

from __future__ import annotations

from fastapi import HTTPException, Request

from .models import Class, User


def current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    with request.app.state.Session() as db:
        user = db.get(User, user_id)
    return user if user and not user.disabled else None


def require_user(request: Request) -> User:
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=303, headers={"Location": "/signin"})
    return user


def require_staff(request: Request) -> User:
    user = require_user(request)
    if user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403)
    return user


def require_class(request: Request, class_id: int) -> Class:
    user = require_staff(request)
    with request.app.state.Session() as db:
        klass = db.get(Class, class_id)
    if klass is None:
        raise HTTPException(status_code=404)
    if user.role != "admin" and klass.teacher_id != user.id:
        raise HTTPException(status_code=403)
    return klass
