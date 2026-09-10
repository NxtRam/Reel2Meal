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
    # pool_pre_ping: test connection before use (handles Neon idle disconnects)
    # pool_recycle: recycle connections every 5 min before Neon closes them
    # pool_size / max_overflow: keep connections lean on free tier
    return create_async_engine(
        url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,       # recycle every 5 minutes
        pool_size=5,
        max_overflow=10,
    )


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
