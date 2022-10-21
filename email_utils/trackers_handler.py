import fnmatch
import json
import re
from typing import Optional
from urllib.parse import urlparse

from app.constants import ROOT_DIR
from email_utils.trackers_handler_types import TrackerData, TrackerPattern, TrackersJsonFile

TRACKERS_PATH = ROOT_DIR / "assets" / "trackers.json"
tracker_data: TrackersJsonFile = json.loads(TRACKERS_PATH.read_text())


__all__ = [
    "check_pattern_matches",
    "check_pattern_matches",
]


def check_pattern_matches(url: str, pattern: TrackerPattern) -> bool:
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
