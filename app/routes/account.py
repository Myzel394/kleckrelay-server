from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.account import update_account_data
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas.user import UserDetail, UserUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=UserDetail
)
def update_account_data_api(
    user_data: UserUpdate,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    update_account_data(
        db,
        user=user,
        data=user_data,
    )

    return user


@router.get(
    "/me",
    response_model=UserDetail
)
def get_me(
    user: User = Depends(get_user),
):
    return user
