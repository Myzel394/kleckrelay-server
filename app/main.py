from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import constants, doctor, life_constants
from .controllers.server_statistics import get_server_statistics
from .database.dependencies import with_db
from .routes import routers

app = FastAPI()


@app.on_event("startup")
def show_information():
    if constants.IS_TESTING:
        return

    with with_db() as db:
        # Ensure statistics instance exists
        get_server_statistics(db)

    doctor.check_life_constants()


app.include_router(routers)

if life_constants.IS_DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
            f"http://{life_constants.MAIL_DOMAIN}:5173",
            f"http://{life_constants.API_DOMAIN}:5173",
            f"http://{life_constants.APP_DOMAIN}:5173",
            f"http://app.krl:5173"
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
