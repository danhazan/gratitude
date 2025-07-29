import asyncio
import httpx
from app.core.database import get_test_engine
from sqlalchemy import text

async def debug_signup():
    """Debug the signup endpoint to see what error is returned."""
    # First, let's check what users exist in the test database
    engine = get_test_engine()
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, email, username FROM users"))
        users = result.fetchall()
        print("Existing users in test database:")
        for user in users:
            print(f"  - ID: {user[0]}, Email: {user[1]}, Username: {user[2]}")
    
    # Now test the signup endpoint
    async with httpx.AsyncClient(base_url="http://testserver") as client:
        test_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/v1/auth/signup", json=test_data)
        print(f"\nSignup response status: {response.status_code}")
        print(f"Signup response body: {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_signup()) 