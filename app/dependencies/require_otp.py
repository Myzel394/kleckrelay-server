from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials

from .get_user import get_user
from app.models import User
from ..authentication.handler import access_security

__all__ = [
    "require_otp_if_enabled",
]


def require_otp_if_enabled(
    user: User = Depends(get_user),
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> bool:
    if not user.has_otp_enabled:
        return False

    if credentials["has_otp_verified"]:
        return True

    raise HTTPException(
        status_code=424,
        detail="OTP required.",
    )
