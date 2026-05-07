from datetime import UTC
from typing import Any

from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.errors import ProviderUnavailableError
from app.data_providers.schemas import NormalizedDataPoint, PriceHistoryPoint, PriceHistoryResponse


class YFinanceProvider(BaseDataProvider):
    provider_id = "yfinance"
    display_name = "Yahoo Finance via yfinance"
    source_type = "unofficial_market_data"
    capabilities = ["market_price", "price_history", "company_profile"]
    requires_api_key = False
    cost_note = "Free unofficial prototype source; not suitable as the sole production source."
    limitations = [
        "yfinance is an unofficial data access library and may change or rate-limit without notice.",
        "Prices can be delayed, adjusted, missing, or unavailable for some symbols.",
    ]

    def get_market_price(self, symbol: str) -> NormalizedDataPoint:
        yf = _load_yfinance()
        ticker = yf.Ticker(symbol.upper())

        try:
            fast_info = getattr(ticker, "fast_info", {}) or {}
            value = _read_fast_info(fast_info, "last_price") or _read_fast_info(fast_info, "lastPrice")
            currency = _read_fast_info(fast_info, "currency") or "USD"

            if value is None:
                history = ticker.history(period="5d")
                if history.empty:
                    raise ProviderUnavailableError(f"No yfinance price history returned for {symbol}.")
                value = float(history["Close"].dropna().iloc[-1])
                as_of = history.index[-1].to_pydatetime()
            else:
                history = ticker.history(period="5d")
                as_of = history.index[-1].to_pydatetime() if not history.empty else utc_now()
        except Exception as exc:
            raise ProviderUnavailableError(f"yfinance price lookup failed for {symbol}: {exc}") from exc

        if as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=UTC)

        return NormalizedDataPoint(
            provider=self.provider_id,
            source_type="market_price",
            asset_type="stock",
            symbol_or_series_id=symbol.upper(),
            value=float(value),
            currency=str(currency) if currency else "USD",
            as_of=as_of,
            retrieved_at=utc_now(),
            source_url=f"https://finance.yahoo.com/quote/{symbol.upper()}",
            freshness="prototype market data; verify before relying on it",
            confidence="medium",
            limitations=self.limitations,
        )

    def get_price_history(self, symbol: str, period: str = "1mo") -> PriceHistoryResponse:
        yf = _load_yfinance()
        ticker = yf.Ticker(symbol.upper())

        try:
            history = ticker.history(period=period)
        except Exception as exc:
            raise ProviderUnavailableError(f"yfinance history lookup failed for {symbol}: {exc}") from exc

        if history.empty:
            raise ProviderUnavailableError(f"No yfinance price history returned for {symbol}.")

        points: list[PriceHistoryPoint] = []
        for index, row in history.tail(90).iterrows():
            date = index.to_pydatetime()
            if date.tzinfo is None:
                date = date.replace(tzinfo=UTC)
            points.append(
                PriceHistoryPoint(
                    date=date,
                    open=_optional_float(row.get("Open")),
                    high=_optional_float(row.get("High")),
                    low=_optional_float(row.get("Low")),
                    close=float(row["Close"]),
                    volume=_optional_float(row.get("Volume")),
                )
            )

        as_of = points[-1].date
        return PriceHistoryResponse(
            provider=self.provider_id,
            asset_type="stock",
            symbol_or_series_id=symbol.upper(),
            currency="USD",
            as_of=as_of,
            retrieved_at=utc_now(),
            source_url=f"https://finance.yahoo.com/quote/{symbol.upper()}/history",
            freshness="prototype market data; verify before relying on it",
            confidence="medium",
            limitations=self.limitations,
            points=points,
        )


def _load_yfinance() -> Any:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ProviderUnavailableError("yfinance is not installed in this environment.") from exc
    return yf


def _read_fast_info(fast_info: Any, key: str) -> Any | None:
    if isinstance(fast_info, dict):
        return fast_info.get(key)
    return getattr(fast_info, key, None)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
