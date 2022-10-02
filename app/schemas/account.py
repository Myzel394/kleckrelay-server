from pydantic import BaseModel

__all__ = [
    "VerifyPasswordModel",
    "IsPasswordCorrectResponseModel",
]


class VerifyPasswordModel(BaseModel):
    password: str


class IsPasswordCorrectResponseModel(BaseModel):
    is_password_correct: bool
