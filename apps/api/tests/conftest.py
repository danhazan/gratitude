"""
Pytest configuration and fixtures for testing.
"""

import pytest
import pytest_asyncio
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import httpx
from httpx import AsyncClient, ASGITransport

# Set testing environment
os.environ["TESTING"] = "true"

# Test database engine - Use PostgreSQL for testing to match production
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:iamgreatful@localhost:5432/grateful_test")

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_engine(event_loop):
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )
    yield engine
    event_loop.run_until_complete(engine.dispose())

@pytest.fixture(scope="function")
def session_factory(test_engine):
    """Create a session factory."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

@pytest_asyncio.fixture(scope="function")
async def test_db_setup(test_engine):
    """Set up test database tables."""
    from app.core.database import Base
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(session_factory, test_db_setup):
    """Create a new database session for a test."""
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture
async def async_client(db_session):
    """Create an async test client with database session."""
    from main import app
    from app.core.database import get_db
    
    # Override the database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides = {get_db: override_get_db}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_client(db_session):
    """Create a test client with database session."""
    from fastapi.testclient import TestClient
    from main import app
    from app.core.database import get_db
    
    # Override the database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides = {get_db: override_get_db}
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear() 