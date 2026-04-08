import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.event_log import EventLog


def log(
    db: Session,
    event_name: str,
    tenant_id: str | None = None,
    payload: dict | None = None,
) -> None:
    """Fire-and-forget event log. Never raises — logging must not break request flow."""
    try:
        entry = EventLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            event_name=event_name,
            payload_json=json.dumps(payload) if payload else None,
        )
        db.add(entry)
        db.flush()
    except Exception:
        pass  # intentionally silent
