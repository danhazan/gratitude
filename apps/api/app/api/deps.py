from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import jwt
import os

# Security scheme
security = HTTPBearer()

# JWT secret key
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Get current user from JWT token."""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    # db_user = await user.get(db, id=user_id)
    raise HTTPException(status_code=501, detail="User lookup not implemented")

async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Optional current user (for endpoints that work with or without authentication)
async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise None."""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None  # User lookup not implemented 