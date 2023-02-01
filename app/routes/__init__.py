from fastapi import APIRouter

from .account import router as account_router
from .alias import router as alias_router
from .authentication import router as auth_router
from .image_proxy import router as image_proxy_router
from .report import router as report_router
from .settings import router as settings_router
from .user_preference import router as user_preferences_router
from .reserved_alias import router as reserved_alias_router
from .admin import router as admin_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/v1/auth")
routers.include_router(alias_router, prefix="/v1/alias")
routers.include_router(account_router, prefix="/v1/account")
routers.include_router(image_proxy_router, prefix="/v1/image-proxy")
routers.include_router(user_preferences_router, prefix="/v1/preferences")
routers.include_router(settings_router, prefix="/v1/server")
routers.include_router(report_router, prefix="/v1/report")
routers.include_router(reserved_alias_router, prefix="/v1/reserved-alias")
routers.include_router(admin_router, prefix="/v1/admin")
