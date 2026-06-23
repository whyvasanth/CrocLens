from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import (
    DeleteRecordResponse,
    RetirementAccountCreateRequest,
    RetirementAccountResponse,
    RetirementAccountUpdateRequest,
    RetirementPlanResponse,
)
from app.services.retirement_service import (
    create_retirement_account,
    delete_retirement_account,
    get_retirement_plan,
    update_retirement_account,
)

router = APIRouter(prefix="/retirement", tags=["retirement"])


@router.get("/plan", response_model=RetirementPlanResponse)
def read_retirement_plan(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> RetirementPlanResponse:
    return get_retirement_plan(db, current_user)


@router.post("/accounts", response_model=RetirementAccountResponse)
def create_account(
    request: RetirementAccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> RetirementAccountResponse:
    return create_retirement_account(db, current_user, request)


@router.put("/accounts/{account_id}", response_model=RetirementAccountResponse)
def update_account(
    account_id: str,
    request: RetirementAccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> RetirementAccountResponse:
    return update_retirement_account(db, current_user, account_id, request)


@router.delete("/accounts/{account_id}", response_model=DeleteRecordResponse)
def delete_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_retirement_account(db, current_user, account_id)
