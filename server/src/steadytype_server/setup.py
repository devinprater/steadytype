"""Create the first administrator. Never prints or logs the password."""

from __future__ import annotations

import argparse
import getpass

from .config import Settings
from .db import Base, make_engine, make_session
from .models import User
from .security import hash_password


def create_admin(settings: Settings, username: str, password: str,
                 display_name: str = "Administrator") -> int:
    if len(password) < 10:
        raise SystemExit("Use a password of at least ten characters.")
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    Session = make_session(engine)
    with Session() as db:
        existing = db.query(User).filter(User.username == username.lower()).first()
        if existing is not None:
            raise SystemExit(f"{username} already exists.")
        admin = User(username=username.lower(), display_name=display_name,
                     role="admin", password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        return admin.id


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Create a SteadyType administrator.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", help="omit to be prompted")
    parser.add_argument("--display-name", default="Administrator")
    args = parser.parse_args(argv)
    password = args.password or getpass.getpass("New administrator password: ")
    create_admin(Settings.from_env(), args.username, password, args.display_name)
    print(f"Created administrator {args.username.lower()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
