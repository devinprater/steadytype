"""Server settings from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./steadytype.db"
    secret: str = "change-me-before-anyone-uses-this"
    school_name: str = "SteadyType"
    timezone: str = "America/Chicago"
    secure_cookies: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            database_url=os.environ.get("STEADYTYPE_DATABASE_URL", cls.database_url),
            secret=os.environ.get("STEADYTYPE_SECRET", cls.secret),
            school_name=os.environ.get("STEADYTYPE_SCHOOL_NAME", cls.school_name),
            timezone=os.environ.get("STEADYTYPE_TIMEZONE", cls.timezone),
            secure_cookies=os.environ.get("STEADYTYPE_SECURE_COOKIES", "0") == "1",
        )
