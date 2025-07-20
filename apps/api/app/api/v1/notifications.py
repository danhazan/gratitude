from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse
from sqlalchemy.future import select
from typing import List

router = APIRouter()

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_in: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    # Only allow creating notifications for the current user (or admin logic can be added)
    if notification_in.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create notification for another user")
    notification = Notification(**notification_in.dict())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id))
    notifications = result.scalars().all()
    return notifications 