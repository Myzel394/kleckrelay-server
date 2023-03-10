import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app import life_constants
from app.models import APIKey, User
from app.schemas.api_key import APIKeyCreateModel
from app.utils.hashes import hash_fast, verify_fast_hash

__all__ = [
    "create_api_key",
    "find_api_key",
]


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
        label=data.label,
        hashed_key=hash_fast(key),
    )

    db.add(api_key_instance)
    db.commit()
    db.refresh(api_key_instance)

    return api_key_instance, key


def find_api_key(
    db: Session,
    key: str
) -> Optional[APIKey]:
    # Does someone have a better way to do this?
    all_keys = db.query(APIKey).filter(APIKey.expires_at > datetime.utcnow())

    for api_key in all_keys:
        if verify_fast_hash(api_key.hashed_key, key):
            return api_key
