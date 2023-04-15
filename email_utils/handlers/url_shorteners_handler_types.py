from typing import Literal, Optional, TypedDict

__all__ = [
    "BlacklistData",
    "ShortenerPattern",
    "ShortenerData",
    "UrlShortenersJsonFile",
]


class ShortenerPattern(TypedDict):
    pattern: str
    type: Literal["domain"]


class ShortenerData(TypedDict):
    name: Optional[str]
    url: Optional[str]
    patterns: list[ShortenerPattern]


class BlacklistData(TypedDict):
    blacklist: list[ShortenerData]


class UrlShortenersJsonFile(TypedDict):
    shorteners: BlacklistData

