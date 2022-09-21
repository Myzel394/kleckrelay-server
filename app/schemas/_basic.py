from pydantic import BaseModel

__all__ = [
    "HTTPBadRequestExceptionModel",
    "HTTPNotFoundExceptionModel",
]


class HTTPBadRequestExceptionModel(BaseModel):
    detail: str


class HTTPNotFoundExceptionModel(BaseModel):
    item: str
