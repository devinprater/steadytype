"""Application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from sqlalchemy import text as sql_text
from starlette.middleware.sessions import SessionMiddleware

from . import models  # noqa: F401 - registers every table before create_all
from .config import Settings
from .db import Base, make_engine, make_session


def _upgrade(engine) -> None:
    """Add columns that older databases do not have yet."""
    inspector = inspect(engine)
    if "classes" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("classes")}
    if "goal_minutes" not in columns:
        with engine.begin() as connection:
            connection.execute(sql_text(
                "ALTER TABLE classes ADD COLUMN goal_minutes INTEGER NOT NULL DEFAULT 40"))


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    _upgrade(engine)
    app = FastAPI(title="SteadyType")
    app.state.settings = settings
    app.state.engine = engine
    app.state.Session = make_session(engine)
    app.add_middleware(SessionMiddleware, secret_key=settings.secret,
                       same_site="lax", https_only=settings.secure_cookies)
    app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")),
              name="static")
    from .api import router as api
    from .routes_dashboard import router as dashboard
    app.include_router(dashboard)
    app.include_router(api)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    return app


def app_factory():
    """Uvicorn entry point: uvicorn --factory steadytype_server.main:app_factory"""
    return create_app()
