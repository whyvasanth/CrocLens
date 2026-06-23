from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import (
    DeleteRecordResponse,
    TaxInsightResponse,
    TaxLotCreateRequest,
    TaxLotResponse,
    TaxLotUpdateRequest,
)
from app.services.tax_service import create_tax_lot, delete_tax_lot, get_tax_insights, update_tax_lot

router = APIRouter(prefix="/tax", tags=["tax"])


@router.get("/insights", response_model=TaxInsightResponse)
def read_tax_insights(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> TaxInsightResponse:
    return get_tax_insights(db, current_user)


@router.post("/lots", response_model=TaxLotResponse)
def create_lot(
    request: TaxLotCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> TaxLotResponse:
    return create_tax_lot(db, current_user, request)


@router.put("/lots/{lot_id}", response_model=TaxLotResponse)
def update_lot(
    lot_id: str,
    request: TaxLotUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> TaxLotResponse:
    return update_tax_lot(db, current_user, lot_id, request)


@router.delete("/lots/{lot_id}", response_model=DeleteRecordResponse)
def delete_lot(
    lot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_tax_lot(db, current_user, lot_id)
