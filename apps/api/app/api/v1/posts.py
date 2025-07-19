from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user, get_optional_current_user
from app.core.database import get_db
from app.crud.post import post
from app.crud.interaction import like, comment
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostList, PostType
from app.schemas.interaction import CommentCreate, CommentResponse, CommentWithAuthor

router = APIRouter()

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post."""
    from app.models.post import Post
    import uuid
    
    # Create post object directly with author_id
    post_obj = Post(
        id=str(uuid.uuid4()),
        author_id=current_user.id,
        content=post_in.content,
        post_type=post_in.post_type,
        title=post_in.title,
        image_url=post_in.image_url,
        location=post_in.location,
        is_public=post_in.is_public
    )
    
    db.add(post_obj)
    await db.commit()
    await db.refresh(post_obj)
    
    return post_obj

@router.get("/feed", response_model=List[PostList])
async def get_user_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's personalized feed."""
    return await post.get_user_feed(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/", response_model=List[PostList])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    post_type: Optional[PostType] = Query(None),
    q: Optional[str] = Query(None, min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db)
):
    """Get posts with optional filtering."""
    if q:
        return await post.search_posts(db, query=q, skip=skip, limit=limit)
    elif post_type:
        return await post.get_by_type(db, post_type=post_type, skip=skip, limit=limit)
    else:
        return await post.get_multi_with_author(db, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=PostList)
async def get_post(
    post_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific post by ID."""
    current_user_id = current_user.id if current_user else None
    db_post = await post.get_with_author(db, post_id=post_id, current_user_id=current_user_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return db_post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_in: PostUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a post."""
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return await post.update(db, db_obj=db_post, obj_in=post_in)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a post."""
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await post.remove(db, id=post_id)

@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Like a post."""
    # Check if post exists
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    result = await like.create_like(db, user_id=current_user.id, post_id=post_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    return {"message": "Post liked successfully"}

@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlike a post."""
    # Check if post exists
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    success = await like.remove_like(db, user_id=current_user.id, post_id=post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not liked"
        )

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    comment_in: CommentCreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a comment on a post."""
    # Check if post exists
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return await comment.create_comment(
        db, 
        author_id=current_user.id, 
        post_id=post_id, 
        content=comment_in.content,
        parent_id=comment_in.parent_id
    )

@router.get("/{post_id}/comments", response_model=List[CommentWithAuthor])
async def get_post_comments(
    post_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get comments for a post."""
    # Check if post exists
    db_post = await post.get(db, id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return await comment.get_post_comments(db, post_id=post_id, skip=skip, limit=limit) 