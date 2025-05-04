from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# New SQLAlchemy 2.0 base class
class Base(DeclarativeBase):
    pass

# Database configuration - now using asyncpg for PostgreSQL (recommended for production)
DATABASE_URL = "postgresql+asyncpg://user:password@db/swiftcodes"

# Engine configuration with new 2.0 parameters
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # N
    pool_recycle=3600    # Recycle connections after 1 hour
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    future=True  # 
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions
    Uses new 2.0 async context manager pattern
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database with new 2.0 metadata API"""
    async with engine.begin() as conn:
        # New metadata API in 2.0
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created using SQLAlchemy 2.0")