import enum

__all__ = [
    "AliasType",
    "ImageProxyFormatType",
    "ProxyUserAgentType",
]


class AliasType(str, enum.Enum):
    RANDOM = "random"
    CUSTOM = "custom"


class ImageProxyFormatType(str, enum.Enum):
    WEBP = "webp"
    PNG = "png"
    JPEG = "jpeg"

    def __str__(self) -> str:
        return str(self.value).split(".")[-1]


class ProxyUserAgentType(str, enum.Enum):
    APPLE_MAIL = "apple-mail"
    GOOGLE_MAIL = "google-mail"
    OUTLOOK_WINDOWS = "outlook-windows"
    OUTLOOK_MACOS = "outlook-macos"
    FIREFOX = "firefox"
    CHROME = "chrome"
