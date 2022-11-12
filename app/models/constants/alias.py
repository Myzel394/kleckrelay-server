from ..enums.alias import ProxyUserAgentType

__all__ = [
    "PROXY_USER_AGENT_STRING_MAP"
]


PROXY_USER_AGENT_STRING_MAP = {
    ProxyUserAgentType.FIREFOX:
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    ProxyUserAgentType.GOOGLE_MAIL:
        "Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)",
    ProxyUserAgentType.OUTLOOK_WINDOWS: 
        "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.15225; Pro)",
    ProxyUserAgentType.OUTLOOK_MACOS:
        "MacOutlook/16.61.22050700",
    ProxyUserAgentType.CHROME:
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/106.0.0.0 Safari/537.36",
    ProxyUserAgentType.APPLE_MAIL:
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/106.0.0.0 Safari/537.36",
}
