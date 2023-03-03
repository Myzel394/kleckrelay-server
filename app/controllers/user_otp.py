import secrets

import pyotp
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.models import User
from app.models.user_otp import OTPStatusType, UserOTP

__all__ = [
    "get_otp_from_user",
    "create_otp",
    "verify_otp_setup",
    "delete_otp",
]

from app.utils.hashes import hash_slowly


def _create_recovery_code() -> str:
    raw_code = "".join(
        secrets.choice(life_constants.RECOVERY_CODE_CHARS)
        for _ in range(life_constants.RECOVERY_CODE_LENGTH)
    )

    # Split the code into groups of 5 characters
    return "-".join(
        raw_code[i:i + 5]
        for i in range(0, len(raw_code), 5)
    )


def get_otp_from_user(db: Session, /, user: User) -> UserOTP:
    return db.query(UserOTP).filter_by(user_id=user.id).one()


def create_otp(db: Session, /, user: User) -> tuple[list[str], UserOTP]:
    logger.info(f"Request: Create OTP -> Creating OTP for {user=}.")
    secret = pyotp.random_base32()
    recovery_codes = [
        _create_recovery_code()
        for _ in range(life_constants.RECOVERY_CODES_AMOUNT)
    ]
    logger.info(f"Request: Create OTP -> Created recovery codes.")
    otp = UserOTP(
        user=user,
        secret=secret,
        hashed_recovery_codes=[
            hash_slowly(
                code.replace("-", ""),
            )
            for code in recovery_codes
        ]
    )

    logger.info(f"Request: Create OTP -> Committing to database.")
    db.add(otp)
    db.commit()
    db.refresh(otp)
    logger.info(f"Request: Create OTP -> Done. Returning.")

    return recovery_codes, otp


def delete_otp(db: Session, /, otp: UserOTP) -> None:
    db.delete(otp)
    db.commit()


def verify_otp_setup(db: Session, /, otp: UserOTP, code: str) -> bool:
    if code != pyotp.TOTP(otp.secret).now():
        return False

    otp.status = OTPStatusType.AVAILABLE

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return True
