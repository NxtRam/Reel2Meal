from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _make_engine():
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        # SQLite dev/test mode — no connection pooling issues
        return create_async_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
            future=True,
        )
    # PostgreSQL (production/staging)
    return create_async_engine(url, echo=False, future=True)


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
