import pyotp
from sqlalchemy.orm import Session

from app import constants, life_constants, logger
from app.authentication.errors import TokenMaxTriesReachedError, TokenCorsInvalidError, TokenExpiredError
from app.controllers._cors import generate_cors_token
from app.models import User
from app.models.otp_authentication import OTPAuthentication
from app.utils.hashes import hash_fast, verify_fast_hash

__all__ = [
    "create_otp_authentication",
    "verify_otp_authentication",
    "delete_otp_authentication",
]


def create_otp_authentication(
    db: Session,
    /,
    user: User,
) -> tuple[str, OTPAuthentication]:
    cors_token = generate_cors_token()
    otp = OTPAuthentication(
        hashed_cors_token=hash_fast(cors_token),
        user=user,
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return cors_token, otp


def verify_otp_authentication(
    db: Session,
    /,
    otp: OTPAuthentication,
    cors_token: str,
    code: str,
) -> bool:
    logger.info("Verifying OTP Authentication.")

    if otp.is_expired:
        logger.info("OTP Authentication is expired.")
        raise TokenExpiredError()

    if otp.tries > life_constants.OTP_MAX_TRIES:
        logger.info("OTP Authentication has exceeded max tries.")
        raise TokenMaxTriesReachedError()

    if not verify_fast_hash(otp.hashed_cors_token, cors_token):
        logger.info("OTP Authentication CORS Token is invalid.")
        raise TokenCorsInvalidError()

    otp.tries += 1

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return pyotp.TOTP(otp.user.otp.secret).verify(code)


def delete_otp_authentication(
    db: Session,
    /,
    otp: OTPAuthentication,
) -> None:
    db.delete(otp)
    db.commit()
