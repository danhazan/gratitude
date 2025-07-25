"""
Database setup utilities for testing and development.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .database import Base, TEST_DATABASE_URL

async def create_test_database():
    """Create test database tables."""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables were created (PostgreSQL version)
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
    
    await engine.dispose()

async def drop_test_database():
    """Drop test database tables."""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

def setup_test_db():
    """Synchronous wrapper for creating test database."""
    asyncio.run(create_test_database())

def teardown_test_db():
    """Synchronous wrapper for dropping test database."""
    asyncio.run(drop_test_database())

if __name__ == "__main__":
    # Create test database when run directly
    setup_test_db() 