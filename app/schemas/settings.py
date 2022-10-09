from pydantic import BaseModel

__all__ = [
    "SettingsModel",
]


class SettingsModel(BaseModel):
    mail_domain: str
    random_email_id_min_length: int
    random_email_id_chars: str
    image_proxy_enabled: bool
    image_proxy_life_time: int
    disposable_emails_enabled: bool
    other_relays_enabled: bool
    other_relay_domains: list[str]
