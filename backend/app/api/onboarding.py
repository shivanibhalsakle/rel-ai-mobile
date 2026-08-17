from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.db.preferences_repository import get_preferences, save_preferences
from app.schemas.preferences import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.post("/onboarding", response_model=OnboardingResponse)
async def submit_onboarding(
    preferences: OnboardingRequest,
    current_user: dict = Depends(get_current_user),
):
    save_preferences(current_user["uid"], preferences)
    return OnboardingResponse()

@router.get("/onboarding")
async def read_onboarding(current_user: dict = Depends(get_current_user)):
    preferences = get_preferences(current_user["uid"])
    if preferences is None:
        return {"onboardingCompleted": False}
    return {"onboardingCompleted": True, "preferences": preferences}