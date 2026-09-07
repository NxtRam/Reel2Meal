"""
conftest.py
-----------
Uses an in-memory SQLite database (via aiosqlite + StaticPool).

Tables are created eagerly at import time via asyncio.run() on the async
engine — the ONLY engine that the app's overridden get_db uses.

`TestSession` is exported so test files can seed data directly.
"""

import asyncio

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.deps import get_db

# ---------------------------------------------------------------------------
# Single shared in-memory SQLite connection (StaticPool)
# ---------------------------------------------------------------------------
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Create tables ONCE at import time — guaranteed before any fixture runs
# ---------------------------------------------------------------------------

async def _bootstrap():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(_bootstrap())

# ---------------------------------------------------------------------------
# Dependency override — app uses the test engine
# ---------------------------------------------------------------------------

async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

