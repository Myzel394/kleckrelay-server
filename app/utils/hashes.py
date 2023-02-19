from passlib.context import CryptContext

from app.constant_keys import FAST_HASH_SALT, SLOW_HASH_SALT

__all__ = [
    "hash_slowly",
    "hash_fast",
    "verify_slow_hash",
    "verify_fast_hash"
]

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_slowly(value: str) -> str:
    return pwd_context.hash(f"{value}#{SLOW_HASH_SALT}")


def hash_fast(value: str) -> str:
    return pwd_context.hash(f"{value}#{FAST_HASH_SALT}")


def verify_fast_hash(hashed_value: str, value: str) -> bool:
    return pwd_context.verify(f"{value}#{FAST_HASH_SALT}", hashed_value)


def verify_slow_hash(hashed_value: str, value: str) -> bool:
    return pwd_context.verify(f"{value}#{SLOW_HASH_SALT}", hashed_value)
