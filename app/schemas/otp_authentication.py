from pydantic import BaseModel

__all__ = [
    "VerifyOTPAuthenticationModel"
]


class VerifyOTPAuthenticationModel(BaseModel):
    code: str
    cors_token: str
