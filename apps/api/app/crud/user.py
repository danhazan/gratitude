from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.post import Post
from app.models.interaction import Follow, Like
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_profile(self, db: AsyncSession, *, user_id: str, current_user_id: Optional[str] = None) -> Optional[User]:
        """Get user profile with stats."""
        # Get user with posts count
        posts_count_query = select(func.count(Post.id)).where(Post.author_id == User.id)
        
        # Get followers count
        followers_count_query = select(func.count(Follow.id)).where(Follow.followed_id == User.id)
        
        # Get following count
        following_count_query = select(func.count(Follow.id)).where(Follow.follower_id == User.id)
        
        # Check if current user is following this user
        is_following_query = None
        if current_user_id:
            is_following_query = select(func.count(Follow.id)).where(
                Follow.follower_id == current_user_id,
                Follow.followed_id == User.id
            )
        
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            # Get counts
            posts_count = await db.execute(posts_count_query)
            user.posts_count = posts_count.scalar()
            
            followers_count = await db.execute(followers_count_query)
            user.followers_count = followers_count.scalar()
            
            following_count = await db.execute(following_count_query)
            user.following_count = following_count.scalar()
            
            # Check if following
            if current_user_id:
                is_following = await db.execute(is_following_query)
                user.is_following = is_following.scalar() > 0
        
        return user

    async def search_users(self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Search users by username or full name."""
        search_query = f"%{query}%"
        result = await db.execute(
            select(User)
            .where(
                (User.username.ilike(search_query)) |
                (User.full_name.ilike(search_query))
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_followers(self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Get user's followers."""
        result = await db.execute(
            select(User)
            .join(Follow, User.id == Follow.follower_id)
            .where(Follow.followed_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_following(self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Get users that the user is following."""
        result = await db.execute(
            select(User)
            .join(Follow, User.id == Follow.followed_id)
            .where(Follow.follower_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def is_following(self, db: AsyncSession, *, follower_id: str, followed_id: str) -> bool:
        """Check if one user is following another."""
        result = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        )
        return result.scalar_one_or_none() is not None

user = CRUDUser(User) 