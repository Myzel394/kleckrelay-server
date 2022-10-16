from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.controllers.user import get_user_by_id, set_password
from app.database.dependencies import get_db
from app.schemas.account import IsPasswordCorrectResponseModel, VerifyPasswordModel
from app.schemas.user import SimpleUserResponseModel, UserUpdate
from app.utils import verify_slow_hash

router = APIRouter()


@router.post(
    "/verify-password",
    response_model=IsPasswordCorrectResponseModel,
)
def verify_password(
    password_data: VerifyPasswordModel,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    return {
        "is_password_correct": verify_slow_hash(
            hashed_value=user.hashed_password,
            value=password_data.password,
        )
    }


@router.patch(
    "/",
    response_model=SimpleUserResponseModel
)
def update_account_data(
    user_data: UserUpdate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    update_data = user_data.dict(exclude_unset=True)

    if "password" in update_data:
        new_password = update_data.pop("password")

        set_password(user, new_password)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user": user,
        "detail": "Updates user successfully!"
    }

