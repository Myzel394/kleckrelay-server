import secrets

from sqlalchemy.orm import Session

from app import life_constants
from app.models import APIKey, User
from app.schemas.api_key import APIKeyCreateModel

__all__ = [
    "create_api_key",
]

from app.utils.hashes import hash_fast


def _generate_key() -> str:
    return "".join(
        secrets.choice(life_constants.API_KEY_CHARS)
        for _ in range(life_constants.API_KEY_LENGTH)
    )


def create_api_key(
    db: Session,
    /,
    data: APIKeyCreateModel,
    user: User,
) -> tuple[APIKey, str]:
    key = _generate_key()
    api_key_instance = APIKey(
        user_id=user.id,
        scopes=data.scopes,
        expires_at=data.expires_at,
        hashed_key=hash_fast(key),
    )

    db.add(api_key_instance)
    db.commit()
    db.refresh(api_key_instance)

    return api_key_instance, key
