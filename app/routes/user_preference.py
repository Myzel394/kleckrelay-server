from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app.authentication.handler import access_security
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.models import EmailAlias
from app.schemas.user_preferences import UserPreferencesUpdate

router = APIRouter()


@router.patch(
    "/",
    response_model=None,
)
def update_user_preferences(
    update: UserPreferencesUpdate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    update_data = update.dict(exclude_unset=True, exclude_none=True)
    update_data.pop("update_all_instances", None)

    for key, value in update_data.items():
        setattr(user.preferences, key, value)

    db.add(user.preferences)
    db.commit()
    db.refresh(user.preferences)

    if update.update_all_instances:
        alias_update = {
            name.split("_", 1)[1]: value
            for name, value in update_data.items()
            if value is not None
        }
        aliases = db.query(EmailAlias).filter_by(user_id=user.id).all()

        for alias in aliases:
            for key, value in alias_update.items():
                setattr(alias, f"pref_{key}", value)

            # Bulk update does not work
            db.add(alias)
            db.commit()
            db.refresh(alias)

    return {
        "detail": "Updated preferences successfully!"
    }
