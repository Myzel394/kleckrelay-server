from datetime import datetime

import pyotp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, Response

from app import constants, logger
from app.authentication.authentication_response import (
    OTPVerificationStatus,
    set_authentication_cookies,
)
from app.controllers.user_otp import create_otp, delete_otp, verify_otp_setup
from app.database.dependencies import get_db
from app.dependencies.require_otp import require_otp_if_enabled
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas._basic import HTTPBadRequestExceptionModel, SimpleDetailResponseModel
from app.schemas.user_otp import (
    DeleteOTPModel, HasUserOTPEnabledResponseModel, UserOTPResponseModel, VerifyOTPModel,
)
from app.utils.hashes import verify_slow_hash

router = APIRouter()


@router.get("/", response_model=HasUserOTPEnabledResponseModel)
def has_user_otp_enabled_api(
    user: User = Depends(get_user),
):
    logger.info(f"Request: Get OTP -> Checking if {user=} has OTP enabled.")

    return {
        "enabled": user.otp.is_verified if user.otp else False,
    }


@router.post("/", response_model=UserOTPResponseModel)
def create_user_otp_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info(f"Request: Create OTP -> Create new OTP for {user=}.")

    if user.otp:
        logger.info(f"Request: Create OTP -> Deleting old OTP.")
        delete_otp(db, otp=user.otp)

    logger.info(f"Request: Create OTP -> Creating OTP...")
    recovery_codes, otp = create_otp(db, user=user)
    logger.info(f"Request: Create OTP -> OTP created successfully.")

    return {
        "secret": otp.secret,
        "recovery_codes": recovery_codes,
    }


@router.post(
    "/verify",
    response_model=SimpleDetailResponseModel,
    responses={
        "202": {
            "model": SimpleDetailResponseModel,
            "detail": "OTP is already verified."
        },
        "409": {
            "model": HTTPBadRequestExceptionModel,
            "detail": "OTP has not been set up."
        },
        "410": {
            "model": HTTPBadRequestExceptionModel,
            "detail": "OTP has expired."
        },
        "400": {
            "model": HTTPBadRequestExceptionModel,
            "detail": "OTP code invalid."
        }
    }
)
def verify_otp_api(
    data: VerifyOTPModel,
    response: Response,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    if not user.otp:
        raise HTTPException(
            status_code=409,
            detail="OTP has not been set up.",
        )

    if user.otp.is_verified:
        return JSONResponse({
            "detail": "OTP is already verified."
        }, status_code=202)

    if user.otp.created_at < datetime.utcnow() - constants.OTP_TIMEOUT:
        delete_otp(db, otp=user.otp)

        raise HTTPException(
            status_code=410,
            detail="OTP has expired.",
        )

    if not verify_otp_setup(db, otp=user.otp, code=data.code):
        raise HTTPException(
            status_code=400,
            detail="OTP code invalid."
        )

    set_authentication_cookies(response, user, otp_status=OTPVerificationStatus.VERIFIED)

    return {
        "detail": "OTP is verified.",
    }


@router.delete(
    "/",
    response_model=SimpleDetailResponseModel,
    responses={
        "202": {
            "model": SimpleDetailResponseModel,
            "detail": "OTP was not enabled. No action taken."
        },
        "400": {
            "model": HTTPBadRequestExceptionModel,
            "detail": "Recovery code or OTP code is invalid."
        }
    }
)
def delete_user_otp_api(
    data: DeleteOTPModel,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Delete OTP -> Deleting OTP for {user=}.")

    if not user.otp:
        logger.info(f"Request: Delete OTP -> OTP was not enabled. No action taken.")
        return JSONResponse(
            status_code=202,
            content={
                "detail": "OTP was not enabled. No action taken."
            }
        )

    if (
        (data.code and pyotp.TOTP(user.otp.secret).verify(data.code))
        or (
            data.recovery_code and any(
                verify_slow_hash(recovery_code, data.recovery_code)
                for recovery_code in user.otp.hashed_recovery_codes
            )
        )
    ):
        logger.info(
            f"Request: Delete OTP -> Valid code or recovery code provided. Deleting OTP now."
        )
        delete_otp(db, otp=user.otp)

        return {
            "detail": "OTP was deleted."
        }

    logger.info(f"Request: Delete OTP -> Recovery code or OTP code is invalid.")
    return JSONResponse({
        "detail": "Recovery code or OTP code is invalid."
    }, status_code=400)
