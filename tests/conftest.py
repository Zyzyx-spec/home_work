import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator, Any
import logging

from app.main import app
from app.database import Base, get_db
from app.models import SwiftCode
from app.schemas import SwiftCodeType

# Configure test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_swift_codes.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override dependency for database session in tests"""
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
async def test_app():
    """Fixture for creating test application with overridden dependencies"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield app
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    app.dependency_overrides.clear()

@pytest.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Fixture for creating test HTTP client"""
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        timeout=30.0
    ) as client:
        yield client

@pytest.fixture(scope="module")
def test_data() -> list[dict]:
    """Fixture providing test data for SWIFT codes"""
    return [
        {
            "swift_code": "BOFAUS3NXXX",
            "bank_name": "BANK OF AMERICA",
            "address": "100 NORTH TRYON STREET, CHARLOTTE NC 28255",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "code_type": SwiftCodeType.HEADQUARTER,
            "is_active": True
        },
        {
            "swift_code": "BOFAUS3NBOS",
            "bank_name": "BANK OF AMERICA",
            "address": "100 FEDERAL STREET, BOSTON MA 02110",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "code_type": SwiftCodeType.BRANCH,
            "is_active": True
        }
    ]

@pytest.fixture
async def populated_db(test_data) -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing database with test data"""
    async with TestingSessionLocal() as session:
        for data in test_data:
            session.add(SwiftCode(**data))
        await session.commit()
        yield session
        await session.rollback()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing clean database session for each test"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()