import pyotp
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import constants, logger
from app.controllers.user_otp import create_otp, delete_otp, get_otp_from_user, verify_otp_setup
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.user_otp import (
    HasUserOTPEnabledResponseModel, UserOTPResponseModel,
    VerifyOTPModel,
)

router = APIRouter()


@router.get("/", response_model=HasUserOTPEnabledResponseModel)
def has_user_otp_enabled_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Get OTP -> Checking if {user=} has OTP enabled.")

    try:
        get_otp_from_user(db, user=user)
    except NoResultFound:
        logger.info("Request: Get OTP -> No OTP found.")
        return {
            "enabled": False,
        }
    else:
        logger.info("Request: Get OTP -> OTP found.")
        return {
            "enabled": True,
        }


@router.post("/", response_model=UserOTPResponseModel)
def create_user_otp_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Create OTP -> Create new OTP for {user=}.")

    try:
        otp = get_otp_from_user(db, user=user)
    except NoResultFound:
        pass
    else:
        logger.info(f"Request: Create OTP -> Deleting old OTP.")
        delete_otp(db, otp=otp)

    logger.info(f"Request: Create OTP -> Creating OTP...")
    otp = create_otp(db, user=user)
    logger.info(f"Request: Create OTP -> OTP created successfully.")

    return {
        "id": otp.id,
        "secret": otp.secret,
        "uri": pyotp.TOTP(otp.secret).provisioning_uri(
            name=user.email.address,
            issuer_name="KleckRelay",
        )
    }


@router.post("/verify", response_model=SimpleDetailResponseModel)
def verify_otp_api(
    data: VerifyOTPModel,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Verify OTP -> Verifying OTP for {user=}.")
    try:
        otp = get_otp_from_user(db, user=user)
    except NoResultFound:
        logger.info(f"Request: Verify OTP -> No OTP found.")
        raise HTTPException(
            status_code=400,
            detail="You have not enabled OTP. Please enable it first.",
        )

    if otp.is_verified:
        logger.info(f"Request: Verify OTP -> OTP already verified.")
        return JSONResponse({
            "detail": "OTP is already verified.",
        }, status_code=202)

    if not verify_otp_setup(db, otp=otp, code=data.code):
        logger.info(f"Request: Verify OTP -> Code invalid.")
        return JSONResponse({
            "detail": "Invalid OTP.",
        }, status_code=400)

    logger.info(f"Request: Verify OTP -> OTP verified successfully.")
    return {
        "detail": "OTP is verified.",
    }
