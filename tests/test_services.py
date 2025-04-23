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

# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/swiftcodes_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
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
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

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

@pytest.fixture(scope="module")
async def test_app():
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
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        timeout=30.0
    ) as client:
        yield client

@pytest.fixture(scope="module")
def test_data() -> list[dict]:
    """Test data using boolean is_headquarter instead of SwiftCodeType"""
    now = datetime.now(timezone.utc)
    return [
        {
            "id": uuid.uuid4(),
            "swift_code": "BOFAUS3NXXX",
            "bank_name": "BANK OF AMERICA",
            "address": "100 NORTH TRYON STREET, CHARLOTTE NC 28255",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": True,  # Headquarters
            "is_active": True,
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
            "is_headquarter": False,  # Branch
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": uuid.uuid4(),
            "swift_code": "BOFAUS3NSF",
            "bank_name": "BANK OF AMERICA",
            "address": "1 MARKET STREET, SAN FRANCISCO CA 94105",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarter": False,  # Another branch
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    ]

@pytest.fixture
async def populated_db(test_data) -> AsyncGenerator[AsyncSession, None]:
    """DB with test data using boolean is_headquarter"""
    async with TestingSessionLocal() as session:
        for data in test_data:
            # Skip adding headquarter_id if the model doesn't support it
            swift_code_data = {
                k: v for k, v in data.items()
                if k != 'headquarter_id'
            }
            session.add(SwiftCode(**swift_code_data))
        await session.commit()
        yield session
        await session.rollback()

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