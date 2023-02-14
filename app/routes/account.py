from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.controllers.account import update_account_data
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.schemas.user import SimpleUserResponseModel, UserUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=SimpleUserResponseModel
)
def update_account_data_api(
    user_data: UserUpdate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    update_account_data(
        db,
        user=user,
        data=user_data,
    )

    return {
        "user": user,
        "detail": "Updates user successfully!"
    }


@router.get(
    "/me",
    response_model=SimpleUserResponseModel,
)
def get_me(
        credentials: JwtAuthorizationCredentials = Security(access_security),
        db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    return {
        "user": user,
        "detail": "Returned user successfully!",
    }
