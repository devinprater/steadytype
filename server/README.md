# SteadyType server

FastAPI, SQLAlchemy, server-rendered Jinja2. SQLite for tests, PostgreSQL in
production. See `../deploy/README.md` for the Ubuntu and Caddy setup.

## Pages

- `/signin` — staff only.
- `/classes` — the classes you teach.
- `/classes/{id}` — scoreboard and CSV.
- `/classes/{id}/students/{student}` — attempts and weak keys.
- `/healthz`.

## API

- `POST /api/v1/auth/student` with `{"username"}`.
- `POST /api/v1/auth/staff` with `{"username", "password"}`.
- `GET /api/v1/me`, `GET /api/v1/course`.
- `POST /api/v1/attempts` with a batched list. Idempotent by attempt id.

## Tests

```
PYTHONPATH=src ../.venv/Scripts/python.exe -m pytest tests -q
```
