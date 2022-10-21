from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
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
