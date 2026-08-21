import pytest
from pydantic import ValidationError

from app.schemas.preferences import BudgetBand, OnboardingRequest, WorkspaceNeeds


def test_onboarding_request_defaults():
    request = OnboardingRequest()
    assert request.activities == []
    assert request.budgetBand is None
    assert request.indoorOutdoorPreference == "either"
    assert request.workspaceNeeds == WorkspaceNeeds()


def test_onboarding_request_full_payload():
    request = OnboardingRequest(
        activities=["gym", "yoga"],
        budgetBand=BudgetBand(min=10, max=50, period="month"),
        maxTravelMinutes=30,
        travelMode="walk",
        minRating=4.0,
        workspaceNeeds=WorkspaceNeeds(wifi=True, quiet=True),
        preferredWorkoutTimes=["morning"],
        indoorOutdoorPreference="indoor",
    )
    assert request.budgetBand.min == 10
    assert request.travelMode == "walk"


def test_max_travel_minutes_rejects_negative():
    with pytest.raises(ValidationError):
        OnboardingRequest(maxTravelMinutes=-5)


def test_max_travel_minutes_rejects_over_180():
    with pytest.raises(ValidationError):
        OnboardingRequest(maxTravelMinutes=181)


def test_min_rating_rejects_out_of_range():
    with pytest.raises(ValidationError):
        OnboardingRequest(minRating=5.5)
    with pytest.raises(ValidationError):
        OnboardingRequest(minRating=-1)


def test_travel_mode_rejects_invalid_value():
    with pytest.raises(ValidationError):
        OnboardingRequest(travelMode="teleport")


def test_indoor_outdoor_preference_rejects_invalid_value():
    with pytest.raises(ValidationError):
        OnboardingRequest(indoorOutdoorPreference="underwater")


def test_budget_band_rejects_negative_amounts():
    with pytest.raises(ValidationError):
        BudgetBand(min=-1, max=50, period="month")


def test_budget_band_rejects_invalid_period():
    with pytest.raises(ValidationError):
        BudgetBand(min=10, max=50, period="year")