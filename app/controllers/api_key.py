from sqlalchemy.orm import Session

from app.models import APIKey, User
from app.schemas.api_key import APIKeyCreateModel

__all__ = [
    "create_api_key",
]


def create_api_key(
    db: Session,
    /,
    data: APIKeyCreateModel,
    user: User,
) -> APIKey:
    key = APIKey(
        user_id=user.id,
        scopes=data.scopes,
        expires_at=data.expires_at,
    )

    db.add(key)
    db.commit()
    db.refresh(key)

    return key
