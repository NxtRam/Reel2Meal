from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, reels, feed, menu, users, orders, payments, comments, media


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from app.utils.migrate_db import run_migration
    await run_migration()
    yield


app = FastAPI(
    title="Reel2Meal API",
    description="Food reels platform — Phase 1",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,   # Prevents 307 redirects that strip Authorization header
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(reels.router, prefix=API_PREFIX)
app.include_router(comments.router, prefix=API_PREFIX)
app.include_router(feed.router, prefix=API_PREFIX)
app.include_router(menu.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(orders.router, prefix=API_PREFIX)
app.include_router(payments.router, prefix=API_PREFIX)
app.include_router(media.router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "reel2meal-api"}
