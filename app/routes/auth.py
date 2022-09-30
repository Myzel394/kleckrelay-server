from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.constants import get_is_testing
from app.controllers.email import get_email_by_address, verify_email
from app.authentication.email_login import (
    create_email_login_token,
    delete_email_login_token, get_email_login_token_from_email, is_token_valid,
)
from app.authentication.errors import (
    EmailIncorrectTokenError, EmailLoginTokenExpiredError,
    EmailLoginTokenMaxTriesReachedError, EmailLoginTokenSameRequestTokenInvalidError,
)
from app.authentication.handler import access_security, refresh_security
from app.authentication.user_management import (
    check_if_email_exists, create_user,
    get_user_by_email, get_user_by_id,
)
from app.database.dependencies import get_db
from app.life_constants import EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS
from app import logger
from app.schemas._basic import HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel
from app.schemas.authentication import (
    AuthenticationCredentialsResponseModel,
    EmailLoginTokenResponseModel, EmailLoginTokenVerifyModel, LoginWithEmailTokenModel,
    VerifyEmailModel,
)

from app.schemas.user import UserCreate

router = APIRouter()


@router.post(
    "/signup",
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
            detail="Email already in use.",
        )

    logger.info(f"Request: Signup -> Create user {user.email}.")
    await create_user(db, user=user)

    logger.info("Request: Signup -> Return Response.")

    return {}


@router.post(
    "/verify-email",
    response_model=AuthenticationCredentialsResponseModel,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
        },
        202: {
            "model": {},
        }
    }
)
def signup_verify_email(
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
            return JSONResponse(
                {},
                status_code=202,
            )

        logger.info(f"Request: Verify Email -> Verifying email {email.address}.")
        verify_email(db, email=email, token=input_data.token)
        logger.info(
            f"Request: Verify Email -> Done verifying {email.address}. Returning credentials."
        )

        return {
            "access_token": access_security.create_access_token(subject=email.user.to_jwt_object()),
            "refresh_token": refresh_security.create_refresh_token(subject=email.user.to_jwt_object()),
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
    "/login/email_token",
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
    }


@router.post(
    "/login/email_token/verify",
    response_model=AuthenticationCredentialsResponseModel,
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
            return {
                "access_token": access_security.create_access_token(subject=user.to_jwt_object()),
                "refresh_token": refresh_security.create_refresh_token(subject=user.to_jwt_object()),
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
    "/refresh",
    response_model=AuthenticationCredentialsResponseModel,
)
async def refresh_token(
    credentials: JwtAuthorizationCredentials = Security(refresh_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Refresh -> New Request to refresh JWT token.")

    user = get_user_by_id(db, credentials["id"])

    logger.info("Request: Refresh -> Returning new credentials.")
    return {
        "access_token": access_security.create_access_token(subject=user.to_jwt_object()),
        "refresh_token": refresh_security.create_refresh_token(subject=user.to_jwt_object()),
    }

