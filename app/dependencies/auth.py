import enum
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from fastapi_jwt.jwt import JwtAccess, JwtAuthBase
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import constants, logger
from app.authentication.authentication_response import OTPVerificationStatus
from app.authentication.handler import access_security
from app.controllers.api_key import find_api_key
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.models import APIKey, User
from app.models.enums.api_key import APIKeyScope

__all__ = [
    "AuthResultMethod",
    "AuthResult",
    "get_auth",
]


class AuthResultMethod(str, enum.Enum):
    JWT = "jwt"
    API_KEY = "api_key"


@dataclass
class AuthResult:
    user: User
    method: AuthResultMethod
    credentials: Optional[JwtAuthorizationCredentials] = None
    api_key: Optional[APIKey] = None


def _extract_api_key_from_header(
    request: Request
) -> Optional[str]:
    raw_header = request.headers.get("Authorization", "")

    if (result := constants.API_KEY_HEADER_REGEX.match(raw_header)) is not None:
        return result.group(1)

    return None


def get_auth(
    allow_api: bool = False,
    api_key_scope: Optional[APIKeyScope] = None,
    check_otp_if_enabled: bool = True,
    enforce_otp: bool = False,
    require_admin: bool = False,
):
    async def _method(
        db: Session = Depends(get_db),
        api_key_header: Optional[str] = Depends(_extract_api_key_from_header),
        # Required for `access_security`
        bearer: JwtAuthBase.JwtAccessBearer = Security(JwtAccess._bearer),
        cookie: JwtAuthBase.JwtAccessCookie = Security(JwtAccess._cookie),
    ):
        def _get_api():
            if (api_key_instance := find_api_key(db, api_key_header)) is not None:
                logger.info("API Key found in database.")

                if api_key_scope in api_key_instance.scopes:
                    logger.info("API Key has the required scope.")
                    return api_key_instance

                logger.info("API Key does not have the required scope.")

                raise HTTPException(
                    status_code=401,
                    detail="API Key has not the required scope.",
                )

        async def _get_credentials():
            credentials = await access_security(bearer=bearer, cookie=cookie)

            if credentials is not None:
                logger.info("JWT Token found.")

                try:
                    return get_user_by_id(db, credentials["id"]), credentials
                except NoResultFound:
                    logger.info("User account not found.")

                    raise HTTPException(
                        status_code=401,
                        detail="Credentials invalid.",
                    )

        if allow_api and api_key_header:
            if (api_key := _get_api()) is not None:
                if require_admin and not api_key.user.is_admin:
                    raise HTTPException(
                        status_code=401,
                        detail="Admin privileges required to use this endpoint.",
                    )

                return AuthResult(
                    user=api_key.user,
                    method=AuthResultMethod.API_KEY,
                )

            raise HTTPException(
                status_code=401,
                detail="API Key invalid.",
            )

        if (result := await _get_credentials()) is not None:
            user, credentials = result

            if enforce_otp:
                if not user.has_otp_enabled:
                    raise HTTPException(
                        status_code=401,
                        detail="You need to enable OTP to use this endpoint.",
                    )

            if check_otp_if_enabled or enforce_otp:
                if user.has_otp_enabled and \
                    OTPVerificationStatus(credentials["otp_status"]) is not OTPVerificationStatus.VERIFIED:
                    raise HTTPException(
                        status_code=424,
                        detail="OTP required.",
                    )

            if require_admin and not user.is_admin:
                raise HTTPException(
                    status_code=401,
                    detail="Admin privileges required to use this endpoint.",
                )

            return AuthResult(
                user=user,
                credentials=credentials,
                method=AuthResultMethod.JWT,
            )

        raise HTTPException(
            status_code=401,
            detail="Credentials or API Key invalid.",
        )

    return _method