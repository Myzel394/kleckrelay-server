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
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.report import Report

router = APIRouter()


@router.get("/", response_model=Page[Report])
def get_reports(
    user: User = Depends(get_user),
    params: Params = Depends(),
):
    logger.info("Request: Get all Reports -> New Request.")

    return paginate(user.email_reports, params)


@router.get("/{id}", response_model=Report)
def get_report(
    id: uuid.UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Report -> New Request.")

    try:
        report = get_report_from_user_by_id(db, user=user, id=id)
    except NoResultFound:
        logger.info(f"Request: Get Report -> Report with {id=} not found.")
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )
    else:
        return report


@router.delete("/{id}", response_model=SimpleDetailResponseModel)
def delete_report_api(
    id: uuid.UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Delete Report -> Delete report with {id=}.")

    try:
        report = get_report_from_user_by_id(db, user=user, id=id)
        delete_report(db, report=report)
    except NoResultFound:
        logger.info(f"Request: Delete Report -> Report with {id=} not found.")
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return {
        "detail": "Deleted report successfully!",
    }
