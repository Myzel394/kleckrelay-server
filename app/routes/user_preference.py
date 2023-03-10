from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.user_preferences import update_user_preferences
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, get_auth
from app.schemas.user_preferences import UserPreferencesUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=None,
)
def update_user_preferences_api(
    update: UserPreferencesUpdate,
    auth: AuthResult = Depends(get_auth()),
    db: Session = Depends(get_db),
):
    update_user_preferences(
        db,
        preferences=auth.user.preferences,
        update=update,
    )

    return {
        "detail": "Updated preferences successfully!"
    }
