from app import gpg_handler

PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

xjMEY1BWURYJKwYBBAHaRw8BAQdAF7V3c/or1pqMSO+K1NdlTzX8M3OWMIsM
fRaXjBpKcfrNG0pvbiBTbWl0aCA8am9uQGV4YW1wbGUuY29tPsKMBBAWCgA+
BQJjUFZRBAsJBwgJEPYcYW9Bd+RzAxUICgQWAAIBAhkBAhsDAh4BFiEEoXES
0EdOGluYpuHr9hxhb0F35HMAAHPbAQDKUYRKK4fBmx0oY51NFngIWlgh37r2
jh43FGyEfPtiiAD/ar4x4hYdzdTgstCd5IgHGN0rHePn8buFQ+BTclK3UwjO
OARjUFZREgorBgEEAZdVAQUBAQdAfNbp3wadPhBZd8PA0RuQbsWLQMkKozDF
x/vu1H34bQQDAQgHwngEGBYIACoFAmNQVlEJEPYcYW9Bd+RzAhsMFiEEoXES
0EdOGluYpuHr9hxhb0F35HMAAPaXAP90baEdk1ughlSfxwr1/qdXYasj4eXD
CY/XrzMgKvnwawEAtMHyvho1Les1B+7jJsKpNmOjssHIbDSeWTc0Dl8hugc=
=/9/F
-----END PGP PUBLIC KEY BLOCK-----"""

# Shoutout to all the bots, that will try to use this key...
PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----

xVgEY1BWURYJKwYBBAHaRw8BAQdAF7V3c/or1pqMSO+K1NdlTzX8M3OWMIsM
fRaXjBpKcfoAAP972BDfdV6zN7A5A7OzI/ECaSHO87ucPJWDAMDfSwXN+xET
zRtKb24gU21pdGggPGpvbkBleGFtcGxlLmNvbT7CjAQQFgoAPgUCY1BWUQQL
CQcICRD2HGFvQXfkcwMVCAoEFgACAQIZAQIbAwIeARYhBKFxEtBHThpbmKbh
6/YcYW9Bd+RzAABz2wEAylGESiuHwZsdKGOdTRZ4CFpYId+69o4eNxRshHz7
YogA/2q+MeIWHc3U4LLQneSIBxjdKx3j5/G7hUPgU3JSt1MIx10EY1BWURIK
KwYBBAGXVQEFAQEHQHzW6d8GnT4QWXfDwNEbkG7Fi0DJCqMwxcf77tR9+G0E
AwEIBwAA/06+/xPfxIBx3ZjycwACRpIlL/2+dTKwZOpn7T7IX60oEafCeAQY
FggAKgUCY1BWUQkQ9hxhb0F35HMCGwwWIQShcRLQR04aW5im4ev2HGFvQXfk
cwAA9pcA/3RtoR2TW6CGVJ/HCvX+p1dhqyPh5cMJj9evMyAq+fBrAQC0wfK+
GjUt6zUH7uMmwqk2Y6OywchsNJ5ZNzQOXyG6Bw==
=sw6M
-----END PGP PRIVATE KEY BLOCK-----"""


def test_can_sign():
    message = str(gpg_handler.sign_message("hello"))
    assert message.startswith("-----BEGIN PGP SIGNED MESSAGE-----")


def test_can_encrypt():
    message = str(gpg_handler.encrypt_message("hello", public_key_in_str=PUBLIC_KEY))
    assert message.startswith("-----BEGIN PGP MESSAGE-----")
