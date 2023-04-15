# Handlers return on what to do with an email. They check for example if an email has a tracker,
# a shortened url or if it has a footer.
import fnmatch
import json
import re
from typing import Optional
from urllib.parse import urlparse

from app.constants import ROOT_DIR
from .trackers_handler_types import TrackerData, TrackersJsonFile
from .url_shorteners_handler_types import ShortenerData, UrlShortenersJsonFile

TRACKERS_PATH = ROOT_DIR / "assets" / "trackers.json"
URL_SHORTENERS_PATH = ROOT_DIR / "assets" / "url-shorteners.json"
tracker_data: TrackersJsonFile = json.load(TRACKERS_PATH.open())
url_shorteners_data: UrlShortenersJsonFile = json.load(URL_SHORTENERS_PATH.open())


__all__ = [
    "check_pattern_matches",
    "check_is_url_a_tracker",
    "check_is_a_url_shortener",
]


def check_pattern_matches(url: str, pattern) -> bool:
    result = urlparse(url)

    if pattern['type'] == "domain":
        return result.hostname == pattern['pattern']
    elif pattern['type'] == "glob":
        return fnmatch.fnmatch(url, pattern['pattern'])
    elif pattern['type'] == "regex":
        return re.search(pattern['pattern'], url) is not None


def check_is_url_a_tracker(url: str) -> Optional[TrackerData]:
    blacklisted_trackers = tracker_data["trackers"]["blacklist"]

    for tracker in blacklisted_trackers:
        for pattern in tracker["patterns"]:
            if check_pattern_matches(url, pattern):
                return tracker


def check_is_a_url_shortener(url: str) -> Optional[ShortenerData]:
    url_shorteners = url_shorteners_data["shorteners"]["blacklist"]

    for shortener in url_shorteners:
        for pattern in shortener["patterns"]:
            if check_pattern_matches(url, pattern):
                return shortener
