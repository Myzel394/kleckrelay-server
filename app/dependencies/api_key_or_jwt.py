from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi_jwt.jwt import JwtAccess, JwtAuthBase
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import constants
from app.authentication.handler import access_security
from app.controllers.api_key import find_api_key
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


def api_key_or_jwt(scope: APIKeyScope):
    async def _method(
        db: Session,
        api_key: Optional[str] = Depends(_extract_api_key_from_header),
        # Required for `access_security`
        bearer: JwtAuthBase.JwtAccessBearer = Security(JwtAccess._bearer),
        cookie: JwtAuthBase.JwtAccessCookie = Security(JwtAccess._cookie),
    ):
        if api_key is not None:
            if (api_key_instance := find_api_key(db, api_key)) is not None:
                if scope in api_key_instance.scopes:
                    return

                raise HTTPException(
                    status_code=401,
                    detail="API Key does not have the required scope.",
                )

            raise HTTPException(
                status_code=401,
                detail="Invalid API Key.",
            )
        else:
            if await access_security(bearer=bearer, cookie=cookie):
                return

            raise HTTPException(
                status_code=401,
                detail="Invalid JWT Token.",
            )

    return _method
