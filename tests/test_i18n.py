from app.i18n import translate as t
from app.models import LanguageType


def test_can_get_i18n():
    expected_message = "Welcome message"

    assert t("_test", "welcome", language=LanguageType.EN_US) == expected_message


def test_can_get_nested_i18n():
    expected_message = "Nested message"

    assert t("_test", "nested.deep", language=LanguageType.EN_US) == expected_message
