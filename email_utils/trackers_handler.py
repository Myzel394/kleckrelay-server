import fnmatch
import json
import random
import re
import string
from typing import Optional
from urllib.parse import urlparse

from lxml import etree
from lxml.etree import _Element, XMLSyntaxError
from pyquery import PyQuery as pq

from app.constants import ROOT_DIR
from email_utils.trackers_handler_types import TrackerData, TrackerPattern, TrackersJsonFile

TRACKERS_PATH = ROOT_DIR / "assets" / "trackers.json"
tracker_data: TrackersJsonFile = json.loads(TRACKERS_PATH.read_text())


__all__ = [
    "check_pattern_matches",
    "check_pattern_matches",
    "remove_trackers",
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


def _generate_random_class() -> str:
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=50
        )
    )


def remove_trackers(html: str) -> str:
    try:
        d = pq(etree.fromstring(html))
    except XMLSyntaxError:
        return html

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]

        if check_is_url_a_tracker(source) is not None:
            image.getparent().remove(image)

    return d.html()
