from fastapi import APIRouter

from .auth import router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(router, prefix="/auth")
