"""
Test database setup and basic operations.
"""

import pytest
import uuid
from sqlalchemy import text
from app.models.user import User
from app.models.post import Post
from app.models.interaction import Like, Comment, Follow

class TestDatabaseSetup:
    """Test database setup and basic operations."""
    
    @pytest.mark.asyncio
    async def test_database_connection(self, db_session):
        """Test that database connection works."""
        # Test basic query
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    @pytest.mark.asyncio
    async def test_tables_exist(self, db_session):
        """Test that all tables were created."""
        # Check that users table exists
        result = await db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        assert result.fetchone() is not None
        
        # Check that posts table exists
        result = await db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'"))
        assert result.fetchone() is not None
        
        # Check that likes table exists
        result = await db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='likes'"))
        assert result.fetchone() is not None
    
    @pytest.mark.asyncio
    async def test_user_creation(self, db_session):
        """Test creating a user in the database."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            id=str(uuid.uuid4()),
            email=f"test_{unique_id}@example.com",
            username=f"testuser_{unique_id}",
            full_name="Test User"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Verify user was created
        assert user.id is not None
        assert user.email == f"test_{unique_id}@example.com"
        assert user.username == f"testuser_{unique_id}"
    
    @pytest.mark.asyncio
    async def test_post_creation(self, db_session):
        """Test creating a post in the database."""
        # Create a test user first with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            id=str(uuid.uuid4()),
            email=f"test_{unique_id}@example.com",
            username=f"testuser_{unique_id}",
            full_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create a test post
        post = Post(
            id=str(uuid.uuid4()),
            author_id=user.id,
            content="This is a test post about gratitude",
            post_type="daily"
        )
        
        db_session.add(post)
        await db_session.commit()
        await db_session.refresh(post)
        
        # Verify post was created
        assert post.id is not None
        assert post.author_id == user.id
        assert post.content == "This is a test post about gratitude"
    
    @pytest.mark.asyncio
    async def test_like_creation(self, db_session):
        """Test creating a like in the database."""
        # Create a test user with unique data
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            id=str(uuid.uuid4()),
            email=f"test_{unique_id}@example.com",
            username=f"testuser_{unique_id}",
            full_name="Test User"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create a test post
        post = Post(
            id=str(uuid.uuid4()),
            author_id=user.id,
            content="This is a test post",
            post_type="daily"
        )
        db_session.add(post)
        await db_session.commit()
        
        # Create a like
        like = Like(
            id=str(uuid.uuid4()),
            user_id=user.id,
            post_id=post.id
        )
        
        db_session.add(like)
        await db_session.commit()
        await db_session.refresh(like)
        
        # Verify like was created
        assert like.id is not None
        assert like.user_id == user.id
        assert like.post_id == post.id 