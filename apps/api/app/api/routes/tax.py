from fastapi import APIRouter

from app.schemas.api import TaxInsightResponse
from app.services.tax_service import get_tax_insights

router = APIRouter(prefix="/tax", tags=["tax"])


@router.get("/insights", response_model=TaxInsightResponse)
def read_tax_insights() -> TaxInsightResponse:
    return get_tax_insights()
