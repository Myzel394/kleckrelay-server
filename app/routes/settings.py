from fastapi import APIRouter

from app import constants, life_constants
from app.schemas.settings import SettingsModel

router = APIRouter()


@router.get("/", response_model=SettingsModel)
def get_settings():
    return {
        "mail_domain": life_constants.MAIL_DOMAIN,
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
        "email_resend_wait_time": life_constants.EMAIL_RESEND_WAIT_TIME_IN_SECONDS,
    }
