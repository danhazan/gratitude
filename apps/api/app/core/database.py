from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import MetaData, event
import os
from typing import AsyncGenerator

# Database URL - use PostgreSQL for development and production
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://grateful:password@localhost:5432/grateful"
)

# Base class for models, set default schema to 'public'
Base = declarative_base(metadata=MetaData(schema="public"))

# Create async engine and sessionmaker only when needed
_engine = None
_AsyncSessionLocal = None

def get_async_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # Set to False in production
            pool_pre_ping=True,
            pool_recycle=300,
        )
        # Ensure search_path is set to public for every connection
        @event.listens_for(_engine.sync_engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute('SET search_path TO public')
            cursor.close()
    return _engine

def get_async_sessionmaker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = sessionmaker(
            get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal

# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    AsyncSessionLocal = get_async_sessionmaker()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# For testing - use PostgreSQL test database by default
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:iamgreatful@localhost:5432/grateful_test")

def get_test_engine():
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

def get_test_session():
    test_engine = get_test_engine()
    TestingSessionLocal = sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    return TestingSessionLocal() 