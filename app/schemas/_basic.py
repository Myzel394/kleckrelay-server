from pydantic import BaseModel

__all__ = [
    "HTTPBadRequestExceptionModel",
    "HTTPNotFoundExceptionModel",
    "SimpleDetailResponseModel",
]


class HTTPBadRequestExceptionModel(BaseModel):
    detail: str


class HTTPNotFoundExceptionModel(BaseModel):
    item: str


class SimpleDetailResponseModel(BaseModel):
    detail: str
