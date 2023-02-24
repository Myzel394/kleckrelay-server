import pyotp
from sqlalchemy.orm import Session

from app.models import User
from app.models.user_otp import StatusType, UserOTP

__all__ = [
    "get_otp_from_user",
    "create_otp",
    "verify_otp",
]


def get_otp_from_user(db: Session, /, user: User) -> UserOTP:
    return db.query(UserOTP).filter_by(user_id=user.id).one()


def create_otp(db: Session, /, user: User) -> UserOTP:
    secret = pyotp.random_base32()
    otp = UserOTP(
        user=user.id,
        secret=secret,
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return otp


def delete_otp(db: Session, /, otp: UserOTP) -> None:
    db.delete(otp)
    db.commit()


def verify_otp(db: Session, /, otp: UserOTP, code: str) -> bool:
    if code != pyotp.TOTP(otp.secret).now():
        return False

    otp.status = StatusType.AVAILABLE

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return True
