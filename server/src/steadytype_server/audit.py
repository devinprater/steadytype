"""A plain record of who changed what."""

from __future__ import annotations

from .models import AuditLog


def record(db, actor, action: str, target: str = "", detail: str = "") -> None:
    db.add(AuditLog(actor_id=getattr(actor, "id", None),
                    actor_name=getattr(actor, "username", "") or "system",
                    action=action, target=target, detail=detail))
