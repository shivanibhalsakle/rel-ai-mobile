from typing import Literal

from pydantic import BaseModel, Field


class BudgetBand(BaseModel):
    min: float = Field(ge=0)
    max: float = Field(ge=0)
    currency: str = "USD"
    period: Literal["month", "class"]


class WorkspaceNeeds(BaseModel):
    wifi: bool = False
    outlets: bool = False
    quiet: bool = False
    food: bool = False


class OnboardingRequest(BaseModel):
    activities: list[str] = []
    budgetBand: BudgetBand | None = None
    maxTravelMinutes: int | None = Field(default=None, ge=0, le=180)
    travelMode: Literal["walk", "bike", "transit", "drive"] | None = None
    minRating: float | None = Field(default=None, ge=0, le=5)
    workspaceNeeds: WorkspaceNeeds = WorkspaceNeeds()
    preferredWorkoutTimes: list[str] = []
    indoorOutdoorPreference: Literal["indoor", "outdoor", "either"] = "either"


class OnboardingResponse(BaseModel):
    status: str = "saved"
    preferencesId: str = "profile"