from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import life_constants, logger
from app.authentication.handler import access_security
from app.controllers.admin import get_admin_users
from app.controllers.global_settings import get_settings, update_settings
from app.controllers.user import get_admin_user_by_id
from app.database.dependencies import get_db
from app.schemas.admin import AdminSettingsModel, AdminUsersResponseModel

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


@router.get(
    "/settings/",
    response_model=AdminSettingsModel,
)
def get_settings_api(
    response: Response,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Admin Settings -> New Request.")

    # Validate user being an admin
    user = get_admin_user_by_id(db, credentials["id"])
    logger.info(f"Request: Get Admin Settings -> User {user=} is an admin.")

    if not life_constants.USE_GLOBAL_SETTINGS:
        logger.info(
            "Request: Get Admin Settings -> Global settings are disabled. Returning error."
        )

        response.status_code = 204

        return {
            "detail": "Global settings are disabled."
        }

    logger.info("Request: Get Admin Settings -> Global settings are enabled. Returning settings.")
    return get_settings(db)


@router.patch(
    "/settings/",
    response_model=AdminSettingsModel,
)
def update_settings_api(
    response: Response,
    update_data: AdminSettingsModel,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Update Admin Settings -> New Request.")

    # Validate user being an admin
    user = get_admin_user_by_id(db, credentials["id"])
    logger.info(f"Request: Update Admin Settings -> User {user=} is an admin.")

    if not life_constants.USE_GLOBAL_SETTINGS:
        logger.info(
            "Request: Update Admin Settings -> Global settings are disabled. Returning error."
        )

        response.status_code = 204

        return {
            "detail": "Global settings are disabled."
        }

    # Update settings
    logger.info(f"Request: Update Admin Settings -> Updating settings with {update_data=}.")
    settings = update_settings(db, update_data)
    logger.info(f"Request: Update Admin Settings -> Success! Returning updated settings.")

    return settings
