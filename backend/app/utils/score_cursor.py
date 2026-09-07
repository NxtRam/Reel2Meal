"""
Score-based keyset pagination cursor utilities.

Cursor format: base64url( JSON{ "score": int, "id": str(UUID) } )

Using (score, id) instead of (timestamp, id) keeps the feed stable
even when scores change between page requests.
"""

import base64
import json
import uuid


def encode_score_cursor(score: int, reel_id: uuid.UUID) -> str:
    payload = {"score": score, "id": str(reel_id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_score_cursor(cursor: str) -> tuple[int, uuid.UUID] | None:
    try:
        raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return int(raw["score"]), uuid.UUID(raw["id"])
    except Exception:
        return None
