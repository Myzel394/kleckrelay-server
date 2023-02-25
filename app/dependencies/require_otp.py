from typing import Optional

import pyotp
from fastapi import Body, Depends, HTTPException

from .get_user import get_user
from app.models import User
from .. import constants
from ..schemas.user_otp import VerifyOTPModel

__all__ = [
    "require_otp_if_enabled",
]


def require_otp_if_enabled(
    data: Optional[VerifyOTPModel] = Body(None),
    user: User = Depends(get_user),
) -> bool:
    if not user.has_otp_enabled:
        return False

    if data is None or not data.code:
        raise HTTPException(
            status_code=424,
            detail="OTP required.",
        )

    if not pyotp.TOTP(user.otp.secret).verify(data.code):
        raise HTTPException(
            status_code=424,
            detail="OTP code invalid."
        )

    return True
