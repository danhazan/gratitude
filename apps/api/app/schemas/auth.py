"""
Authentication schemas.
"""

from pydantic import BaseModel, EmailStr, constr, ConfigDict

class UserCreate(BaseModel):
    """Schema for user creation."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    username: constr(min_length=3, max_length=50)  # type: ignore
    password: constr(min_length=8)  # type: ignore

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