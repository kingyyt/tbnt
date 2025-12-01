from fastapi import APIRouter
from app.api.endpoints import user, work, chat, friends

api_router = APIRouter()
api_router.include_router(user.router, prefix="/auth", tags=["auth"])
api_router.include_router(work.router, prefix="/work", tags=["work"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
