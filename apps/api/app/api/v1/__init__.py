from fastapi import APIRouter
from app.api.v1 import posts, follows, notifications, auth

api_router = APIRouter()

api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(follows.router, prefix="/follows", tags=["follows"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"]) 