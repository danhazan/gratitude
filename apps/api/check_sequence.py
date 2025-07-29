import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine

async def check_sequence():
    """Check if the users table has a proper sequence for auto-incrementing."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Check if sequence exists
        result = await conn.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public' AND sequence_name LIKE '%users%'"))
        sequences = result.fetchall()
        print("Sequences found:", sequences)
        
        # Check table structure
        result = await conn.execute(text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id'"))
        columns = result.fetchall()
        print("ID column info:", columns)
        
        # Check if sequence is properly linked
        result = await conn.execute(text("SELECT pg_get_serial_sequence('users', 'id')"))
        sequence = result.fetchone()
        print("Linked sequence:", sequence)

if __name__ == "__main__":
    asyncio.run(check_sequence()) 