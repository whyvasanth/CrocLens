from fastapi import APIRouter, Query

from app.data_providers import get_data_provider_registry
from app.data_providers.schemas import NormalizedDataPoint, PriceHistoryResponse, TechnicalIndicatorResponse

router = APIRouter(tags=["market data"])


@router.get("/market/price/{symbol}", response_model=NormalizedDataPoint)
def read_market_price(symbol: str) -> NormalizedDataPoint:
    return get_data_provider_registry().get_market_price(symbol)


@router.get("/market/history/{symbol}", response_model=PriceHistoryResponse)
def read_market_history(symbol: str, period: str = Query(default="1mo", max_length=20)) -> PriceHistoryResponse:
    return get_data_provider_registry().get_price_history(symbol, period)


@router.get("/market/indicators/{symbol}", response_model=TechnicalIndicatorResponse)
def read_market_indicators(symbol: str) -> TechnicalIndicatorResponse:
    return get_data_provider_registry().get_technical_indicators(symbol)


@router.get("/crypto/price/{coin_id}", response_model=NormalizedDataPoint)
def read_crypto_price(coin_id: str) -> NormalizedDataPoint:
    return get_data_provider_registry().get_crypto_price(coin_id)


@router.get("/macro/series/{series_id}", response_model=NormalizedDataPoint)
def read_macro_series(series_id: str) -> NormalizedDataPoint:
    return get_data_provider_registry().get_macro_series(series_id)


@router.get("/rates/treasury", response_model=NormalizedDataPoint)
def read_treasury_rates() -> NormalizedDataPoint:
    return get_data_provider_registry().get_treasury_rates()
