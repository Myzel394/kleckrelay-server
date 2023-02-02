from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.admin import get_admin_users
from app.controllers.user import get_admin_user_by_id
from app.database.dependencies import get_db
from app.schemas.admin import AdminUsersResponseModel

router = APIRouter()


@router.get(
    "/users/",
    response_model=AdminUsersResponseModel,
)
def get_admin_users_api(
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Admins -> New Request.")

    # Validate user being an admin
    user = get_admin_user_by_id(db, credentials["id"])
    logger.info(f"Request: Get Admins -> User {user=} is an admin.")

    return {
        "users": get_admin_users(db)
    }
