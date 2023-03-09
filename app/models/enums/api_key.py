import enum

__all__ = [
    "APIKeyScope"
]


class APIKeyScope(str, enum.Enum):
    PROFILE_BASIC = "profile_basic"
    FULL_PROFILE = "full_profile"

    PREFERENCES_READ = "read:preferences"
    PREFERENCES_UPDATE = "update:preferences"

    ALIAS_READ = "read:alias"
    ALIAS_CREATE = "create:alias"
    ALIAS_UPDATE = "update:alias"
    ALIAS_DELETE = "delete:alias"

    REPORT_READ = "read:report"
    REPORT_DELETE = "delete:report"


