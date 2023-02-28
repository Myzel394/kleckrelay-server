from fastapi import Response

from app import constants, life_constants
from app.authentication.handler import access_security, refresh_security
from app.models import User

__all__ = [
    "set_authentication_cookies",
]


def set_authentication_cookies(response: Response, user: User, has_otp_verified: bool) -> None:
    # Cookies normally should be set by the reverse proxy - these are only for debug and testing
    # purposes
    response.set_cookie(
        key=constants.ACCESS_TOKEN_COOKIE_NAME,
        value=access_security.create_access_token(subject={
            "id": str(user.id),
            "has_otp_verified": has_otp_verified,
        }),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        max_age=life_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
    )

    response.set_cookie(
        key=constants.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_security.create_refresh_token(subject={
            "id": str(user.id),
            "has_otp_verified": has_otp_verified,
        }),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        max_age=life_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES * 60,
    )
