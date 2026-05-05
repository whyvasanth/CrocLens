from fastapi import APIRouter

from app.schemas.api import ActionPlanResponse
from app.services.mock_data import generate_action_plan, get_action_plan

router = APIRouter(prefix="/action-plans", tags=["action plans"])


@router.get("", response_model=ActionPlanResponse)
def read_action_plan() -> ActionPlanResponse:
    return get_action_plan()


@router.post("/generate", response_model=ActionPlanResponse)
def create_action_plan() -> ActionPlanResponse:
    return generate_action_plan()

