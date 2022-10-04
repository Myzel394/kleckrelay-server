from fastapi import APIRouter

from .account import router as account_router
from .alias import router as alias_router
from .auth import router as auth_router
from .image_proxy import router as image_proxy_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/auth")
routers.include_router(alias_router, prefix="/alias")
routers.include_router(account_router, prefix="/account")
routers.include_router(image_proxy_router, prefix="/image-proxy")
