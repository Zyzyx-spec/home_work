import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from datetime import datetime, timezone

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

# Override FastAPI dependency
async def OverrideGetDb() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest_asyncio.fixture
async def DbSession() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest_asyncio.fixture(scope="module")
async def TestApp() -> AsyncGenerator:
    app.dependency_overrides[get_db] = OverrideGetDb

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield app

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def Client(TestApp) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=TestApp, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def PopulatedDb(DbSession: AsyncSession, TestData: list[dict]) -> AsyncGenerator[AsyncSession, None]:
    try:
        for data in TestData:
            valid_data = {k: v for k, v in data.items() if hasattr(SwiftCode, k)}
            DbSession.add(SwiftCode(**valid_data))
        await DbSession.commit()
        yield DbSession
    except Exception:
        await DbSession.rollback()
        raise
    finally:
        await DbSession.close()

@pytest.fixture
def TestData() -> list[dict]:
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