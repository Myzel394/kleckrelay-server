from fastapi import APIRouter

from .account import router as account_router
from .alias import router as alias_router
from .authentication import router as auth_router
from .report import router as report_router
from .server import router as server_router
from .user_preference import router as user_preferences_router
from .reserved_alias import router as reserved_alias_router
from .admin import router as admin_router
from .otp_setup import router as user_otp_router
from .login_with_email_token import router as login_with_email_token_router
from .proxy import router as proxy_router
from .api_key import router as api_key_router

__all__ = [
    "routers",
]


routers = APIRouter()

routers.include_router(auth_router, prefix="/v1/auth")
routers.include_router(alias_router, prefix="/v1/alias")
routers.include_router(account_router, prefix="/v1/account")
routers.include_router(user_preferences_router, prefix="/v1/preferences")
routers.include_router(server_router, prefix="/v1/server")
routers.include_router(report_router, prefix="/v1/report")
routers.include_router(reserved_alias_router, prefix="/v1/reserved-alias")
routers.include_router(admin_router, prefix="/v1/admin")
routers.include_router(user_otp_router, prefix="/v1/setup-otp")
routers.include_router(login_with_email_token_router, prefix="/v1/auth/login/email-token")
routers.include_router(proxy_router, prefix="/v1/proxy")
routers.include_router(api_key_router, prefix="/v1/api-key")
