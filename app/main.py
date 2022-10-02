from fastapi import FastAPI

from . import doctor
from .constants import get_is_testing
from .routes import routers

app = FastAPI()


@app.on_event("startup")
def show_information():
    if get_is_testing():
        return

    doctor.check_life_constants()


app.include_router(routers)

