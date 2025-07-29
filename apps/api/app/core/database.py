"""
Database configuration and base model.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:iamgreatful@localhost:5432/grateful")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:iamgreatful@localhost:5432/grateful_test")

# Create base class for declarative models
Base = declarative_base()

def get_async_engine():
    """Get async database engine."""
    return create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

def get_test_engine():
    """Get test database engine."""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

async def get_db() -> AsyncSession:
    """Get database session."""
    engine = get_async_engine()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session 