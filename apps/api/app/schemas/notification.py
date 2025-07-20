from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class NotificationBase(BaseModel):
    type: str
    priority: str = "normal"
    title: str
    message: str
    data: Optional[Any] = None
    channel: str = "in_app"

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True 