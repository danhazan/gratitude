"""
Pytest configuration and fixtures for testing.
"""

import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, TEST_DATABASE_URL
from app.models import user, post, interaction

# Test database engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

# Test session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Set up test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Create a new database session for a test."""
    # Create tables for this test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture
async def test_client(db_session):
    """Create a test client with database session."""
    from fastapi.testclient import TestClient
    from main import app
    
    # Override the database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides = {get_db: override_get_db}
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

# Import the get_db function for dependency override
from app.core.database import get_db 