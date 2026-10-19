"""Staff pages: sign in, classes, scoreboard, student detail, CSV."""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .audit import record
from .auth import current_user, require_class, require_staff
from .db import utcnow
from .models import Attempt, AuditLog, Class, Enrollment, User
from .security import check_csrf, csrf_token, verify_password
from .signin_rules import SignInError, check_username

router = APIRouter()

TEMPLATES = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
    autoescape=select_autoescape(["html"]),
)


def render(request: Request, template: str, **context) -> HTMLResponse:
    user = current_user(request)
    body = TEMPLATES.get_template(template).render(
        user=user, school=request.app.state.settings.school_name,
        csrf=csrf_token(request.session), **context)
    return HTMLResponse(body)


@router.get("/")
def home(request: Request):
    return RedirectResponse("/classes" if current_user(request) else "/signin", status_code=303)


@router.get("/signin")
def signin_form(request: Request):
    if current_user(request):
        return RedirectResponse("/classes", status_code=303)
    return render(request, "signin.html", error=None)


@router.post("/signin")
def signin(request: Request, username: str = Form(""), password: str = Form(""),
           csrf: str = Form("")):
    if not check_csrf(request.session, csrf):
        return render(request, "signin.html", error="The form expired. Try again.")
    with request.app.state.Session() as db:
        user = db.query(User).filter(User.username == username.strip().lower()).first()
        ok = (user is not None and user.role in ("teacher", "admin")
              and not user.disabled and verify_password(password, user.password_hash))
        if ok:
            request.session["user_id"] = user.id
    if not ok:
        return render(request, "signin.html", error="That username and password do not match.")
    return RedirectResponse("/classes", status_code=303)


@router.post("/signout")
def signout(request: Request, csrf: str = Form("")):
    if check_csrf(request.session, csrf):
        request.session.clear()
    return RedirectResponse("/signin", status_code=303)


def today_start(request: Request):
    zone = ZoneInfo(request.app.state.settings.timezone)
    local = datetime.now(zone).replace(hour=0, minute=0, second=0, microsecond=0)
    return local.astimezone(UTC).replace(tzinfo=None)


def class_rows(request: Request, klass: Class) -> list[dict]:
    week_ago = utcnow() - timedelta(days=7)
    day_start = today_start(request)
    with request.app.state.Session() as db:
        students = (db.query(User).join(Enrollment, Enrollment.student_id == User.id)
                    .filter(Enrollment.class_id == klass.id).order_by(User.display_name).all())
        rows = []
        for student in students:
            attempts = (db.query(Attempt).filter(Attempt.student_id == student.id)
                        .order_by(Attempt.started_at.desc()).all())
            practice = [a for a in attempts if a.kind in ("practice", "race")]
            recent = [a for a in practice if a.started_at and a.started_at >= week_ago]
            today = [a for a in practice if a.started_at and a.started_at >= day_start]
            rows.append({
                "student": student,
                "lessons": len({a.lesson_id for a in practice}),
                "accuracy": (sum(a.accuracy for a in practice) / len(practice)) if practice else 0,
                "wpm": (sum(a.wpm for a in practice) / len(practice)) if practice else 0,
                "minutes": sum(a.active_seconds for a in recent) / 60,
                "today_minutes": sum(a.active_seconds for a in today) / 60,
                "last": attempts[0].started_at if attempts else None,
            })
        return rows


@router.get("/classes")
def classes(request: Request):
    user = require_staff(request)
    with request.app.state.Session() as db:
        query = db.query(Class).order_by(Class.name)
        if user.role != "admin":
            query = query.filter(Class.teacher_id == user.id)
        items = query.all()
    return render(request, "classes.html", classes=items)


@router.get("/classes/new")
def new_class_form(request: Request):
    require_staff(request)
    return render(request, "new_class.html", error=None)


@router.post("/classes/new")
def new_class(request: Request, name: str = Form(""), csrf: str = Form("")):
    user = require_staff(request)
    if not check_csrf(request.session, csrf):
        return render(request, "new_class.html", error="The form expired. Try again.")
    if not name.strip():
        return render(request, "new_class.html", error="Give the class a name.")
    with request.app.state.Session() as db:
        klass = Class(name=name.strip(), teacher_id=user.id)
        db.add(klass)
        db.flush()
        record(db, user, "class.create", klass.name)
        db.commit()
    return RedirectResponse("/classes", status_code=303)


@router.post("/classes/{class_id}/students")
def add_student(request: Request, class_id: int, username: str = Form(""),
                display_name: str = Form(""), csrf: str = Form("")):
    klass = require_class(request, class_id)
    if not check_csrf(request.session, csrf):
        return RedirectResponse(f"/classes/{class_id}", status_code=303)
    username = username.strip().lower()
    try:
        check_username(username)
    except SignInError:
        return RedirectResponse(f"/classes/{class_id}?error=username", status_code=303)
    with request.app.state.Session() as db:
        student = db.query(User).filter(User.username == username).first()
        if student is None:
            student = User(username=username, display_name=display_name.strip() or username,
                           role="student")
            db.add(student)
            db.commit()
        if db.query(Enrollment).filter(Enrollment.class_id == klass.id,
                                       Enrollment.student_id == student.id).first() is None:
            db.add(Enrollment(class_id=klass.id, student_id=student.id))
            record(db, current_user(request), "student.add", student.username, klass.name)
            db.commit()
    return RedirectResponse(f"/classes/{class_id}", status_code=303)


@router.get("/classes/{class_id}")
def class_page(request: Request, class_id: int):
    klass = require_class(request, class_id)
    return render(request, "class.html", klass=klass, rows=class_rows(request, klass))


@router.get("/classes/{class_id}/students/{student_id}")
def student_page(request: Request, class_id: int, student_id: int):
    klass = require_class(request, class_id)
    with request.app.state.Session() as db:
        student = db.get(User, student_id)
        attempts = (db.query(Attempt).filter(Attempt.student_id == student_id)
                    .order_by(Attempt.started_at.desc()).limit(50).all())
    if student is None:
        return HTMLResponse("Student not found", status_code=404)
    keys: dict[str, dict] = {}
    for attempt in attempts:
        for stat in (attempt.body or {}).get("key_stats", []):
            entry = keys.setdefault(stat["key"], {"presses": 0, "errors": 0})
            entry["presses"] += stat.get("presses", 0)
            entry["errors"] += stat.get("errors", 0)
    weakest = sorted(keys.items(), key=lambda item: item[1]["errors"], reverse=True)[:10]
    return render(request, "student.html", klass=klass, student=student,
                  attempts=attempts, weakest=weakest)


@router.get("/classes/{class_id}/settings")
def class_settings(request: Request, class_id: int):
    klass = require_class(request, class_id)
    return render(request, "settings.html", klass=klass, saved=False)


@router.post("/classes/{class_id}/settings")
def save_class_settings(request: Request, class_id: int, goal_minutes: str = Form("40"),
                        csrf: str = Form("")):
    klass = require_class(request, class_id)
    if not check_csrf(request.session, csrf):
        return render(request, "settings.html", klass=klass, saved=False)
    try:
        goal = max(0, min(300, int(goal_minutes)))
    except ValueError:
        goal = 40
    with request.app.state.Session() as db:
        row = db.get(Class, klass.id)
        row.goal_minutes = goal
        record(db, require_staff(request), "class.goal", klass.name,
               "no daily goal" if goal == 0 else f"{goal} minutes a day")
        db.commit()
    klass.goal_minutes = goal
    return render(request, "settings.html", klass=klass, saved=True)


@router.get("/classes/{class_id}/certification")
def certification(request: Request, class_id: int):
    klass = require_class(request, class_id)
    with request.app.state.Session() as db:
        students = (db.query(User).join(Enrollment, Enrollment.student_id == User.id)
                    .filter(Enrollment.class_id == klass.id).order_by(User.display_name).all())
        rows = []
        for student in students:
            tests = (db.query(Attempt)
                     .filter(Attempt.student_id == student.id,
                             Attempt.kind == "timed_test").all())
            best = max(tests, key=lambda a: (a.wpm, -a.errors), default=None)
            rows.append({
                "student": student,
                "wpm": best.wpm if best else None,
                "errors": best.errors if best else None,
                "passed": bool(best and best.wpm >= 50 and best.errors <= 10),
            })
    return render(request, "certification.html", klass=klass, rows=rows)


@router.get("/classes/{class_id}/audit")
def audit(request: Request, class_id: int):
    klass = require_class(request, class_id)
    with request.app.state.Session() as db:
        entries = (db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all())
    return render(request, "audit.html", klass=klass, entries=entries)


@router.get("/classes/{class_id}/export.csv")
def export(request: Request, class_id: int):
    klass = require_class(request, class_id)
    rows = class_rows(request, klass)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["username", "display_name", "lessons", "accuracy", "wpm",
                     "minutes_this_week", "last_active"])
    for row in rows:
        writer.writerow([row["student"].username, row["student"].display_name,
                         row["lessons"], f"{row['accuracy']:.1f}", f"{row['wpm']:.1f}",
                         f"{row['minutes']:.0f}",
                         row["last"].isoformat() if row["last"] else ""])
    return Response(buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=class.csv"})
