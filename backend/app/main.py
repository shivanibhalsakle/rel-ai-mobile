from fastapi import FastAPI

from app.api.health import router
from app.api.me import router as me_router

app= FastAPI()
app.include_router(router, prefix="/v1")
app.include_router(me_router, prefix="/v1")