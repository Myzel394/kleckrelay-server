import enum

__all__ = [
    "StatusType"
]


class StatusType(str, enum.Enum):
    FORWARDING = "forwarding"
    BOUNCING = "bouncing"
