import pyotp
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import constants
from app.controllers.user_otp import create_otp, delete_otp, get_otp_from_user, verify_otp
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import User
from app.models.user_otp import UserOTP
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.user_otp import HasUserOTPEnabledResponseModel, UserOTPResponseModel

router = APIRouter()


@router.get("/", response_model=HasUserOTPEnabledResponseModel)
def has_user_otp_enabled_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    try:
        get_otp_from_user(db, user=user)
    except NoResultFound:
        return {
            "has_otp_enabled": False,
        }
    else:
        return {
            "has_otp_enabled": True,
        }


@router.post("/", response_model=UserOTPResponseModel)
def create_user_otp_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    try:
        otp = get_otp_from_user(db, user=user)
    except NoResultFound:
        pass
    else:
        delete_otp(db, otp=otp)

    otp = create_otp(db, user=user)

    return {
        "id": otp.id,
        "secret": otp.secret,
        "uri": pyotp.TOTP(otp.secret).provisioning_uri(
            name=user.email,
            issuer_name="KleckRelay",
        )
    }


@router.post("/verify", response_model=SimpleDetailResponseModel)
def verify_otp_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    code: str = Body(
        regex=constants.OTP_REGEX,
    ),
):
    try:
        otp = get_otp_from_user(db, user=user)
    except NoResultFound:
        raise HTTPException(
            status_code=400,
            detail="You have not enabled OTP. Please enable it first.",
        )

    if otp.is_verified:
        return JSONResponse({
            "detail": "OTP is already verified.",
        }, status_code=202)

    if not verify_otp(db, otp=otp, code=code):
        return JSONResponse({
            "detail": "Invalid OTP.",
        }, status_code=400)

    return {
        "detail": "OTP is verified.",
    }
