from starlette.responses import Response

from app import life_constants
from app.authentication.handler import access_security, refresh_security
from app.models import User

__all__ = [
    "set_authentication_cookies",
    "create_authentication_response"
]


def set_authentication_cookies(response: Response, user: User) -> None:
    response.set_cookie(
        key="access_token_cookie",
        value=access_security.create_access_token(subject=user.to_jwt_object()),
        httponly=True,
        secure=True,
        samesite="strict",
        domain=life_constants.APP_DOMAIN,
        max_age=life_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token_cookie",
        value=refresh_security.create_access_token(subject=user.to_jwt_object()),
        httponly=True,
        secure=True,
        samesite="strict",
        domain=life_constants.APP_DOMAIN,
        max_age=life_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES * 60,
    )


def create_authentication_response(user: User) -> Response:
    response = Response(user.to_response_object())

    set_authentication_cookies(response, user)

    return response
