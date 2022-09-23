from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas._basic import HTTPBadRequestExceptionModel
from app.schemas.alias import Alias, AliasCreate

router = APIRouter()

@router.post(
    "/create",
    response_model=Alias,
    responses={
        400: {
            "model": HTTPBadRequestExceptionModel,
        }
    }
)
def create_alias(
    alias_data: AliasCreate,
    db: Session = Depends(get_db),
):

