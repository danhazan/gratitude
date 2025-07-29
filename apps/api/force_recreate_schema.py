import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine, Base

async def force_recreate_schema():
    """Force drop and recreate the database schema with proper auto-increment."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ All tables dropped")
        
        # Create all tables with proper schema
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables recreated")
        
        # Verify the users table structure
        result = await conn.execute(text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id'"))
        columns = result.fetchall()
        print("ID column after recreation:", columns)
        
        # Check if sequence exists
        result = await conn.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public' AND sequence_name LIKE '%users%'"))
        sequences = result.fetchall()
        print("Sequences after recreation:", sequences)

if __name__ == "__main__":
    asyncio.run(force_recreate_schema()) 