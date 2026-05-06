from fastapi import APIRouter

from app.schemas.api import RetirementPlanResponse
from app.services.retirement_service import get_retirement_plan

router = APIRouter(prefix="/retirement", tags=["retirement"])


@router.get("/plan", response_model=RetirementPlanResponse)
def read_retirement_plan() -> RetirementPlanResponse:
    return get_retirement_plan()
