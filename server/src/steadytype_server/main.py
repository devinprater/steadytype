"""Application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import Settings
from .db import Base, make_engine, make_session


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
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
