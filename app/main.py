from fastapi import FastAPI

from .routes import routers


app = FastAPI()


app.include_router(routers)

