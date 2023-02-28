from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.user_preferences import update_user_preferences
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.dependencies.require_otp import require_otp_if_enabled
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
    __: bool = Depends(require_otp_if_enabled),
):
    update_user_preferences(
        db,
        preferences=user.preferences,
        update=update,
    )

    return {
        "detail": "Updated preferences successfully!"
    }
