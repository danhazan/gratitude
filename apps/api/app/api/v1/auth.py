"""
Authentication endpoints.
"""

import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, TokenData
from app.core.security import create_access_token, get_password_hash, verify_password, decode_token
import jwt

# Set up logging
logger = logging.getLogger(__name__)

# Constants
SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

router = APIRouter()
security = HTTPBearer()

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
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = TokenData(
        sub=str(db_user.id),  # Convert to string for JWT
        exp=int(expiration.timestamp())
    )
    access_token = create_access_token(token_data.model_dump())
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user."""
    db_user = await User.get_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = TokenData(
        sub=str(db_user.id),  # Convert to string for JWT
        exp=int(expiration.timestamp())
    )
    access_token = create_access_token(token_data.model_dump())
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/session")
async def get_session(
    auth: HTTPAuthorizationCredentials = Depends(security), 
    db: AsyncSession = Depends(get_db)
):
    """Get current user session."""
    try:
        logger.info(f"Received token: {auth.credentials[:20]}...")  # Log first 20 chars
        
        # Step 1: Decode token
        payload = decode_token(auth.credentials)
        logger.info(f"Token payload: {payload}")
        
        # Step 2: Create token data
        token_data = TokenData(**payload)
        logger.info(f"Token data: {token_data}")
        
        # Step 3: Get user from database (convert string ID back to int)
        user_id = int(token_data.sub)
        db_user = await User.get_by_id(db, user_id)
        logger.info(f"Found user: {db_user.email if db_user else 'None'}")
        
        if not db_user:
            logger.error("User not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username
        }
    except jwt.PyJWTError as e:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ValueError as e:
        logger.error(f"Value Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/logout")
async def logout():
    """Logout user."""
    return {"message": "Successfully logged out"} 