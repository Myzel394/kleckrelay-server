import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.authentication.errors import (
    EmailLoginTokenExpiredError, EmailLoginTokenMaxTriesReachedError, EmailLoginTokenSameRequestTokenInvalidError
)

from app.constants import (
    EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS,
    EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH,
)

from app.life_constants import (
    EMAIL_LOGIN_TOKEN_CHARS, EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS,
    EMAIL_LOGIN_TOKEN_LENGTH, EMAIL_LOGIN_TOKEN_MAX_TRIES,
)
from app import logger
from app.mails.send_email_login_token import send_email_login_token
from app.models.email_login import EmailLoginToken
from app.models.user import User
from app.utils import hash_fast, hash_slowly


def get_token_from_email(db: Session, /, email: str) -> Optional[EmailLoginToken]:
    return db.query(EmailLoginToken).filter(EmailLoginToken.user.email == email).first()


def is_token_expired(instance: EmailLoginToken) -> bool:
    expires_at = instance.created_at + timedelta(seconds=EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS)

    return expires_at < datetime.now()


def is_token_valid(
        db: Session,
        /,
        instance: EmailLoginToken,
        token: str,
        same_request_token: str
) -> bool:
    logger.info(f"Is token valid: Checking if token is valid for {instance.email}.")

    if is_token_expired(instance):
        logger.info(f"Is token valid: Token for {instance.email} expired.")
        raise EmailLoginTokenExpiredError()

    if instance.hashed_same_request_token != hash_fast(same_request_token):
        logger.info(f"Is token valid: Token for {instance.email} is incorrect.")
        raise EmailLoginTokenSameRequestTokenInvalidError()

    if instance.tries > EMAIL_LOGIN_TOKEN_MAX_TRIES:
        logger.info(f"Is token valid: {instance.email} has exceeded it's max tries.")
        raise EmailLoginTokenMaxTriesReachedError()

    logger.info(f"Is token valid: Token for {instance.email} is correct.")

    # Save this try
    instance.tries += 1

    db.add(instance)
    db.commit()
    db.refresh(instance)

    logger.info(f"Is token valid: {instance.email} saved successfully.")

    return instance.hashed_token == hash_fast(token)


def create_email_login_token(db: Session, /, user: User) -> Tuple[EmailLoginToken, str]:
    """Create a new email login token.

    Returns a new email login token with the same_request_token.
    """

    # Delete existing email login tokens, there can only be one token
    if user.email_login_token is not None:
        with logger.with_info(
            f"Create email login token: Deleting existing email login token for {user.email}."
        ):
            delete_email_login_token(db, user.email_login_token)

    logger.info(f"Create email login token: Generating new email login token for {user.email}.")
    token = generate_token()
    same_request_token = generate_same_request_token()
    instance = EmailLoginToken(
        user=user,
        hashed_token=hash_fast(token),
        hashed_same_request_token=hash_fast(same_request_token)
    )

    send_email_login_token(
        user=user,
        token=token,
    )

    db.add(instance)
    db.commit()
    db.refresh(instance)

    logger.info(
        f"Create email login token: Email Login Token created for {user.email} successfully."
    )

    return instance, same_request_token


def delete_email_login_token(db: Session, /, instance: EmailLoginToken):
    db.delete(instance)
    db.commit()


def get_email_login_token_from_email(db: Session, /, email: str) -> Optional[EmailLoginToken]:
    return db.query(EmailLoginToken).filter(EmailLoginToken.email == email).first()


def generate_token() -> str:
    return "".join(
        secrets.choice(EMAIL_LOGIN_TOKEN_CHARS)
        for _ in range(EMAIL_LOGIN_TOKEN_LENGTH)
    )


def generate_same_request_token() -> str:
    return "".join(
        secrets.choice(EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS)
        for _ in range(EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH)
    )

