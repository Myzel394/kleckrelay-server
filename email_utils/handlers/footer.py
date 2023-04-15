import enum
import json
from dataclasses import dataclass
from typing import Optional

from app.constants import ROOT_DIR, EMAIL_QUOTE_REGEX
from email_utils.handlers.footers_handler_types import FootersJsonFile

FOOTERS_PATH = ROOT_DIR / "assets" / "trackers.json"
footers_data: FootersJsonFile = json.load(FOOTERS_PATH.open())


class FragmentType(str, enum.Enum):
    REPLY = "reply"
    FORWARD = "forward"
    CONTENT = "content"


@dataclass
class Fragment:
    """A `Fragment` is a part of an email message that contains a footer part.
    """
    start_line: int
    end_line: int
    type: FragmentType
    lines: list[str]


def is_quote_header(line: str) -> bool:
    return ...


def should_create_new_fragment(
    fragment: Fragment,
    line: str,
    is_quote: bool,
) -> bool:
    return (
        is_quote and fragment.type == FragmentType.CONTENT
        or is_quote_header(line)
        or line == ""
    )


def find_fragments(content: str) -> list[Fragment]:
    lines = reversed(content.splitlines())

    fragments = []
    current_fragment: Optional[Fragment] = None

    for raw_line in lines:
        line = raw_line.strip()

        is_quote = EMAIL_QUOTE_REGEX.match(line) is not None
