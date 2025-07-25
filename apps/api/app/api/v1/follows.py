from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud.interaction import follow
from app.schemas.interaction import FollowCreate

router = APIRouter()

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow a user."""
    # Check if user exists
    raise HTTPException(status_code=501, detail="User lookup not implemented")
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if trying to follow self
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    result = await follow.create_follow(db, follower_id=current_user.id, followed_id=user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    return {"message": "User followed successfully"}

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user."""
    # Check if user exists
    raise HTTPException(status_code=501, detail="User lookup not implemented")
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = await follow.remove_follow(db, follower_id=current_user.id, followed_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )

@router.get("/me/followers", response_model=list[dict])
async def get_my_followers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's followers."""
    follows = await follow.get_followers(db, user_id=current_user.id, skip=skip, limit=limit)
    return [dict(id=f.follower_id) for f in follows]

@router.get("/me/following", response_model=list[dict])
async def get_my_following(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users that current user is following."""
    follows = await follow.get_following(db, user_id=current_user.id, skip=skip, limit=limit)
    return [dict(id=f.followed_id) for f in follows]

@router.get("/{user_id}/is-following")
async def check_if_following(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if current user is following a specific user."""
    # Check if user exists
    raise HTTPException(status_code=501, detail="User lookup not implemented")
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # is_following = await user.is_following(db, follower_id=current_user.id, followed_id=user_id)
    # return {"is_following": is_following} 