import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from datetime import datetime, timezone
import uuid

from app.main import app
from app.database import Base, get_db
from app.models import SwiftCode

# Test database configuration - adjust to your setup
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/swiftcodes_test"

# Create test engine with echo=True for SQL debugging
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=True
)

# Test session factory configuration
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop fixture for async tests"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests"""
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
    """Test application with overridden dependencies"""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield app
    
    # Clean up - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Restore original dependencies
    app.dependency_overrides.clear()

@pytest.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client fixture for tests"""
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        timeout=30.0
    ) as client:
        yield client

@pytest.fixture(scope="module")
def test_data() -> list[dict]:
    """Test data fixture with consistent snake_case naming"""
    now = datetime.now(timezone.utc)
    return [
        {
            "id": uuid.uuid4(),
            "swift_code": "BOFAUS3NXXX",
            "bank_name": "BANK OF AMERICA",
            "address": "100 NORTH TRYON STREET, CHARLOTTE NC 28255",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True,  
            "is_active": True,
            "time_zone": "America/New_York",
            "created_at": now,
            "updated_at": now
        },
        {
            "id": uuid.uuid4(),
            "swift_code": "BOFAUS3NBOS",
            "bank_name": "BANK OF AMERICA",
            "address": "100 FEDERAL STREET, BOSTON MA 02110",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": False,  
            "is_active": True,
            "time_zone": "America/New_York",
            "created_at": now,
            "updated_at": now
        }
    ]

@pytest.fixture
async def populated_db(test_data) -> AsyncGenerator[AsyncSession, None]:
    """Database pre-populated with test data"""
    async with TestingSessionLocal() as session:
        for data in test_data:
            session.add(SwiftCode(**data))
        await session.commit()
        yield session
        await session.rollback()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Clean database session for each test"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()