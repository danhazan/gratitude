"""
Test factories for creating test data.
"""

import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
from app.models.user import User

class UserFactory:
    """Factory for creating test users."""
    
    @staticmethod
    def create_user(db_session, **kwargs) -> User:
        """Create a test user with default or overridden values."""
        unique_id = uuid.uuid4().hex[:8]
        
        # Default values
        defaults = {
            "email": f"test-{unique_id}@example.com",
            "username": f"testuser{unique_id}",
            "hashed_password": bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        
        # Override defaults with any provided values
        user_data = {**defaults, **kwargs}
        user = User(**user_data)
        db_session.add(user)
        return user

    @staticmethod
    def create_auth_token(user_id: str, secret_key: str = "your-secret-key-here") -> str:
        """Create a JWT token for testing."""
        import jwt
        
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60 * 24 * 7)  # 7 days
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")

    @staticmethod
    def get_auth_headers(user_id: str) -> dict:
        """Get authentication headers for testing."""
        token = UserFactory.create_auth_token(user_id)
        return {"Authorization": f"Bearer {token}"}