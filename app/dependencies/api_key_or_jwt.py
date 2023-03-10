from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi_jwt.jwt import JwtAccess, JwtAuthBase
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import constants
from app.authentication.authentication_response import OTPVerificationStatus
from app.authentication.handler import access_security
from app.controllers.api_key import find_api_key
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.logger import logger
from app.models import User
from app.models.enums.api_key import APIKeyScope

__all__ = [
    "api_key_or_jwt",
]


def _extract_api_key_from_header(
    request: Request
) -> Optional[str]:
    raw_header = request.headers.get("Authorization", "")

    if (result := constants.API_KEY_HEADER_REGEX.match(raw_header)) is not None:
        return result.group(1)

    return None


def api_key_or_jwt(scope: APIKeyScope, should_check_otp: bool = False):
    async def _method(
        db: Session = Depends(get_db),
        api_key: Optional[str] = Depends(_extract_api_key_from_header),
        # Required for `access_security`
        bearer: JwtAuthBase.JwtAccessBearer = Security(JwtAccess._bearer),
        cookie: JwtAuthBase.JwtAccessCookie = Security(JwtAccess._cookie),
    ) -> User:
        logger.info("Checking API Key or JWT Token.")
        user = None
        credentials = None

        if api_key is not None:
            if (api_key_instance := find_api_key(db, api_key)) is not None:
                logger.info("API Key found in database.")

                if scope in api_key_instance.scopes:
                    logger.info("API Key has the required scope.")
                    user = api_key_instance.user
                else:
                    logger.info("API Key does not have the required scope.")

                    raise HTTPException(
                        status_code=401,
                        detail="API Key does not have the required scope.",
                    )
            else:
                logger.info("API Key not found in database.")

                raise HTTPException(
                    status_code=401,
                    detail="Invalid API Key.",
                )
        else:
            credentials = await access_security(bearer=bearer, cookie=cookie)

            if credentials is not None:
                logger.info("JWT Token found.")

                try:
                    user = get_user_by_id(db, credentials["id"])
                except NoResultFound:
                    logger.info("User account not found.")

                    raise HTTPException(
                        status_code=401,
                        detail="User account not found."
                    )
            else:
                logger.info("JWT Token not found.")

                raise HTTPException(
                    status_code=401,
                    detail="Invalid JWT Token.",
                )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid API Key or JWT Token.",
            )

        return user



    return _method
