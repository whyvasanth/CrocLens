from fastapi import APIRouter

from app.schemas.api import (
    OnboardingOptionsResponse,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
)
from app.services.onboarding_service import create_onboarding_profile, get_onboarding_options

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/options", response_model=OnboardingOptionsResponse)
def read_onboarding_options() -> OnboardingOptionsResponse:
    return get_onboarding_options()


@router.post("/profile", response_model=OnboardingProfileResponse)
def create_profile(profile: OnboardingProfileRequest) -> OnboardingProfileResponse:
    return create_onboarding_profile(profile)
