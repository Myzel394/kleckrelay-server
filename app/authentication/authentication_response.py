import enum
from datetime import datetime

from fastapi import Response

from app import constants, life_constants
from app.authentication.handler import access_security, refresh_security
from app.models import User

__all__ = [
    "OTPVerificationStatus",
    "set_authentication_cookies",
]


class OTPVerificationStatus(str, enum.Enum):
    VERIFIED = "verified"
    NOT_VERIFIED = "not_verified"
    CHALLENGED = "challenged"


def set_authentication_cookies(
    response: Response,
    user: User,
    otp_status: OTPVerificationStatus = OTPVerificationStatus.NOT_VERIFIED,
) -> None:
    subject = {
        "id": str(user.id),
        "otp_status": otp_status.value,
    }

    if otp_status is OTPVerificationStatus.CHALLENGED:
        subject["otp_challenged_at"] = datetime.utcnow().isoformat()

    # Cookies normally should be set by the reverse proxy - these are only for debug and testing
    # purposes
    response.set_cookie(
        key=constants.ACCESS_TOKEN_COOKIE_NAME,
        value=access_security.create_access_token(subject=subject),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        max_age=life_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
    )

    response.set_cookie(
        key=constants.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_security.create_refresh_token(subject=subject),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        max_age=life_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES * 60,
    )
