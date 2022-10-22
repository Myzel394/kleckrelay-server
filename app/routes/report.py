from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.email_report import get_report_by_id
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.report import Report

router = APIRouter()


@router.get("/", response_model=list[Report])
def get_reports(
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get all Reports -> New Request.")

    user = get_user_by_id(db, credentials["id"])

    return user.email_reports


@router.delete("/{id}", response_model=SimpleDetailResponseModel)
def delete_report(
    id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Delete Report -> Delete report with {id=}.")
    user = get_user_by_id(db, credentials["id"])

    try:
        report = get_report_by_id(db, id=id)
    except NoResultFound:
        logger.info(f"Request: Delete Report -> Report with {id=} not found.")
        raise HTTPException(
            status_code=404,
            detail="Alias not found."
        )
    else:
        db.delete(report)
        db.commit()

    return {
        "detail": "Deleted report successfully!",
    }
