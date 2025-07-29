import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine, Base
from app.models.user import User

async def recreate_test_schema():
    """Recreate the test database schema with full_name column."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Drop the users table specifically
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        print("✅ Users table dropped from test database")
        
        # Create the users table with proper SQL including full_name
        create_sql = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            username VARCHAR NOT NULL UNIQUE,
            full_name VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        )
        """
        await conn.execute(text(create_sql))
        print("✅ Users table created in test database with full_name column")
        
        # Verify the structure
        result = await conn.execute(text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"))
        columns = result.fetchall()
        print("Test database users table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {col[3]}' if col[3] else ''}")

if __name__ == "__main__":
    asyncio.run(recreate_test_schema()) 