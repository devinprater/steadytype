# SteadyType

A speech-first typing tutor for blind and low-vision adults, with a staff dashboard.

- `engine/` — the teaching engine. Pure Python, tested without a keyboard or a screen reader.
- `client/` — the wxPython desktop client. Run `python -m steadytype_client` from `client/`.
- `server/` — the FastAPI server and staff dashboard. Plan 3.
- `server/` — the staff dashboard and the API. See `deploy/README.md`.
- `deploy/` — Docker Compose, Caddy, and the nightly backup.
- `content/` — the built-in course.

Design: `docs/superpowers/specs/2026-10-19-steadytype-design.md`
Plans: `docs/superpowers/plans/`

License: GPL-3.0-or-later.
