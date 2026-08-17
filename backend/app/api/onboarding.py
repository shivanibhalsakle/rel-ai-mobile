from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.preferences import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.post("/onboarding", response_model=OnboardingResponse)
async def submit_onboarding(
    preferences: OnboardingRequest,
    current_user: dict = Depends(get_current_user),
):
    return OnboardingResponse()