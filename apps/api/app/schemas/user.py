from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# Create User Schema
class UserCreate(UserBase):
    pass

# Update User Schema
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# User Response Schema
class UserResponse(UserBase):
    id: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# User Profile Schema (with stats)
class UserProfile(UserResponse):
    posts_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    is_following: Optional[bool] = None

# User List Schema (for search/listing)
class UserList(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True 