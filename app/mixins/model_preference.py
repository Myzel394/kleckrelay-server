__all__ = [
    "ModelPreference",
]


class ModelPreference:
    USER_FIELD = "user"
    USER_PREFERENCES_FIELD = "preferences"
    FIELD_PREFIX = "pref_"

    @classmethod
    def _get_user_preference_prefix(cls) -> str:
        return cls.__name__.lower() + "_"

    def get_preference_value(self, name: str):
        if (value := getattr(self, f"pref_{name}", None)) is not None:
            return value

        user = getattr(self, self.USER_FIELD)
        preferences = getattr(user, self.USER_PREFERENCES_FIELD)

        return getattr(preferences, self._get_user_preference_prefix() + name)
