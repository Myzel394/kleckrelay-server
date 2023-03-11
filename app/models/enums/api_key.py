import enum

__all__ = [
    "APIKeyScope"
]


class APIKeyScope(str, enum.Enum):
    PROFILE_READ = "read:profile"
    PROFILE_UPDATE = "update:profile"

    PREFERENCES_READ = "read:preferences"
    PREFERENCES_UPDATE = "update:preferences"

    ALIAS_READ = "read:alias"
    ALIAS_CREATE = "create:alias"
    ALIAS_UPDATE = "update:alias"
    ALIAS_DELETE = "delete:alias"

    REPORT_READ = "read:report"
    REPORT_DELETE = "delete:report"

    ADMIN_CRON_REPORT_READ = "read:admin_cron_report"
    ADMIN_SETTINGS_READ = "read:admin_settings"
    ADMIN_SETTINGS_UPDATE = "update:admin_settings"

    ADMIN_RESERVED_ALIAS_READ = "read:admin_reserved_alias"
    ADMIN_RESERVED_ALIAS_CREATE = "create:admin_reserved_alias"
    ADMIN_RESERVED_ALIAS_UPDATE = "update:admin_reserved_alias"
    ADMIN_RESERVED_ALIAS_DELETE = "delete:admin_reserved_alias"
