import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine

async def clean_test_db():
    """Clean the test database by removing all users."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Delete all users
        await conn.execute(text("DELETE FROM users"))
        print("✅ All users removed from test database")
        
        # Verify it's empty
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.fetchone()[0]
        print(f"✅ Users table now has {count} records")

if __name__ == "__main__":
    asyncio.run(clean_test_db()) 