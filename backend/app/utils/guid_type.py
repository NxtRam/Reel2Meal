"""
Custom SQLAlchemy type for UUID columns that works with both
PostgreSQL (native UUID) and SQLite (stored as 32-char hex string).

Usage in models:
    from app.utils.guid_type import GUID
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
"""

import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    - PostgreSQL: uses the native UUID column type.
    - SQLite (and others): stores as a 32-char hex string (no dashes).
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return str(value)
        if isinstance(value, uuid.UUID):
            return value.hex
        return uuid.UUID(str(value)).hex

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(str(value))
