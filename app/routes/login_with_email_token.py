from typing import Union

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import logger
from app.authentication.authentication_response import (
    OTPVerificationStatus, set_authentication_cookies,
)
from app.authentication.errors import (
    TokenExpiredError,
    TokenIncorrectError, TokenMaxTriesReachedError, TokenCorsInvalidError,
)
from app.controllers.email import send_verification_email
from app.controllers.email_login import (
    change_allow_login_from_different_devices, create_email_login_token,
    delete_email_login_token, get_email_login_token_from_email, validate_token,
)
from app.controllers.user import (
    check_if_email_exists,
    get_user_by_email
)
from app.database.dependencies import get_db
from app.dependencies.email_login import get_email_login_token
from app.life_constants import EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS
from app.mails.send_email_login_token import send_email_login_token
from app.models import EmailLoginToken
from app.schemas._basic import (
    HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel,
    SimpleDetailResponseModel,
)
from app.schemas.authentication import (
    EmailLoginTokenResponseModel,
    EmailLoginTokenVerifyModel,
    LoginWithEmailOTPRequiredResponseModel, LoginWithEmailTokenModel,
)
from app.schemas.user import UserDetail

router = APIRouter()


@router.post(
    "/",
    response_model=EmailLoginTokenResponseModel,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
        }
    }
)
async def create_login_with_email_token(
    input_data: LoginWithEmailTokenModel,
    db: Session = Depends(get_db),
):
    logger.info("Request: Login with email token -> New Request.")
    email = input_data.email

    # No other error can occur, so we can simply return if the email doesn't exist
    if not (await check_if_email_exists(db, email)):
        logger.info(f"Request: Login with email token -> Email {email} not found.")
        raise HTTPException(
            status_code=404,
            detail="Email not found."
        )

    user = await get_user_by_email(db, email=email)

    if not user.email.is_verified:
        logger.info(f"Request: Login with email token -> Email {email} not verified.")

        send_verification_email(user.email, language=user.language)

        raise HTTPException(
            status_code=400,
            detail="Your email has not been verified. Please verify it.",
        )

    logger.info(f"Request: Login with email token -> Create email login token for {email}.")
    token_data = create_email_login_token(db, user=user)

    return {
        "same_request_token": token_data[1],
        "detail": "An email was sent."
    }


@router.post(
    "/verify",
    response_model=Union[UserDetail, LoginWithEmailOTPRequiredResponseModel],
    responses={
        202: {
            "model": LoginWithEmailOTPRequiredResponseModel,
            "description": "User was successfully logged in, but OTP is required.",
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
        },
        400: {
            "model": HTTPBadRequestExceptionModel,
        }
    }
)
async def verify_email_token(
    response: Response,
    input_data: EmailLoginTokenVerifyModel,
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Verify Email Token -> New verification request for {input_data.email}.")
    default_error_message = "Email or token or same request token invalid or no token found."

    email_login = await get_email_login_token_from_email(db, email=input_data.email)

    if not email_login:
        logger.info(
            f"Request: Verify Email Token -> No Login Token for {input_data.email} found."
        )

        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=404,
                detail="No Token found. Please request one.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )

    try:
        validate_token(
            db,
            instance=email_login,
            token=input_data.token,
            same_request_token=input_data.same_request_token
        )
    except TokenExpiredError:
        logger.info(
            f"Request: Verify Email Token -> Token for {input_data.email} expired."
        )

        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=400,
                detail="Token expired. Please request a new one.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )
    except TokenMaxTriesReachedError:
        logger.info(
            f"Request: Verify Email Token -> Token for {input_data.email} has exceeded its "
            f"tries."
        )

        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=400,
                detail="Token tries exceeded. Please request a new one.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )
    except TokenCorsInvalidError:
        logger.info(
            f"Request: Verify Email Token -> Same request token for {input_data.email} is "
            f"invalid."
        )

        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=400,
                detail="Same request token invalid.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )
    except TokenIncorrectError:
        logger.info(
            f"Request: Verify Email Token -> Token for {input_data.email} incorrect."
        )
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

    logger.info(
        f"Request: Verify Email Token -> Token for {input_data.email} correct. Proceeding."
    )

    user = email_login.user

    logger.info(
        f"Request: Verify Email Token -> Removing Email Login Token for {input_data.email}."
    )
    # Clean up the token
    delete_email_login_token(db, email_login)

    logger.info(
        f"Request: Verify Email Token -> Returning credentials for {input_data.email}"
    )

    if user.has_otp_enabled:
        logger.info("Request: Verify Email Token -> User has OTP enabled. Creating OTP...")
        set_authentication_cookies(response, user, otp_status=OTPVerificationStatus.CHALLENGED)

        logger.info("Request: Verify Email Token -> OTP created. Returning OTP.")

        response.status_code = 202

        return {
            "code": "otp_challenge_created",
        }
    else:
        set_authentication_cookies(response, user, otp_status=OTPVerificationStatus.NOT_VERIFIED)

        return user


@router.post(
    "/resend-email",
    response_model=SimpleDetailResponseModel,
    responses={
        404: {
            "model": HTTPBadRequestExceptionModel,
            "description": "No current email login token found. Please request one."
        }
    }
)
async def resend_email_login_token(
    email_login: EmailLoginToken = Depends(get_email_login_token),
):
    logger.info(
        f"Request: Resend Email Login Token: New Request for {email_login.user.email.address}."
    )

    send_email_login_token(
        user=email_login.user,
        token=email_login.token,
    )

    return {
        "detail": "Login code was resent."
    }


@router.patch(
    "/allow-login-from-different-devices",
    response_model=SimpleDetailResponseModel,
    responses={
        404: {
            "model": HTTPBadRequestExceptionModel,
            "description": "No current email login token found. Please request one."
        }
    }
)
async def email_login_allow_login_from_different_devices(
    allow: bool = Body(..., example=True),
    db: Session = Depends(get_db),
    email_login_token: EmailLoginToken = Depends(get_email_login_token),
):
    change_allow_login_from_different_devices(
        db,
        email_login_token,
        allow,
    )

    return {
        "detail": "Login from different devices updated."
    }

