"""
User schemas.
"""
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    """Schema for user creation."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    username: str
    password: str

class UserOut(BaseModel):
    """Schema for user output."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    username: str 