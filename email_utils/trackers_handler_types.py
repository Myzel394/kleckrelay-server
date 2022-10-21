from typing import Literal, Optional, TypedDict

__all__ = [
    "TrackerPattern",
    "TrackerData",
    "BlacklistData",
    "TrackerPattern",
    "TrackersJsonFile",
]


class TrackerPattern(TypedDict):
    pattern: str
    type: Literal["domain", "regex", "glob"]


class TrackerData(TypedDict):
    name: Optional[str]
    url: Optional[str]
    patterns: list[TrackerPattern]


class BlacklistData(TypedDict):
    blacklist: list[TrackerData]


class TrackersJsonFile(TypedDict):
    trackers: BlacklistData

