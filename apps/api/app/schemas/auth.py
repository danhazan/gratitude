"""
Authentication schemas.
"""

from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    """Schema for user creation."""
    email: EmailStr
    username: constr(min_length=3, max_length=50)  # type: ignore
    password: constr(min_length=8)  # type: ignore

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = "bearer"