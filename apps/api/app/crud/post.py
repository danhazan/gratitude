from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.post import Post, PostType
from app.models.user import User
from app.models.interaction import Like, Comment, Follow
from app.schemas.post import PostCreate, PostUpdate

class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    async def get_multi_with_author(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Post]:
        """Get multiple posts with author information and interaction counts."""
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.is_public == True)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Add interaction counts
        for post in posts:
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post.id)
            )
            post.likes_count = likes_count.scalar()
            
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post.id)
            )
            post.comments_count = comments_count.scalar()
        
        return posts

    async def get_with_author(self, db: AsyncSession, *, post_id: str, current_user_id: Optional[str] = None) -> Optional[Post]:
        """Get post with author information and interaction counts."""
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.id == post_id)
        )
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if post:
            # Get likes count
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post_id)
            )
            post.likes_count = likes_count.scalar()
            
            # Get comments count
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post_id)
            )
            post.comments_count = comments_count.scalar()
            
            # Check if current user liked the post
            if current_user_id:
                is_liked = await db.execute(
                    select(Like).where(
                        Like.post_id == post_id,
                        Like.user_id == current_user_id
                    )
                )
                post.is_liked = is_liked.scalar_one_or_none() is not None
        
        return post

    async def get_user_feed(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Post]:
        """Get feed for a user (posts from followed users + their own posts)."""
        # Get posts from followed users and own posts
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(
                (Post.author_id == user_id) |
                (Post.author_id.in_(
                    select(User.id)
                    .join(Follow, User.id == Follow.followed_id)
                    .where(Follow.follower_id == user_id)
                ))
            )
            .where(Post.is_public == True)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Add interaction counts and like status
        for post in posts:
            # Likes count
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post.id)
            )
            post.likes_count = likes_count.scalar()
            
            # Comments count
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post.id)
            )
            post.comments_count = comments_count.scalar()
            
            # Check if user liked
            is_liked = await db.execute(
                select(Like).where(
                    Like.post_id == post.id,
                    Like.user_id == user_id
                )
            )
            post.is_liked = is_liked.scalar_one_or_none() is not None
        
        return posts

    async def get_user_posts(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Post]:
        """Get posts by a specific user."""
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.author_id == user_id)
            .where(Post.is_public == True)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Add interaction counts
        for post in posts:
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post.id)
            )
            post.likes_count = likes_count.scalar()
            
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post.id)
            )
            post.comments_count = comments_count.scalar()
        
        return posts

    async def search_posts(
        self, 
        db: AsyncSession, 
        *, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Post]:
        """Search posts by content."""
        search_query = f"%{query}%"
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.content.ilike(search_query))
            .where(Post.is_public == True)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Add interaction counts
        for post in posts:
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post.id)
            )
            post.likes_count = likes_count.scalar()
            
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post.id)
            )
            post.comments_count = comments_count.scalar()
        
        return posts

    async def get_by_type(
        self, 
        db: AsyncSession, 
        *, 
        post_type: PostType, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Post]:
        """Get posts by type."""
        query = (
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.post_type == post_type)
            .where(Post.is_public == True)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Add interaction counts
        for post in posts:
            likes_count = await db.execute(
                select(func.count(Like.id)).where(Like.post_id == post.id)
            )
            post.likes_count = likes_count.scalar()
            
            comments_count = await db.execute(
                select(func.count(Comment.id)).where(Comment.post_id == post.id)
            )
            post.comments_count = comments_count.scalar()
        
        return posts

post = CRUDPost(Post) 