from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user, get_optional_current_user
from app.core.database import get_db
from app.crud.user import user
from app.crud.post import post
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfile, UserList
from app.schemas.post import PostList

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    # Check if user with email already exists
    db_user = await user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_user = await user.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return await user.create(db, obj_in=user_in)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information."""
    # Check if username is being changed and if it's already taken
    if user_in.username and user_in.username != current_user.username:
        db_user = await user.get_by_username(db, username=user_in.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    return await user.update(db, db_obj=current_user, obj_in=user_in)

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile by ID."""
    current_user_id = current_user.id if current_user else None
    db_user = await user.get_profile(db, user_id=user_id, current_user_id=current_user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.get("/{user_id}/posts", response_model=List[PostList])
async def get_user_posts(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get posts by a specific user."""
    # Check if user exists
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return await post.get_user_posts(db, user_id=user_id, skip=skip, limit=limit)

@router.get("/search/", response_model=List[UserList])
async def search_users(
    q: str = Query(..., min_length=1, max_length=50),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search users by username or full name."""
    return await user.search_users(db, query=q, skip=skip, limit=limit)

@router.get("/{user_id}/followers", response_model=List[UserList])
async def get_user_followers(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get followers of a user."""
    # Check if user exists
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    follows = await user.get_followers(db, user_id=user_id, skip=skip, limit=limit)
    return [follow.follower for follow in follows]

@router.get("/{user_id}/following", response_model=List[UserList])
async def get_user_following(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get users that a user is following."""
    # Check if user exists
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    follows = await user.get_following(db, user_id=user_id, skip=skip, limit=limit)
    return [follow.followed for follow in follows] 