from datetime import timedelta

from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie

from app.constant_keys import JWT_REFRESH_SECRET_KEY, JWT_SECRET_KEY
from app.life_constants import (
    ACCESS_TOKEN_EXPIRE_IN_MINUTES,
    REFRESH_TOKEN_EXPIRE_IN_MINUTES,
)

__all__ = [
    "access_security",
    "refresh_security",
]

access_security = JwtAccessBearerCookie(
    secret_key=JWT_SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES),
)
refresh_security = JwtRefreshBearerCookie(
    secret_key=JWT_REFRESH_SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_IN_MINUTES),
)
