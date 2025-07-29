"""Drop and recreate the database schema."""

import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine, Base

async def recreate_schema():
    """Drop and recreate the database schema."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(recreate_schema()) 