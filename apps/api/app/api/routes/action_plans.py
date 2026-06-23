from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import ActionPlanResponse, ActionPlanStatusResponse
from app.services.action_plan_service import (
    complete_action_plan_item,
    dismiss_action_plan_item,
    generate_action_plan_for_user,
    get_action_plan_for_user,
    reopen_action_plan_item,
)

router = APIRouter(prefix="/action-plans", tags=["action plans"])


@router.get("", response_model=ActionPlanResponse)
def read_action_plan(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> ActionPlanResponse:
    return get_action_plan_for_user(db, current_user)


@router.post("/generate", response_model=ActionPlanResponse)
def create_action_plan(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> ActionPlanResponse:
    return generate_action_plan_for_user(db, current_user)


@router.post("/items/{item_id}/complete", response_model=ActionPlanStatusResponse)
def complete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> ActionPlanStatusResponse:
    return complete_action_plan_item(db, current_user, item_id)


@router.post("/items/{item_id}/dismiss", response_model=ActionPlanStatusResponse)
def dismiss_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> ActionPlanStatusResponse:
    return dismiss_action_plan_item(db, current_user, item_id)


@router.post("/items/{item_id}/reopen", response_model=ActionPlanStatusResponse)
def reopen_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> ActionPlanStatusResponse:
    return reopen_action_plan_item(db, current_user, item_id)
