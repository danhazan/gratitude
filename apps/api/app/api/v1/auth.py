from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user, get_user_by_email, get_user_by_username

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, data.email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    to_encode = {"sub": db_user.id, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/session")
async def get_session(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    raise HTTPException(status_code=501, detail="User lookup not implemented")
    if not db_user or not db_user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return {"id": db_user.id, "email": db_user.email, "username": db_user.username}

# Logout is a no-op for JWT, but endpoint provided for completeness
@router.post("/logout")
async def logout():
    return {"message": "Logged out (client should delete token)"}

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user = await create_user(db, user_in)
    return user 