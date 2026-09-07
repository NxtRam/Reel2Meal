import asyncio
from sqlalchemy import text
from app.database import engine

async def run_migration():
    print("Running database migrations...")
    async with engine.begin() as conn:
        dialect = conn.dialect.name
        print(f"Database dialect: {dialect}")
        
        if dialect == "sqlite":
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            if "role" not in columns:
                print("Adding role column to users table (SQLite)...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
            if "restaurant_id" not in columns:
                print("Adding restaurant_id column to users table (SQLite)...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN restaurant_id CHAR(36) REFERENCES restaurants(id) ON DELETE SET NULL"))
        else:
            print("Adding columns to users table (PostgreSQL)...")
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS restaurant_id UUID REFERENCES restaurants(id) ON DELETE SET NULL"))
            
    print("Database migrations completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
