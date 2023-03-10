from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import logger
from app.controllers.account import update_account_data
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, get_auth
from app.dependencies.get_user import get_user
from app.dependencies.require_otp import require_otp_if_enabled
from app.models import User
from app.models.enums.api_key import APIKeyScope
from app.schemas.user import UserDetail, UserUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=UserDetail
)
def update_account_data_api(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(get_auth()),
):
    logger.info(f"Request: Update Account Data -> Update user={auth.user} with {user_data=}.")
    update_account_data(
        db,
        user=auth.user,
        data=user_data,
    )
    logger.info(f"Request: Update Account Data -> Updating successfully.")

    return auth.user


@router.get(
    "/me",
    response_model=UserDetail
)
def get_me(
    auth: AuthResult = Depends(get_auth(
        allow_api=True,
        api_key_scope=APIKeyScope.FULL_PROFILE,
    )),
):
    return auth.user
