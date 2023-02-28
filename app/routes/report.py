from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.orm import Session

from app import logger
from app.controllers.email_report import (
    delete_report,
    get_report_from_user_by_id,
)
from app.database.dependencies import get_db
from app.dependencies.get_instance_from_user import get_instance_from_user
from app.dependencies.get_user import get_user
from app.dependencies.require_otp import require_otp_if_enabled
from app.models import EmailReport, User
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.report import Report

router = APIRouter()


@router.get("/", response_model=Page[Report])
def get_reports(
    user: User = Depends(get_user),
    params: Params = Depends(),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info("Request: Get all Reports -> New Request.")

    return paginate(user.email_reports, params)


@router.get("/{id}", response_model=Report)
def get_report(
    report: EmailReport = Depends(get_instance_from_user(get_report_from_user_by_id)),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info("Request: Get Report -> New Request.")
    return report


@router.delete("/{id}", response_model=SimpleDetailResponseModel)
def delete_report_api(
    report: EmailReport = Depends(get_instance_from_user(get_report_from_user_by_id)),
    db: Session = Depends(get_db),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info(f"Request: Delete Report -> Delete report with {id=}.")

    delete_report(db, report=report)

    return {
        "detail": "Deleted report successfully!",
    }
