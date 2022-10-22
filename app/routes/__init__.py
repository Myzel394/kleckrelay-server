from fastapi import APIRouter

from .account import router as account_router
from .alias import router as alias_router
from .authentication import router as auth_router
from .image_proxy import router as image_proxy_router
from .report import router as report_router
from .settings import router as settings_router
from .user_preference import router as user_preferences_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/auth")
routers.include_router(alias_router, prefix="/alias")
routers.include_router(account_router, prefix="/account")
routers.include_router(image_proxy_router, prefix="/image-proxy")
routers.include_router(user_preferences_router, prefix="/preferences")
routers.include_router(settings_router, prefix="/settings")
routers.include_router(report_router, prefix="/report")
