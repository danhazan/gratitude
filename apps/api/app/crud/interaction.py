from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.interaction import Like, Comment, Follow
from app.schemas.interaction import LikeCreate, CommentCreate, CommentUpdate, FollowCreate

class CRUDLike(CRUDBase[Like, LikeCreate, LikeCreate]):
    async def create_like(self, db: AsyncSession, *, user_id: str, post_id: str) -> Optional[Like]:
        """Create a like if it doesn't exist."""
        # Check if like already exists
        existing_like = await db.execute(
            select(Like).where(
                Like.user_id == user_id,
                Like.post_id == post_id
            )
        )
        if existing_like.scalar_one_or_none():
            return None  # Like already exists
        
        # Create new like
        like_data = LikeCreate(post_id=post_id)
        return await self.create(db, obj_in=like_data)

    async def remove_like(self, db: AsyncSession, *, user_id: str, post_id: str) -> bool:
        """Remove a like."""
        like = await db.execute(
            select(Like).where(
                Like.user_id == user_id,
                Like.post_id == post_id
            )
        )
        like = like.scalar_one_or_none()
        if like:
            await db.delete(like)
            await db.commit()
            return True
        return False

    async def get_post_likes(self, db: AsyncSession, *, post_id: str, skip: int = 0, limit: int = 20) -> List[Like]:
        """Get all likes for a post."""
        result = await db.execute(
            select(Like)
            .options(selectinload(Like.user))
            .where(Like.post_id == post_id)
            .order_by(desc(Like.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    async def get_post_comments(
        self, 
        db: AsyncSession, 
        *, 
        post_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Comment]:
        """Get comments for a post with author information."""
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.post_id == post_id)
            .where(Comment.parent_id.is_(None))  # Only top-level comments
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        comments = result.scalars().all()
        
        # Add replies count for each comment
        for comment in comments:
            replies_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.parent_id == comment.id)
            )
            comment.replies_count = replies_count.scalar()
        
        return comments

    async def get_comment_replies(
        self, 
        db: AsyncSession, 
        *, 
        comment_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Comment]:
        """Get replies to a comment."""
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.parent_id == comment_id)
            .order_by(Comment.created_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_comment(
        self, 
        db: AsyncSession, 
        *, 
        author_id: str, 
        post_id: str, 
        content: str, 
        parent_id: Optional[str] = None
    ) -> Comment:
        """Create a new comment."""
        comment_data = CommentCreate(
            post_id=post_id,
            content=content,
            parent_id=parent_id
        )
        comment = await self.create(db, obj_in=comment_data)
        comment.author_id = author_id
        await db.commit()
        await db.refresh(comment)
        return comment

class CRUDFollow(CRUDBase[Follow, FollowCreate, FollowCreate]):
    async def create_follow(self, db: AsyncSession, *, follower_id: str, followed_id: str) -> Optional[Follow]:
        """Create a follow relationship if it doesn't exist."""
        # Check if follow already exists
        existing_follow = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        )
        if existing_follow.scalar_one_or_none():
            return None  # Follow already exists
        
        # Create new follow
        follow_data = FollowCreate(followed_id=followed_id)
        follow = await self.create(db, obj_in=follow_data)
        follow.follower_id = follower_id
        await db.commit()
        await db.refresh(follow)
        return follow

    async def remove_follow(self, db: AsyncSession, *, follower_id: str, followed_id: str) -> bool:
        """Remove a follow relationship."""
        follow = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        )
        follow = follow.scalar_one_or_none()
        if follow:
            await db.delete(follow)
            await db.commit()
            return True
        return False

    async def get_followers(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Follow]:
        """Get followers of a user."""
        result = await db.execute(
            select(Follow)
            .options(selectinload(Follow.follower))
            .where(Follow.followed_id == user_id)
            .order_by(desc(Follow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_following(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Follow]:
        """Get users that a user is following."""
        result = await db.execute(
            select(Follow)
            .options(selectinload(Follow.followed))
            .where(Follow.follower_id == user_id)
            .order_by(desc(Follow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Create instances
like = CRUDLike(Like)
comment = CRUDComment(Comment)
follow = CRUDFollow(Follow) 