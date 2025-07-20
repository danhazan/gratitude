"""
Pytest configuration and fixtures for testing.
"""

import pytest
import pytest_asyncio
import asyncio
import os
import jwt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base, TEST_DATABASE_URL
from app.models import user, post, interaction
import httpx
from httpx import AsyncClient, ASGITransport

# Set testing environment
os.environ["TESTING"] = "true"

# JWT settings for testing
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Test database engine
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:iamgreatful@localhost:5432/grateful_test")
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
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

@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    from app.models.user import User
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email=f"test-{uuid.uuid4()}@example.com",
        username=f"testuser{uuid.uuid4().hex[:8]}",  # Remove hyphen
        full_name="Test User",
        bio="A test user for testing",
        is_verified=True,
        is_active=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest_asyncio.fixture
async def test_user2(db_session):
    """Create a second test user."""
    from app.models.user import User
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email=f"test2-{uuid.uuid4()}@example.com",
        username=f"testuser2{uuid.uuid4().hex[:8]}",  # Remove hyphen
        full_name="Test User 2",
        bio="A second test user for testing",
        is_verified=True,
        is_active=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest_asyncio.fixture
async def test_post(db_session, test_user):
    """Create a test post."""
    from app.models.post import Post, PostType
    import uuid
    
    post = Post(
        id=str(uuid.uuid4()),
        author_id=test_user.id,
        content="This is a test post content",
        post_type=PostType.DAILY,  # Use proper enum
        is_public=True
    )
    
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    
    return post

@pytest.fixture
def create_test_token():
    """Create a JWT token for testing."""
    def _create_token(user_id: str):
        payload = {"sub": user_id, "type": "access"}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return _create_token

@pytest.fixture
def auth_headers(create_test_token):
    """Create authentication headers for testing."""
    def _auth_headers(user_id: str):
        token = create_test_token(user_id)
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers 