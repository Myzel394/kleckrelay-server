from datetime import datetime

from pydantic import BaseModel

__all__ = [
    "SettingsModel",
    "ServerStatisticsModel"
]


class SettingsModel(BaseModel):
    mail_domain: str
    app_domain: str
    random_email_id_min_length: int
    random_email_id_chars: str
    image_proxy_enabled: bool
    image_proxy_life_time: int
    disposable_emails_enabled: bool
    other_relays_enabled: bool
    other_relay_domains: list[str]
    email_verification_chars: str
    email_verification_length: int
    email_login_token_chars: str
    email_login_token_length: int
    email_resend_wait_time: int
    email_login_expiration_in_seconds: int
    custom_alias_suffix_length: int
    instance_salt: str
    public_key: str


class ServerStatisticsModel(BaseModel):
    sent_emails_amount: int
    proxied_images_amount: int
    expanded_urls_amount: int
    trackers_removed_amount: int
    users_amount: int
    aliases_amount: int
    app_version: str
    launch_date: datetime
