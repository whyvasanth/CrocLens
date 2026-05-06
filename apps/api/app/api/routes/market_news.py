from fastapi import APIRouter

from app.schemas.api import MarketNewsImpactResponse
from app.services.market_news_service import get_market_news_impact

router = APIRouter(prefix="/market-news", tags=["market news"])


@router.get("/impact-summary", response_model=MarketNewsImpactResponse)
def read_market_news_impact() -> MarketNewsImpactResponse:
    return get_market_news_impact()
