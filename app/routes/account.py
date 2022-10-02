from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.authentication.user_management import get_user_by_id
from app.database.dependencies import get_db
from app.schemas.account import IsPasswordCorrectResponseModel, VerifyPasswordModel
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
