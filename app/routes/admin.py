from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import life_constants, logger
from app.controllers.admin import get_admin_users
from app.controllers.global_settings import get_settings, update_settings
from app.database.dependencies import get_db
from app.dependencies.get_user import get_admin_user
from app.models import User
from app.schemas.admin import AdminSettingsModel, AdminUsersResponseModel

router = APIRouter()


@router.get(
    "/users/",
    response_model=AdminUsersResponseModel,
)
def get_admin_users_api(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Admins -> New Request.")

    return {
        "users": get_admin_users(db)
    }


@router.get(
    "/settings/",
    response_model=AdminSettingsModel,
)
def get_settings_api(
    response: Response,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Admin Settings -> New Request.")

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
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Update Admin Settings -> New Request.")

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
