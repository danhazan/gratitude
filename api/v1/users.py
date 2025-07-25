from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user = await create_user(db, user_in)
    return {"id": user.id, "email": user.email, "username": user.username} 