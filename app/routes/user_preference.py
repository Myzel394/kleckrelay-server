from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.controllers.user import get_user_by_id
from app.controllers.user_preferences import update_user_preferences
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import EmailAlias, User
from app.schemas.user_preferences import UserPreferencesUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=None,
)
def update_user_preferences_api(
    update: UserPreferencesUpdate,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    update_user_preferences(
        db,
        preferences=user.preferences,
        update=update,
    )

    return {
        "detail": "Updated preferences successfully!"
    }
