from pydantic import BaseModel


DISCLAIMER = "CrocLens is educational software, not financial advice."


class PricePoint(BaseModel):
    date: str
    close: float


class QuoteResponse(BaseModel):
    symbol: str
    name: str
    price: float
    previous_close: float | None
    change: float | None
    change_percent: float | None
    currency: str
    day_high: float | None
    day_low: float | None
    volume: int | None
    market_cap: float | None
    data_as_of: str
    retrieved_at: str
    provider: str = "yfinance"
    is_sample_data: bool = False
    data_quality: str
    data_limitations: list[str]
    beginner_explanation: str
    educational_disclaimer: str = DISCLAIMER


class MarketHistoryResponse(BaseModel):
    symbol: str
    period: str
    points: list[PricePoint]
    provider: str = "yfinance"
    is_sample_data: bool = False
    data_quality: str
    data_limitations: list[str]
    educational_disclaimer: str = DISCLAIMER


class DemoHolding(BaseModel):
    symbol: str
    name: str
    quantity: float
    latest_price: float
    market_value: float
    allocation_percent: float
    note: str


class DemoPortfolioResponse(BaseModel):
    holdings: list[DemoHolding]
    total_value: float
    is_sample_data: bool = True
    data_quality: str = "demo"
    educational_disclaimer: str = DISCLAIMER


class GuideResponse(BaseModel):
    symbol: str
    summary: str
    observations: list[str]
    considerations: list[str]
    data_limitations: list[str]
    educational_disclaimer: str = DISCLAIMER
