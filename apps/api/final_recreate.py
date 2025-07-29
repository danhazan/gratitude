import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine, Base
from app.models.user import User

async def final_recreate():
    """Final attempt to recreate the schema with proper auto-increment."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Drop the users table specifically
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        print("✅ Users table dropped")
        
        # Create the users table with proper SQL
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
        print("✅ Users table created with proper SERIAL")
        
        # Verify the structure
        result = await conn.execute(text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id'"))
        columns = result.fetchall()
        print("ID column after manual creation:", columns)
        
        # Check sequence
        result = await conn.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public' AND sequence_name LIKE '%users%'"))
        sequences = result.fetchall()
        print("Sequences after manual creation:", sequences)

if __name__ == "__main__":
    asyncio.run(final_recreate()) 