from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import constants, doctor, life_constants
from .routes import routers

app = FastAPI()


@app.on_event("startup")
def show_information():
    if constants.IS_TESTING:
        return

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
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
