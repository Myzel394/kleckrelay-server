from app.models.user import User


def send_email_login_token(user: User, token: str) -> None:
    ...
