from pydantic import BaseModel

__all__ = [
    "SettingsModel",
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
    custom_alias_suffix_length: int
