from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.guide import explain_quote
from app.market_data import InvalidSymbolError, MarketDataError, get_history, get_quote
from app.portfolio import get_demo_portfolio
from app.schemas import DemoPortfolioResponse, GuideResponse, MarketHistoryResponse, QuoteResponse


app = FastAPI(
    title="CrocLens API",
    description="Small API for the CrocLens beginner investment dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "croclens-api"}


@app.get("/api/quote/{symbol}", response_model=QuoteResponse)
async def quote(symbol: str) -> QuoteResponse:
    try:
        return await get_quote(symbol)
    except InvalidSymbolError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/history/{symbol}", response_model=MarketHistoryResponse)
async def history(
    symbol: str,
    period: str = Query(default="6mo", pattern="^(1mo|3mo|6mo|1y|5y)$"),
) -> MarketHistoryResponse:
    try:
        return await get_history(symbol, period)
    except InvalidSymbolError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/demo-portfolio", response_model=DemoPortfolioResponse)
async def demo_portfolio() -> DemoPortfolioResponse:
    return await get_demo_portfolio()


@app.get("/api/guide/{symbol}", response_model=GuideResponse)
async def guide(symbol: str) -> GuideResponse:
    try:
        quote_response = await get_quote(symbol)
    except InvalidSymbolError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return explain_quote(quote_response)
