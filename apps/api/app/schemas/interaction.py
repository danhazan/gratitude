from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Like Schemas
class LikeCreate(BaseModel):
    post_id: str

class LikeResponse(BaseModel):
    id: str
    user_id: str
    post_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    parent_id: Optional[str] = None

class CommentCreate(CommentBase):
    post_id: str

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentResponse(CommentBase):
    id: str
    author_id: str
    post_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CommentWithAuthor(CommentResponse):
    replies_count: int = 0

# Follow Schemas
class FollowCreate(BaseModel):
    followed_id: str

class FollowResponse(BaseModel):
    id: str
    follower_id: str
    followed_id: str
    created_at: datetime

    class Config:
        from_attributes = True 