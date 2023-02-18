from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, Response

from app import life_constants, logger
from app.controllers.admin import get_admin_users
from app.controllers.cron_report import get_latest_cron_report
from app.controllers.global_settings import get_settings, update_settings
from app.database.dependencies import get_db
from app.dependencies.get_user import get_admin_user
from app.models import User
from app.schemas.admin import (
    AdminGlobalSettingsDisabledResponseModel, AdminSettingsModel,
    AdminUsersResponseModel,
)
from app.schemas.cron_report import CronReportResponseModel

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
    responses={
        202: {
            "description": "Global settings are disabled.",
            "model": AdminGlobalSettingsDisabledResponseModel,
        },
    }
)
def get_settings_api(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Admin Settings -> New Request.")

    if not life_constants.USE_GLOBAL_SETTINGS:
        logger.info(
            "Request: Get Admin Settings -> Global settings are disabled. Returning error."
        )

        return JSONResponse({
            "detail": "Global settings are disabled.",
            "code": "error:settings:global_settings_disabled"
        }, status_code=202)

    logger.info("Request: Get Admin Settings -> Global settings are enabled. Returning settings.")
    return get_settings(db)


@router.patch(
    "/settings/",
    response_model=AdminSettingsModel,
    responses={
        202: {
            "description": "Global settings are disabled.",
            "model": AdminGlobalSettingsDisabledResponseModel,
        },
    }
)
def update_settings_api(
    update_data: AdminSettingsModel,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Update Admin Settings -> New Request.")

    if not life_constants.USE_GLOBAL_SETTINGS:
        logger.info(
            "Request: Update Admin Settings -> Global settings are disabled. Returning error."
        )

        return JSONResponse({
            "detail": "Global settings are disabled.",
            "code": "error:settings:global_settings_disabled"
        }, status_code=202)

    # Update settings
    logger.info(f"Request: Update Admin Settings -> Updating settings with {update_data=}.")
    settings = update_settings(db, update_data)
    logger.info(f"Request: Update Admin Settings -> Success! Returning updated settings.")

    return settings


@router.get("/cron-report/latest/", response_model=CronReportResponseModel)
def get_cron_jobs(
    user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Cron Jobs -> New Request.")

    report = get_latest_cron_report(db)
    logger.info(f"Request: Get Cron Jobs -> Latest report is {report=}.")

    response_data = CronReportResponseModel.from_orm(report, user_id=user.id)
    logger.info(f"Request: Get Cron Jobs -> Returning data.")

    return response_data
