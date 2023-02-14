from fastapi import Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.models import User

__all__ = [
    "get_user",
    "get_admin_user"
]


async def get_user(
    db: Session = Depends(get_db),
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> User:
    logger.info("Request: User -> Getting user.")

    try:
        return get_user_by_id(db, credentials["id"])
    except NoResultFound:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )


async def get_admin_user(
    db: Session = Depends(get_db),
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> User:
    try:
        user = get_user_by_id(db, credentials["id"])

        if not user.is_admin:
            raise HTTPException(
                status_code=401,
                detail="User account not found."
            )

        return user
    except NoResultFound:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )
