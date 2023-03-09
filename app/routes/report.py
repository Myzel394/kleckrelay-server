import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.controllers.email_report import (
    delete_report,
    get_report_from_user_by_id,
)
from app.database.dependencies import get_db
from app.dependencies.api_key_or_jwt import api_key_or_jwt
from app.dependencies.require_otp import require_otp_if_enabled
from app.models import User
from app.models.enums.api_key import APIKeyScope
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.report import Report

router = APIRouter()


@router.get("/", response_model=Page[Report])
def get_reports(
    user: User = Depends(api_key_or_jwt(APIKeyScope.REPORT_READ)),
    params: Params = Depends(),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info("Request: Get all Reports -> New Request.")

    return paginate(user.email_reports, params)


@router.get("/{id}", response_model=Report)
def get_report(
    id: uuid.UUID,
    user: User = Depends(api_key_or_jwt(APIKeyScope.REPORT_READ)),
    db: Session = Depends(get_db),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info("Request: Get Report -> New Request.")

    try:
        return get_report_from_user_by_id(db, user=user, id=id)
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )


@router.delete("/{id}", response_model=SimpleDetailResponseModel)
def delete_report_api(
    id: uuid.UUID,
    user: User = Depends(api_key_or_jwt(APIKeyScope.REPORT_DELETE)),
    db: Session = Depends(get_db),
    _: bool = Depends(require_otp_if_enabled),
):
    logger.info("Request: Delete Report -> New Request.")

    try:
        report= get_report_from_user_by_id(db, user=user, id=id)
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    logger.info(f"Request: Delete Report -> Delete report with {id=}.")

    delete_report(db, report=report)

    return {
        "detail": "Deleted report successfully!",
    }
