from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import constants, life_constants, logger
from app.authentication.authentication_response import (
    set_authentication_cookies,
)
from app.authentication.errors import (
    EmailIncorrectTokenError, EmailLoginTokenExpiredError,
    EmailLoginTokenMaxTriesReachedError, EmailLoginTokenSameRequestTokenInvalidError,
)
from app.authentication.handler import refresh_security
from app.controllers.email import get_email_by_address, send_verification_email, verify_email
from app.controllers.email_login import (
    create_email_login_token,
    delete_email_login_token, get_email_login_token_from_email, is_token_valid,
)
from app.controllers.user import (
    check_if_email_exists, create_user,
    get_user_by_email, get_user_by_id,
)
from app.database.dependencies import get_db
from app.life_constants import EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS
from app.mails.send_email_login_token import send_email_login_token
from app.schemas._basic import (
    HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel,
    SimpleDetailResponseModel,
)
from app.schemas.authentication import (
    EmailLoginResendMailModel, EmailLoginTokenResponseModel, EmailLoginTokenVerifyModel,
    LoginWithEmailTokenModel,
    ResendEmailModel, SignupResponseModel, VerifyEmailModel,
)
from app.schemas.user import SimpleUserResponseModel, UserCreate

router = APIRouter()


@router.post(
    "/signup",
    response_model=SignupResponseModel,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel
        }
    }
)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("Request: Signup -> Sign up request.")

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
            f"http://127.0.0.1:5173/auth/verify-email?email={db_user.email.address}&token="
            f"{db_user.email.token}"
        )

    return {
        "normalized_email": db_user.email.address,
        "detail": "Created account successfully! Please verify your email now."
    }


@router.post(
    "/resend-email",
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
            "description": "Email address not found."
        },
        202: {
            "model": {},
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

        send_verification_email(email)
    except NoResultFound:
        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                detail="Email address not found.",
                status_code=404,
            )

    return JSONResponse({
        "detail": "Verification code was resent."
    }, status_code=200)


@router.post(
    "/verify-email",
    response_model=SimpleUserResponseModel,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
        },
        202: {
            "model": SimpleUserResponseModel,
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

            return {
                "user": email.user,
                "detail": "Email has already been verified."
            }

        logger.info(f"Request: Verify Email -> Verifying email {email.address}.")
        verify_email(db, email=email, token=input_data.token)
        logger.info(
            f"Request: Verify Email -> Done verifying {email.address}. Returning credentials."
        )

        set_authentication_cookies(response, email.user)

        return {
            "user": email.user,
            "detail": "Email verified successfully!"
        }
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

    except EmailIncorrectTokenError:
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
    "/login/email-token",
    response_model=EmailLoginTokenResponseModel,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
        }
    }
)
async def login_with_email_token(
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

    logger.info(f"Request: Login with email token -> Email {email} not verified.")
    if not user.email.is_verified:
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
    "/login/email-token/verify",
    response_model=SimpleUserResponseModel,
    responses={
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

    if email_login := (await get_email_login_token_from_email(db, email=input_data.email)):
        try:
            is_valid = is_token_valid(
                db,
                instance=email_login,
                token=input_data.token,
                same_request_token=input_data.same_request_token
            )
        except EmailLoginTokenExpiredError:
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
        except EmailLoginTokenMaxTriesReachedError:
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
        except EmailLoginTokenSameRequestTokenInvalidError:
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
        else:
            if not is_valid:
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

            set_authentication_cookies(response, user)

            return {
                "user": user,
                "detail": "Logged in successfully!"
            }
    else:
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


@router.post(
    "/login/email-token/resend-email",
    response_model=SimpleDetailResponseModel,
    responses={
        404: {
            "model": HTTPBadRequestExceptionModel,
            "description": "No current email login token found. Please request one."
        }
    }
)
async def resend_email_login_token(
    input_data: EmailLoginResendMailModel,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Request: Resend Email Login Token: New Request for {input_data.email}."
    )

    if (email := await get_email_login_token_from_email(db, email=input_data.email)) is not None:
        logger.info(
            f"Request: Resend Email Login Token: Valid token for {input_data.email} found."
        )
        send_email_login_token(
            user=email.user,
            token=email.token,
        )

        return {
            "detail": "Login code was resent."
        }
    else:
        logger.info(
            f"Request: Resend Email Login Token: No token for {input_data.email} found."
        )
        raise HTTPException(
            status_code=404,
            detail="No current email login token found. Please request one.",
        )


@router.post(
    "/refresh",
    response_model=SimpleUserResponseModel,
)
async def refresh_token(
    response: Response,
    credentials: JwtAuthorizationCredentials = Security(refresh_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Refresh -> New Request to refresh JWT token.")

    user = get_user_by_id(db, credentials["id"])

    logger.info("Request: Refresh -> Returning new credentials.")

    set_authentication_cookies(response, user)

    return {
        "user": user,
        "detail": "Token refreshed successfully!"
    }


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
