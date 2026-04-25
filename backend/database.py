# backend/database.py
# Database connection layer for SmartFlow.
# Uses SQLAlchemy async engine — works with SQLite (dev) and PostgreSQL (prod/AWS)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from backend.config import settings

# ── Engine ───────────────────────────────────────────────────
# create_async_engine = non-blocking DB calls (perfect for FastAPI)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # Logs all SQL queries in debug mode
    future=True,                # Use SQLAlchemy 2.0 style
)

# ── Session Factory ──────────────────────────────────────────
# Each API request gets its own session (opened & closed automatically)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Keep objects usable after commit
    autocommit=False,
    autoflush=False,
)

# ── Base Class ───────────────────────────────────────────────
# All database models (tables) inherit from this
class Base(DeclarativeBase):
    pass

# ── Dependency ───────────────────────────────────────────────
# FastAPI injects this into every route that needs DB access
async def get_db():
    """
    Yields a database session per request.
    Automatically closes session when request is done.
    Usage in routes: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ── Table Creator ─────────────────────────────────────────────
# Called once at app startup to create all tables
async def create_tables():
    """Creates all tables defined in models if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")

# ── Health Check ─────────────────────────────────────────────
async def check_db_connection():
    """Tests database connectivity — used in /health endpoint."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": settings.DATABASE_URL}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ── Quick test when run directly ─────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        print("Testing database connection...")
        result = await check_db_connection()
        print(f"DB Status: {result['status']}")
        await create_tables()
        print("Database layer ready!")

    asyncio.run(test())