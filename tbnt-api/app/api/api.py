from fastapi import APIRouter
from app.api.endpoints import user, work

api_router = APIRouter()
api_router.include_router(user.router, prefix="/auth", tags=["auth"])
api_router.include_router(work.router, prefix="/work", tags=["work"])
