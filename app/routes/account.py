from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import logger
from app.controllers.account import update_account_data
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, AuthResultMethod, get_auth
from app.models.enums.api_key import APIKeyScope
from app.schemas.user import UserDetail, UserDetailWithoutPreferences, UserUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=UserDetail
)
def update_account_data_api(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(get_auth(
        allow_api=True,
        api_key_scope=APIKeyScope.PROFILE_UPDATE,
    )),
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
    response_model=Union[UserDetail, UserDetailWithoutPreferences]
)
def get_me(
    auth: AuthResult = Depends(get_auth(
        allow_api=True,
        api_key_scope=APIKeyScope.PROFILE_READ,
    )),
):
    if auth.method == AuthResultMethod.JWT or APIKeyScope.PREFERENCES_READ in auth.api_key.scopes:
        return UserDetail.from_orm(auth.user)
    else:
        return UserDetailWithoutPreferences.from_orm(auth.user)
