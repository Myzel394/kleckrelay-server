from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.authentication.user_management import get_user_by_id
from app.database.dependencies import get_db
from app.schemas.user import User

router = APIRouter()


@router.get("/me", response_model=User)
def get_me(
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["user_id"])

    return user
