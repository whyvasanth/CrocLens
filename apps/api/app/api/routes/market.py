from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_provider_registry
from app.db.session import get_db
from app.providers.registry import ProviderRegistry
from app.schemas.api import MarketHistoryResponse, MarketQuoteResponse, MarketSnapshotResponse
from app.services.market_api_service import (
    get_market_history_response,
    get_market_quote_response,
    get_market_snapshot_response,
)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/snapshot", response_model=MarketSnapshotResponse)
def read_market_snapshot() -> MarketSnapshotResponse:
    return get_market_snapshot_response()


@router.get("/quotes/{symbol}", response_model=MarketQuoteResponse)
async def read_market_quote(
    symbol: str,
    db: Session = Depends(get_db),
    registry: ProviderRegistry = Depends(get_provider_registry),
) -> MarketQuoteResponse:
    return await get_market_quote_response(db, registry, symbol)


@router.get("/history/{symbol}", response_model=MarketHistoryResponse)
async def read_market_history(
    symbol: str,
    period: str = "1M",
    interval: str = "1d",
    db: Session = Depends(get_db),
    registry: ProviderRegistry = Depends(get_provider_registry),
) -> MarketHistoryResponse:
    return await get_market_history_response(db, registry, symbol, period, interval)
