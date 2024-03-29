from hashlib import pbkdf2_hmac

from . import life_constants

__all__ = [
    "SLOW_HASH_SALT",
    "FAST_HASH_SALT",
    "INSTANCE_SALT",
    "JWT_SECRET_KEY",
    "JWT_REFRESH_SECRET_KEY",
    "VERP_SECRET",
    "IMAGE_PROXY_SECRET",
]

SLOW_HASH_SALT = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:SLOW_HASH_SALT--u8brhn9XUv8jeisddsj",
    life_constants.KDF_ITERATIONS
).hex()
FAST_HASH_SALT = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:FAST_HASH_SALT--ah8bhzwxcJVesj98fDJ3f",
    life_constants.KDF_ITERATIONS
).hex()
INSTANCE_SALT = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:INSTANCE_SALT--UISDV9jv9ocjxvjde7893h5",
    life_constants.KDF_ITERATIONS
).hex()

JWT_SECRET_KEY = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:JWT_SECRET_KEY--CA8WJV2Uux6ch3lDVijkxc6",
    life_constants.KDF_ITERATIONS
).hex()

JWT_REFRESH_SECRET_KEY = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:JWT_REFRESH_SECRET_KEY--989sVXJjhmo8dj9ukhmeosjvph",
    life_constants.KDF_ITERATIONS
).hex()

VERP_SECRET = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:VERP_SECRET--JVDUihonseib3vwhrge87",
    life_constants.KDF_ITERATIONS
).hex()

IMAGE_PROXY_SECRET = pbkdf2_hmac(
    "sha256",
    life_constants.KLECK_SECRET.encode(),
    b"KLECKRELAY:IMAGE_PROXY_SECRET--uhevfIMUvbt8w4zh8nt7947t6698",
    life_constants.KDF_ITERATIONS
).hex()
