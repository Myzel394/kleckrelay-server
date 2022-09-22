from app.life_constants import IS_DEBUG


def send_email_verification(address: str, token: str) -> None:
    if IS_DEBUG:
        print(f"Verification token for {address}: {token}")
