import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")

# Convert postgres:// to postgresql+asyncpg:// for SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

kwargs = {}
if "sqlite" not in DATABASE_URL:
    kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
    }

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
    **kwargs
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def init_db():
    """Create tables (dev only — use Alembic in production)."""
    async with engine.begin() as conn:
        from app.db_models import User, Workspace, WorkspaceMember, Blueprint, BlueprintVersion, SimulationRun, CloudPricing
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")

async def close_db():
    """Dispose the engine connection pool."""
    await engine.dispose()
    logger.info("Database connection pool closed")
