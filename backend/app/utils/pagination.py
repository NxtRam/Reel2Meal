import base64
import json
import uuid
from datetime import datetime, timezone


def encode_cursor(reel_id: uuid.UUID, created_at: datetime) -> str:
    """Encode a pagination cursor from reel id + created_at."""
    payload = {"id": str(reel_id), "ts": created_at.isoformat()}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> tuple[uuid.UUID, datetime] | None:
    """Decode a cursor string. Returns (reel_id, created_at) or None."""
    try:
        raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        reel_id = uuid.UUID(raw["id"])
        created_at = datetime.fromisoformat(raw["ts"])
        return reel_id, created_at
    except Exception:
        return None
