from typing import TypedDict

__all__ = [
    "Quote",
    "FootersJsonFile",
]


class Quote(TypedDict):
    regex: str
    language: str


class FootersJsonFile(TypedDict):
    quotes: list[Quote]
