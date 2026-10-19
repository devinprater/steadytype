"""Database engine, session factory, and the declarative base."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def make_session(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


def utcnow() -> datetime:
    """Naive UTC, so SQLite and PostgreSQL compare the same way."""
    return datetime.now(UTC).replace(tzinfo=None)
