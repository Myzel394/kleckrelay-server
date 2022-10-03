from fastapi import FastAPI

from . import constants, doctor
from .routes import routers

app = FastAPI()


@app.on_event("startup")
def show_information():
    if constants.IS_TESTING:
        return

    doctor.check_life_constants()


app.include_router(routers)

