from fastapi import Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import logger
from app.constants import CORS_TOKEN_LENGTH, EMAIL_REGEX, MAX_EMAIL_LENGTH
from app.controllers.email_login import get_email_login_token_from_email
from app.database.dependencies import get_db
from app.models import EmailLoginToken
from app.utils.hashes import verify_fast_hash

__all__ = [
    "get_email_login_token"
]


async def get_email_login_token(
    email: str = Body(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    ),
    same_request_token: str = Body(
        max_length=CORS_TOKEN_LENGTH,
    ),
    db: Session = Depends(get_db),
) -> EmailLoginToken:
    logger.info("Request: Email Login Token -> Getting email login token.")

    email_login = await get_email_login_token_from_email(db, email=email)

    if email_login is None:
        logger.info("Request: Email Login Token -> Email login token not found.")
        raise HTTPException(
            status_code=404,
            detail="Email login token not found.",
        )

    if not email_login.bypass_same_request_token and not verify_fast_hash(
        email_login.hashed_same_request_token,
        same_request_token
    ):
        logger.info("Request: Email Login Token -> Same request token is invalid.")
        raise HTTPException(
            status_code=400,
            detail="Same Request Token is invalid.",
        )

    logger.info("Request: Email Login Token -> Email login token retrieved.")
    return email_login
