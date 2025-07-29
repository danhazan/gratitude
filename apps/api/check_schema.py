import asyncio
from app.core.database import get_test_engine, Base
from app.models.user import User

async def create_schema():
    """Create the database schema for testing."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database schema created successfully!")

if __name__ == "__main__":
    asyncio.run(create_schema()) 