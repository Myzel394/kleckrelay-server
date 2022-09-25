from fastapi import FastAPI

from .routes import routers
from . import doctor


app = FastAPI()


@app.on_event("startup")
def show_information():
    doctor.check_life_constants()


app.include_router(routers)

