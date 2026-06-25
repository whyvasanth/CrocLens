from __future__ import annotations

import asyncio
import math
import re
from datetime import UTC, datetime
from typing import Any

import yfinance as yf

from app.config import settings
from app.guide import explain_quote
from app.schemas import MarketHistoryResponse, PricePoint, QuoteResponse

SYMBOL_RE = re.compile(r"^[A-Za-z0-9.\-]{1,12}$")
LIMITATIONS = [
    "yfinance is an unofficial third-party source and may be delayed or incomplete.",
    "Prices are latest available, not guaranteed real-time.",
    "CrocLens does not provide buy or sell recommendations.",
]


class MarketDataError(RuntimeError):
    pass


class InvalidSymbolError(MarketDataError):
    pass


def normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not SYMBOL_RE.match(normalized):
        raise InvalidSymbolError("Enter a valid stock or ETF ticker, such as VTI or AAPL.")
    return normalized


async def get_quote(symbol: str) -> QuoteResponse:
    normalized = normalize_symbol(symbol)
    return await _run_with_timeout(_fetch_quote, normalized)


async def get_history(symbol: str, period: str = "6mo") -> MarketHistoryResponse:
    normalized = normalize_symbol(symbol)
    return await _run_with_timeout(_fetch_history, normalized, period)


async def _run_with_timeout(func, *args):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args),
            timeout=settings.yfinance_timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        raise MarketDataError("Market data request timed out. Please try again.") from exc


def _fetch_quote(symbol: str) -> QuoteResponse:
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d", interval="1d", auto_adjust=False)
        if history is None or history.empty:
            raise InvalidSymbolError(f"No recent market data was found for {symbol}.")

        latest = history.iloc[-1]
        previous = history.iloc[-2] if len(history.index) > 1 else None
        info = _safe_info(ticker)

        price = _float_or_none(latest.get("Close"))
        previous_close = _float_or_none(previous.get("Close")) if previous is not None else _float_or_none(info.get("previousClose"))
        if price is None:
            raise InvalidSymbolError(f"No latest price was found for {symbol}.")

        change = price - previous_close if previous_close else None
        change_percent = (change / previous_close * 100) if change is not None and previous_close else None
        data_as_of = _format_index_date(history.index[-1])

        quote = QuoteResponse(
            symbol=symbol,
            name=info.get("longName") or info.get("shortName") or symbol,
            price=round(price, 2),
            previous_close=round(previous_close, 2) if previous_close else None,
            change=round(change, 2) if change is not None else None,
            change_percent=round(change_percent, 2) if change_percent is not None else None,
            currency=info.get("currency") or "USD",
            day_high=_rounded(latest.get("High")),
            day_low=_rounded(latest.get("Low")),
            volume=int(latest.get("Volume")) if _float_or_none(latest.get("Volume")) is not None else None,
            market_cap=_float_or_none(info.get("marketCap")),
            data_as_of=data_as_of,
            retrieved_at=datetime.now(tz=UTC).isoformat(),
            data_quality="latest_available",
            data_limitations=LIMITATIONS,
            beginner_explanation="",
        )
        quote.beginner_explanation = explain_quote(quote).summary
        return quote
    except InvalidSymbolError:
        raise
    except Exception as exc:
        raise MarketDataError("CrocLens could not retrieve market data right now.") from exc


def _fetch_history(symbol: str, period: str) -> MarketHistoryResponse:
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval="1d", auto_adjust=False)
        if history is None or history.empty:
            raise InvalidSymbolError(f"No historical prices were found for {symbol}.")

        points = [
            PricePoint(date=_format_index_date(index), close=round(float(row["Close"]), 2))
            for index, row in history.iterrows()
            if _float_or_none(row.get("Close")) is not None
        ]
        if not points:
            raise InvalidSymbolError(f"No usable historical prices were found for {symbol}.")

        return MarketHistoryResponse(
            symbol=symbol,
            period=period,
            points=points,
            data_quality="latest_available",
            data_limitations=LIMITATIONS,
        )
    except InvalidSymbolError:
        raise
    except Exception as exc:
        raise MarketDataError("CrocLens could not retrieve price history right now.") from exc


def _safe_info(ticker: Any) -> dict[str, Any]:
    try:
        return dict(ticker.get_info() or {})
    except Exception:
        return {}


def _float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) else number


def _rounded(value: Any) -> float | None:
    number = _float_or_none(value)
    return round(number, 2) if number is not None else None


def _format_index_date(value: Any) -> str:
    try:
        return value.date().isoformat()
    except AttributeError:
        return str(value)
