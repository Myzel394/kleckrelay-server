from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import gpg_handler
from app.controllers.user_preferences import update_user_preferences
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, get_auth
from app.models.enums.api_key import APIKeyScope
from app.schemas._basic import HTTPNotFoundExceptionModel
from app.schemas.user_preferences import FindPublicKeyResponseModel, UserPreferencesUpdate
from app.utils.email import normalize_email
from email_utils.web_key_discovery import find_public_key

router = APIRouter()


@router.patch(
    "/",
    response_model=None,
)
def update_user_preferences_api(
    update: UserPreferencesUpdate,
    auth: AuthResult = Depends(get_auth(
        allow_api=True,
        api_key_scope=APIKeyScope.PREFERENCES_UPDATE
    )),
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


@router.post(
    "/find-public-key",
    response_model=FindPublicKeyResponseModel,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
            "description": "No public key found for the email address."
        }
    }
)
async def find_public_key_api(
    auth: AuthResult = Depends(get_auth(
        allow_api=True,
        api_key_scope=APIKeyScope.PREFERENCES_UPDATE
    )),
):
    result = find_public_key(auth.user.email.address)

    if result is None:
        return JSONResponse({
            "detail": "No public key found for the email address."
        }, status_code=404)

    normalized_result_email = await normalize_email(result.raw_email)

    if normalized_result_email != auth.user.email.address:
        return JSONResponse({
            "detail": "No public key found for the email address."
        }, status_code=404)

    public_key = gpg_handler.get_public_key_from_fingerprint(result.fingerprint)

    return {
        "public_key": str(public_key),
        "type": result.type,
        "created_at": result.created_at
    }
