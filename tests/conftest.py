import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator, Iterator
from datetime import datetime, timezone
from fastapi import HTTPException

from app.main import app
from app.database import Base, get_db
from app.models import SwiftCode

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/swiftcodes_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Clean DB session"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture(scope="module")
async def test_app() -> AsyncGenerator:
    """Test app with overridden dependencies"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield app
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    app.dependency_overrides.clear()

@pytest.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_data() -> list[dict]:
    """Test data"""
    now = datetime.now(timezone.utc)
    return [
        {
            "swift_code": "BOFAUS3NXXX",
            "bank_name": "BANK OF AMERICA",
            "address": "100 NORTH TRYON STREET, CHARLOTTE NC 28255",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "swift_code": "BOFAUS3NBOS",
            "bank_name": "BANK OF AMERICA",
            "address": "100 FEDERAL STREET, BOSTON MA 02110",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    ]

@pytest.fixture
async def populated_db(db_session: AsyncSession, test_data: list[dict]) -> AsyncSession:
    """DB with test data"""
    for data in test_data:
        valid_data = {k: v for k, v in data.items() if hasattr(SwiftCode, k)}
        db_session.add(SwiftCode(**valid_data))
    await db_session.commit()
    return db_session

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()