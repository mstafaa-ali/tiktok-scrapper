import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import Base, get_db

from sqlalchemy.pool import NullPool

# Gunakan database terpisah untuk testing
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/tiktok_scraper_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)
TestSession = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    """Buat dan bersihkan database untuk setiap test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Provide test database session."""
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Provide test HTTP client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
