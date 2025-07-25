from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PostType(str, Enum):
    DAILY = "daily"
    PHOTO = "photo"
    SPONTANEOUS = "spontaneous"

# Base Post Schema
class PostBase(BaseModel):
    title: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=1000)
    post_type: PostType = PostType.DAILY
    image_url: Optional[str] = None
    is_public: bool = True

# Create Post Schema
class PostCreate(PostBase):
    pass

# Update Post Schema
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    post_type: Optional[PostType] = None
    image_url: Optional[str] = None
    is_public: Optional[bool] = None

# Post Response Schema
class PostResponse(PostBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Post with Author Info
class PostWithAuthor(PostResponse):
    likes_count: int = 0
    comments_count: int = 0
    is_liked: Optional[bool] = None

# Post List Schema (for feed)
class PostList(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    post_type: PostType
    image_url: Optional[str] = None
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    is_liked: Optional[bool] = None

    class Config:
        from_attributes = True 