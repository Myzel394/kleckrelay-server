from fastapi import APIRouter

from .auth import router as auth_router
from .alias import router as alias_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/auth")
routers.include_router(alias_router, prefix="/alias")
