from abc import ABC

__all__ = [
    "ModelPreference",
]


class ModelPreference(ABC):
    USER_FIELD = "user"
    FIELD_PREFIX = "pref_"

    @classmethod
    def _get_user_preference_prefix(cls) -> str:
        return cls.__name__.lower() + "_"

    def get_preference_value(self, name: str):
        if (value := getattr(self, name[:len(self.FIELD_PREFIX)], None)) is not None:
            return value

        user = getattr(self, self.USER_FIELD)

        return getattr(user, self._get_user_preference_prefix() + name)
