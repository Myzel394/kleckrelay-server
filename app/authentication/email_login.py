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
from app.mails.send_email_login_token import send_email_login_token
from app.models.email_login import EmailLoginToken
from app.models.user import User


def hash_token(token: str) -> str:
    ...


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
    if is_token_expired(instance):
        raise EmailLoginTokenExpiredError()

    if instance.hashed_same_request_token != hash_token(same_request_token):
        raise EmailLoginTokenSameRequestTokenInvalidError()

    if instance.tries > EMAIL_LOGIN_TOKEN_MAX_TRIES:
        raise EmailLoginTokenMaxTriesReachedError()

    # Save this try
    instance.tries += 1

    db.add(instance)
    db.commit()
    db.refresh(instance)

    return instance.hashed_token == hash_token(token)


def create_email_login_token(db: Session, /, user: User) -> Tuple[EmailLoginToken, str]:
    """Create a new email login token.

    Returns a new email login token with the same_request_token.
    """

    # Delete existing email login tokens, there can only be one token
    if user.email_login_token is not None:
        delete_email_login_token(user.email_login_token)

    token = generate_token()
    same_request_token = generate_same_request_token()
    instance = EmailLoginToken(
        user=user,
        hashed_token=hash_token(token),
        hashed_same_request_token=hash_token(same_request_token)
    )

    send_email_login_token(
        user=user,
        token=token,
    )

    db.add(instance)
    db.commit()
    db.refresh(instance)

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

