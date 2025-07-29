import asyncio
from sqlalchemy import text
from app.core.database import get_test_engine

async def verify_schema():
    """Verify all database tables are correctly created."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        # Check all tables
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
        tables = result.fetchall()
        print("📋 All tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check users table structure
        print("\n🔍 Users table structure:")
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {col[3]}' if col[3] else ''}")
        
        # Check sequences
        print("\n🔢 Sequences:")
        result = await conn.execute(text("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'"))
        sequences = result.fetchall()
        for seq in sequences:
            print(f"  - {seq[0]}")
        
        # Check constraints
        print("\n🔒 Constraints:")
        result = await conn.execute(text("""
            SELECT constraint_name, constraint_type, table_name 
            FROM information_schema.table_constraints 
            WHERE table_schema = 'public' AND table_name = 'users'
        """))
        constraints = result.fetchall()
        for constraint in constraints:
            print(f"  - {constraint[0]}: {constraint[1]} on {constraint[2]}")

if __name__ == "__main__":
    asyncio.run(verify_schema()) 