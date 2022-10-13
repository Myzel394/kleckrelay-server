from fastapi import Response

from app import constants, life_constants
from app.authentication.handler import access_security, refresh_security
from app.models import User

__all__ = [
    "set_authentication_cookies",
]


def set_authentication_cookies(response: Response, user: User) -> None:
    response.set_cookie(
        key=constants.ACCESS_TOKEN_COOKIE_NAME,
        value=access_security.create_access_token(subject=user.to_jwt_object()),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        samesite="strict",
        domain=None if life_constants.IS_DEBUG else life_constants.APP_DOMAIN,
        max_age=life_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
    )

    response.set_cookie(
        key=constants.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_security.create_access_token(subject=user.to_jwt_object()),
        httponly=not life_constants.IS_DEBUG,
        secure=not life_constants.IS_DEBUG,
        samesite="strict",
        domain=None if life_constants.IS_DEBUG else life_constants.APP_DOMAIN,
        max_age=life_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES * 60,
    )
