"""
Security utilities for authentication.
"""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

# Constants
SECRET_KEY = "your-super-secret-key-change-this-in-production"  # Should be in environment variables
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode JWT token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])