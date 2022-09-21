from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authentication.email import get_email_by_address, verify_email
from app.authentication.email_login import (
    create_email_login_token,
    delete_email_login_token, get_email_login_token_from_email, is_token_valid,
)
from app.authentication.errors import (
    EmailIncorrectTokenError, EmailLoginTokenExpiredError,
    EmailLoginTokenMaxTriesReachedError, EmailLoginTokenSameRequestTokenInvalidError,
)
from app.authentication.handler import access_security, refresh_security
from app.authentication.user_management import check_if_email_exists, create_user, get_user_by_email
from app.database.dependencies import get_db
from app.life_constants import EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS
from app.schemas._basic import HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel
from app.schemas.authentication import EmailLoginTokenResponseModel, EmailLoginTokenVerifyModel, AuthenticationCredentialsResponseModel

from app.schemas.email import VerifyEmailModel
from app.schemas.user import UserCreate

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthenticationCredentialsResponseModel,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel
        }
    }
)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    if check_if_email_exists(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already in use.",
        )

    db_user = create_user(db, user=user)

    return {
        "user": db_user,
    }


@router.post(
    "/verify-email",
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
        }
    }
)
def signup_verify_email(input_data: VerifyEmailModel, db: Session = Depends(get_db)):
    default_error_message = "Email or token invalid."

    try:
        email = get_email_by_address(db, address=input_data.email)

        if email is None:
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

        verify_email(db, email=email, token=input_data.token)

        return {}
    except EmailIncorrectTokenError:
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
async def login_with_email_token(email: str, db: Session = Depends(get_db())):
    # No other error can occur, so we can simply return if the email doesn't exist
    if not check_if_email_exists(db, email):
        raise HTTPException(
            status_code=404,
            detail="Email not found."
        )

    user = get_user_by_email(db, email=email)

    if not user.email.is_verified:
        raise HttpException(
            status_code=400,
            detail="Your email has not been verified. Please verify it.",
        )

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
    db: Session = Depends(get_db()),
):
    default_error_message = "Email or token or same request token invalid."

    if email_login := get_email_login_token_from_email(db, email=input_data.email):
        try:
            is_valid = is_token_valid(
                db,
                instance=email_login,
                token=input_data.token,
                same_request_token=input_data.same_request_token
            )
        except EmailLoginTokenExpiredError:
            raise HTTPException(
                status_code=400,
                detail="Token expired. Please request a new one.",
            )
        except EmailLoginTokenMaxTriesReachedError:
            raise HTTPException(
                status_code=400,
                detail="Token exceeded. Please request a new one.",
            )
        except EmailLoginTokenSameRequestTokenInvalidError:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )
        else:
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=default_error_message,
                )

            user = email_login.user

            # Clean up the token
            delete_email_login_token(db, email_login)

            # Login user
            return {
                "user": user,
                "access_token": access_security.create_access_token(subject=user),
                "refresh_token": refresh_security.create_refresh_token(subject=user),
            }
    else:
        if EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS:
            raise HTTPException(
                status_code=404,
                detail="Email not found.",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=default_error_message,
            )

