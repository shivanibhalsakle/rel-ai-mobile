from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.health import router
from app.api.me import router as me_router
from app.api.onboarding import router as onboarding_router

app= FastAPI()
app.include_router(router, prefix="/v1")
app.include_router(me_router, prefix="/v1")
app.include_router(onboarding_router, prefix="/v1")