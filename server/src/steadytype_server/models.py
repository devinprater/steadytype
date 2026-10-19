"""Users, classes, enrollments, attempts, and devices."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base, utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(16), default="student")
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    @property
    def disabled(self) -> bool:
        return self.disabled_at is not None


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    goal_minutes: Mapped[int] = mapped_column(Integer, default=40)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    teacher: Mapped[User] = relationship()


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("class_id", "student_id", name="one_enrollment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    delivery_mode: Mapped[str] = mapped_column(String(16), default="in_person")

    student: Mapped[User] = relationship()


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(16), default="practice")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    active_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    characters: Mapped[int] = mapped_column(Integer, default=0)
    keypresses: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    wpm: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    real_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    body: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(80), default="")
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str] = mapped_column(String(120), default="")
    detail: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
