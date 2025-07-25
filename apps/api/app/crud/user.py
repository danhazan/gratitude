from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, username=user_in.username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user 