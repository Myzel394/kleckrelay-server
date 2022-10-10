from fastapi import APIRouter

from app import life_constants
from app.schemas.settings import SettingsModel

router = APIRouter()


@router.get("/", response_model=SettingsModel)
def get_settings():
    return {
        "mail_domain": life_constants.MAIL_DOMAIN,
        "random_email_id_min_length": life_constants.RANDOM_EMAIL_ID_MIN_LENGTH,
        "random_email_id_chars": life_constants.RANDOM_EMAIL_ID_CHARS,
        "image_proxy_enabled": life_constants.ENABLE_IMAGE_PROXY,
        "image_proxy_life_time": life_constants.IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS,
        "disposable_emails_enabled": life_constants.USER_EMAIL_ENABLE_DISPOSABLE_EMAILS,
        "other_relays_enabled": life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS,
        "other_relay_domains": life_constants.USER_EMAIL_OTHER_RELAY_DOMAINS,
    }