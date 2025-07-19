from fastapi import APIRouter
from app.api.v1 import users, posts, follows

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(follows.router, prefix="/follows", tags=["follows"]) 