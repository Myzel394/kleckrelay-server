from fastapi import APIRouter

from .auth import router as auth_router
from .account import router as account_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/auth")
routers.include_router(account_router, prefix="/account")
