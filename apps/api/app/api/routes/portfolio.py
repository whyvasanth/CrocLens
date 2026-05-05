from fastapi import APIRouter

from app.schemas.api import PortfolioSummaryResponse
from app.services.mock_data import get_portfolio_summary

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummaryResponse)
def read_portfolio_summary() -> PortfolioSummaryResponse:
    return get_portfolio_summary()

