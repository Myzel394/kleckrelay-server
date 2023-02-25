import pyotp
from sqlalchemy.orm import Session

from app.models import User
from app.models.user_otp import OTPStatusType, UserOTP

__all__ = [
    "get_otp_from_user",
    "create_otp",
    "verify_otp_setup",
    "delete_otp",
]


def get_otp_from_user(db: Session, /, user: User) -> UserOTP:
    return db.query(UserOTP).filter_by(user_id=user.id).one()


def create_otp(db: Session, /, user: User) -> UserOTP:
    secret = pyotp.random_base32()
    otp = UserOTP(
        user=user,
        secret=secret,
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return otp


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
