from datetime import timedelta

from fastapi import FastAPI, Security, HTTPException
from fastapi_jwt import (
    JwtAccessBearerCookie,
    JwtAuthorizationCredentials,
    JwtRefreshBearer,
)

from app.life_constants import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, ACCESS_TOKEN_EXPIRE_IN_MINUTES, REFRESH_TOKEN_EXPIRE_IN_MINUTES

app = FastAPI()


access_security = JwtAccessBearerCookie(
    secret_key=JWT_SECRET_KEY,
    auto_error=False,
    access_expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES),
)
refresh_security = JwtRefreshBearer(
    secret_key=JWT_REFRESH_SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_IN_MINUTES),
)


@app.post("/auth")
def auth():
    # subject (actual payload) is any json-able python dict
    subject = {"username": "username", "role": "user"}

    # Create new access/refresh tokens pair
    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)

    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/auth/refresh")
def refresh(
        credentials: JwtAuthorizationCredentials = Security(refresh_security)
):
    access_token = access_security.create_access_token(subject=credentials.subject)
    refresh_token = refresh_security.create_refresh_token(subject=credentials.subject)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
