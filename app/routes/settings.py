from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import constants, life_constants, gpg_handler, logger
from app.controllers.server_statistics import get_server_statistics as \
    get_server_statistics_instance
from app.database.dependencies import get_db
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.settings import ServerStatisticsModel, SettingsModel

router = APIRouter()


@router.get("/settings", response_model=SettingsModel)
def get_settings():
    return {
        "mail_domain": life_constants.MAIL_DOMAIN,
        "app_domain": life_constants.APP_DOMAIN,
        "random_email_id_min_length": life_constants.RANDOM_EMAIL_ID_MIN_LENGTH,
        "random_email_id_chars": life_constants.RANDOM_EMAIL_ID_CHARS,
        "custom_alias_suffix_length": life_constants.CUSTOM_EMAIL_SUFFIX_LENGTH,
        "image_proxy_enabled": life_constants.ENABLE_IMAGE_PROXY,
        "image_proxy_life_time": life_constants.IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS,
        "disposable_emails_enabled": life_constants.USER_EMAIL_ENABLE_DISPOSABLE_EMAILS,
        "other_relays_enabled": life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS,
        "other_relay_domains": life_constants.USER_EMAIL_OTHER_RELAY_DOMAINS,
        "email_verification_chars": constants.EMAIL_VERIFICATION_TOKEN_CHARS,
        "email_verification_length": constants.EMAIL_VERIFICATION_TOKEN_LENGTH,
        "email_login_token_chars": life_constants.EMAIL_LOGIN_TOKEN_CHARS,
        "email_login_token_length": life_constants.EMAIL_LOGIN_TOKEN_LENGTH,
        "email_login_expiration_in_seconds": life_constants.EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS,
        "email_resend_wait_time": life_constants.EMAIL_RESEND_WAIT_TIME_IN_SECONDS,
        "instance_salt": life_constants.INSTANCE_SALT,
        "public_key": gpg_handler.SERVER_PUBLIC_KEY,
    }


@router.get(
    "/statistics",
    response_model=ServerStatisticsModel,
    responses={
        200: {
            "model": ServerStatisticsModel,
        },
        202: {
            "model": SimpleDetailResponseModel,
            "description": "Server statistics are disabled."
        }
    }
)
def get_server_statistics(
    response: Response,
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Server statistics -> New Request.")

    if not life_constants.ALLOW_STATISTICS:
        logger.info("Request: Get Server statistics -> Statistics disabled.")
        response.status_code = 204

        return {
            "detail": "Server statistics are disabled."
        }
    else:
        logger.info("Request: Get Server statistics -> Statistics enabled. Returning them.")
        statistics = get_server_statistics_instance(db)

        return {
            "sent_emails_amount": statistics.sent_emails_amount,
            "proxied_images_amount": statistics.proxied_images_amount,
            "expanded_urls_amount": statistics.expanded_urls_amount,
            "trackers_removed_amount": statistics.trackers_removed_amount,
            "users_amount": statistics.get_users_amount(db),
            "aliases_amount": statistics.get_aliases_amount(db),
            "app_version": constants.APP_VERSION,
            "launch_date": statistics.created_at,
        }
