"""
Authentication schemas.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    """Schema for user creation."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Schema for user login."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token."""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload."""
    model_config = ConfigDict(from_attributes=True)
    
    sub: str  # User ID as string (JWT requirement)
    exp: int  # Expiration timestamp