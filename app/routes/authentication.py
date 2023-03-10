from datetime import datetime

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import constants, life_constants, logger
from app.authentication.authentication_response import (
    OTPVerificationStatus, set_authentication_cookies,
)
from app.authentication.errors import (
    TokenIncorrectError, )
from app.authentication.handler import access_security, refresh_security
from app.controllers.email import get_email_by_address, send_verification_email, verify_email
from app.controllers.global_settings import get_settings_model
from app.controllers.user import (
    check_if_email_exists, create_user, get_user_by_id,
)
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, get_auth
from app.dependencies.get_user import get_user
from app.life_constants import EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS
from app.models import User
from app.schemas._basic import (
    HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel, SimpleDetailResponseModel,
)
from app.schemas.authentication import (
    ResendEmailAlreadyVerifiedResponseModel, ResendEmailModel, SignupResponseModel,
    VerifyEmailModel,
)
from app.schemas.otp_authentication import VerifyOTPAuthenticationModel
from app.schemas.user import UserCreate, UserDetail

router = APIRouter()


@router.post(
    "/signup",
    response_model=SignupResponseModel,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": UserCreate.schema(ref_template="#/components/schemas/{model}")
                }
            }
        }
    },
)
async def signup(
    request: Request,
    db: Session = Depends(get_db),
):
    logger.info("Request: Signup -> Sign up request.")

    user_data = await request.json()
    try:
        user = UserCreate(settings=get_settings_model(db), **user_data)
    except ValidationError as error:
        logger.info("Request: Signup -> Validation Error.")
        raise HTTPException(
            status_code=422,
            detail=error.errors(),
        )

    if await check_if_email_exists(db, user.email):
        logger.info("Request: Signup -> Email does not exist.")
        raise HTTPException(
            status_code=400,
            detail="This email address is already registered.",
        )

    logger.info(f"Request: Signup -> Create user {user.email}.")
    db_user = await create_user(db, user=user)

    logger.info("Request: Signup -> Return Response.")

    if life_constants.IS_DEBUG:
        logger.info(
            f"Request: Verify Email Token -> URL to verify email is: "
            f"http://localhost:5173/auth/verify-email?email={db_user.email.address}&token="
            f"{db_user.email.token}"
        )

    return {
        "normalized_email": db_user.email.address,
        "detail": "Created account successfully! Please verify your email now."
    }


@router.post(
    "/resend-email",
    response_model=SimpleDetailResponseModel,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
            "description": "Email address not found."
        },
        202: {
            "model": ResendEmailAlreadyVerifiedResponseModel,
            "description": "Email is already verified. No verification email sent."
        }
    }
)
def resend_email(
    input_data: ResendEmailModel,
    db: Session = Depends(get_db),
):
    logger.info("Request: Resend Email -> New Request.")

    try:
        email = get_email_by_address(db, address=input_data.email)

        if email.is_verified:
            return JSONResponse({
                "detail": "Email is already verified.",
                "code": "ok:email_already_verified",
            }, status_code=202)
        else:
            send_verification_email(email, language=email.user.language)
    except NoResultFound:
        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                detail="Email address not found.",
                status_code=404,
            )

    return {
        "detail": "Verification code was resent."
    }


@router.post(
    "/verify-email",
    response_model=UserDetail,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
        },
        202: {
            "model": UserDetail,
            "description": "Email is already verified."
        }
    }
)
def signup_verify_email(
    response: Response,
    input_data: VerifyEmailModel,
    db: Session = Depends(get_db),
):
    logger.info("Request: Verify Email -> Verify Email Request.")
    default_error_message = "Email or token invalid."

    try:
        email = get_email_by_address(db, address=input_data.email)

        if email.is_verified:
            logger.info(
                f"Request: Verify Email -> Email {email.address} already verified. Returning 202."
            )

            response.status_code = 202

            return email.user

        logger.info(f"Request: Verify Email -> Verifying email {email.address}.")
        verify_email(db, email=email, token=input_data.token)
        logger.info(
            f"Request: Verify Email -> Done verifying {email.address}. Returning credentials."
        )

        set_authentication_cookies(
            response,
            email.user,
            otp_status=OTPVerificationStatus.NOT_VERIFIED
        )

        return email.user
    except NoResultFound:
        logger.info(f"Request: Verify Email -> Email {input_data.email} not found.")
        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=404,
                detail="Email not found."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )

    except TokenIncorrectError:
        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=400,
                detail="Token invalid.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )


@router.post(
    "/login/verify-otp",
    response_model=UserDetail,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
            "description": "No OTP challenge found. Please request one."
        },
        410: {
            "model": HTTPBadRequestExceptionModel,
            "description": "OTP code expired."
        },
    }
)
async def verify_otp_api(
    data: VerifyOTPAuthenticationModel,
    response: Response,
    auth: AuthResult = Depends(get_auth(check_otp_if_enabled=False)),
):
    logger.info(
        f"Request: Verify OTP -> New request from user={auth.user} "
        f"with credentials={auth.credentials}."
    )

    otp_status = OTPVerificationStatus(auth.credentials["otp_status"])

    if otp_status is not OTPVerificationStatus.CHALLENGED:
        logger.info(
            f"Request: Verify OTP -> User has not challenged an OTP."
        )

        raise HTTPException(
            status_code=400,
            detail="No OTP challenge found. Please request one.",
        )

    challenged_at = datetime.fromisoformat(auth.credentials["otp_challenged_at"])

    if challenged_at < datetime.utcnow() - constants.OTP_TIMEOUT:
        logger.info(
            f"Request: Verify OTP -> User has challenged an OTP but it has expired."
        )

        raise HTTPException(
            status_code=410,
            detail="OTP challenge expired. Please request a new one.",
        )

    expected_code = pyotp.TOTP(auth.user.otp.secret).now()

    if data.code != expected_code:
        logger.info(
            f"Request: Verify OTP -> User has challenged an OTP but the code is incorrect."
        )

        raise HTTPException(
            status_code=400,
            detail="OTP code is incorrect.",
        )

    logger.info(f"Request: Verify OTP -> Token for user correct. Returning credentials.")
    set_authentication_cookies(response, auth.user, otp_status=OTPVerificationStatus.VERIFIED)

    return auth.user


@router.post(
    "/refresh",
    response_model=UserDetail,
    responses={
        "404": {
            "model": HTTPNotFoundExceptionModel,
            "description": "User account not found."
        }
    }
)
async def refresh_token(
    response: Response,
    auth: AuthResult = Depends(get_auth()),
    db: Session = Depends(get_db),
):
    logger.info("Request: Refresh -> New Request to refresh JWT token.")

    set_authentication_cookies(
        response,
        auth.user,
        otp_status=OTPVerificationStatus(auth.credentials["otp_status"])
    )

    return auth.user


@router.post(
    "/logout",
)
async def logout(
    response: Response,
):
    logger.info("Request: Logout -> New Request.")

    response.delete_cookie(constants.ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(constants.REFRESH_TOKEN_COOKIE_NAME)

    return{
        "detail": "Logout successfully!"
    }
