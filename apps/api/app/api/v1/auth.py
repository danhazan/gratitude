"""
Authentication endpoints.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import create_access_token, get_password_hash, verify_password
import jwt

# Constants
SECRET_KEY = "your-secret-key-here"  # Should be in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create new user."""
    # Check if user exists
    db_user = await User.get_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Create access token
    to_encode = {
        "sub": db_user.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = create_access_token(to_encode)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user."""
    db_user = await User.get_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    to_encode = {
        "sub": db_user.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = create_access_token(to_encode)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/session")
async def get_session(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Get current user session."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    db_user = await User.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return db_user

@router.post("/logout")
async def logout():
    """Logout user."""
    return {"message": "Successfully logged out"} 