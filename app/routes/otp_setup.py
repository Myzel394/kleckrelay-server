from datetime import datetime

import pyotp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import constants, logger
from app.controllers.user_otp import create_otp, delete_otp, get_otp_from_user
from app.database.dependencies import get_db
from app.dependencies.require_otp import require_otp_if_enabled
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas._basic import HTTPBadRequestExceptionModel, SimpleDetailResponseModel
from app.schemas.user_otp import (
    HasUserOTPEnabledResponseModel, UserOTPResponseModel, VerifyOTPModel,
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

    if user.otp:
        logger.info(f"Request: Create OTP -> Deleting old OTP.")
        delete_otp(db, otp=user.otp)

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


@router.post(
    "/verify",
    response_model=SimpleDetailResponseModel,
    responses={
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
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    if not user.otp:
        raise HTTPException(
            status_code=409,
            detail="OTP has not been set up.",
        )

    if user.otp.created_at < datetime.utcnow() - constants.OTP_TIMEOUT:
        delete_otp(db, otp=user.otp)

        raise HTTPException(
            status_code=410,
            detail="OTP has expired.",
        )

    if not pyotp.TOTP(user.otp.secret).verify(data.code):
        raise HTTPException(
            status_code=400,
            detail="OTP code invalid."
        )

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
        }
    }
)
def delete_user_otp_api(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_otp_if_enabled),
):
    if not user.otp:
        return JSONResponse(
            status_code=202,
            content={
                "detail": "OTP was not enabled. No action taken."
            }
        )

    delete_otp(db, otp=user.otp)

    return {
        "detail": "OTP was deleted."
    }
