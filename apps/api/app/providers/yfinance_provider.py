from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Callable

from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderInvalidSymbolError, ProviderMalformedResponseError, ProviderUnavailableError
from app.providers.models import (
    CompanyProfile,
    CorporateAction,
    CorporateActionEvent,
    MarketHistory,
    MarketHistoryPoint,
    MarketQuote,
    utc_now,
)

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9^][A-Z0-9.\-=^]{0,19}$")
PERIOD_MAP = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "YTD": "ytd",
    "1Y": "1y",
    "5Y": "5y",
    "ALL": "max",
}


class YFinanceProvider(BaseProvider):
    name = "yfinance"
    display_name = "Yahoo Finance via yfinance"
    capabilities = ("quote", "history", "profile", "dividends", "splits")

    def __init__(
        self,
        *,
        enabled: bool,
        config: ProviderRuntimeConfig,
        ticker_factory: Callable[[str], Any] | None = None,
    ) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "yfinance is an unofficial third-party wrapper around Yahoo Finance data.",
                "Market data may be delayed, incomplete, adjusted, or unavailable.",
                "CrocLens labels this as educational context, not real-time trading data.",
            ],
        )
        self._ticker_factory = ticker_factory

    async def get_quote(self, symbol: str) -> MarketQuote:
        normalized_symbol = _normalize_symbol(symbol)
        cached = self.cache.get(f"quote:{normalized_symbol}")
        if isinstance(cached, MarketQuote):
            return cached

        self._ensure_available()
        try:
            quote = await self._call_sync(lambda: self._load_quote(normalized_symbol))
            self.cache.set(f"quote:{normalized_symbol}", quote)
            self._record_success()
            return quote
        except ProviderInvalidSymbolError:
            self._record_error("provider_invalid_symbol", f"{normalized_symbol} was not found.", retryable=False)
            raise
        except ProviderMalformedResponseError as exc:
            self._record_error("provider_malformed_response", str(exc))
            raise
        except Exception as exc:  # pragma: no cover - exact yfinance failures vary by version.
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError(f"yfinance could not retrieve {normalized_symbol}.") from exc

    async def get_history(self, symbol: str, period: str, interval: str) -> MarketHistory:
        normalized_symbol = _normalize_symbol(symbol)
        normalized_period = _normalize_period(period)
        normalized_interval = _normalize_interval(interval)
        cache_key = f"history:{normalized_symbol}:{normalized_period}:{normalized_interval}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, MarketHistory):
            return cached

        self._ensure_available()
        try:
            history = await self._call_sync(
                lambda: self._load_history(normalized_symbol, normalized_period, normalized_interval)
            )
            self.cache.set(cache_key, history)
            self._record_success()
            return history
        except (ProviderInvalidSymbolError, ProviderMalformedResponseError):
            self._record_error("provider_malformed_response", f"History was unavailable for {normalized_symbol}.")
            raise
        except Exception as exc:  # pragma: no cover
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError(f"yfinance history was unavailable for {normalized_symbol}.") from exc

    async def get_profile(self, symbol: str) -> CompanyProfile:
        normalized_symbol = _normalize_symbol(symbol)
        cached = self.cache.get(f"profile:{normalized_symbol}")
        if isinstance(cached, CompanyProfile):
            return cached

        self._ensure_available()
        try:
            profile = await self._call_sync(lambda: self._load_profile(normalized_symbol))
            self.cache.set(f"profile:{normalized_symbol}", profile)
            self._record_success()
            return profile
        except Exception as exc:  # pragma: no cover
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError(f"yfinance profile was unavailable for {normalized_symbol}.") from exc

    async def get_dividends(self, symbol: str) -> CorporateAction:
        return await self._load_corporate_action(symbol=symbol, action_type="dividend", attr_name="dividends")

    async def get_splits(self, symbol: str) -> CorporateAction:
        return await self._load_corporate_action(symbol=symbol, action_type="split", attr_name="splits")

    async def _load_corporate_action(self, *, symbol: str, action_type: str, attr_name: str) -> CorporateAction:
        normalized_symbol = _normalize_symbol(symbol)
        cache_key = f"{attr_name}:{normalized_symbol}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, CorporateAction):
            return cached

        self._ensure_available()
        try:
            result = await self._call_sync(
                lambda: self._build_corporate_action(normalized_symbol, action_type, attr_name)
            )
            self.cache.set(cache_key, result)
            self._record_success()
            return result
        except Exception as exc:  # pragma: no cover
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError(f"yfinance {attr_name} were unavailable for {normalized_symbol}.") from exc

    def _ticker(self, symbol: str) -> Any:
        if self._ticker_factory is not None:
            return self._ticker_factory(symbol)

        import yfinance as yf

        return yf.Ticker(symbol)

    def _load_quote(self, symbol: str) -> MarketQuote:
        ticker = self._ticker(symbol)
        fast_info = _as_dict(getattr(ticker, "fast_info", {}) or {})
        info = _as_dict(getattr(ticker, "info", {}) or {})
        price = _first_decimal(
            fast_info,
            info,
            keys=["last_price", "lastPrice", "regularMarketPrice", "currentPrice", "previousClose"],
        )
        if price is None:
            raise ProviderInvalidSymbolError(f"No quote price was returned for {symbol}.")

        retrieved_at = utc_now()
        return MarketQuote(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol,
            asset_type=_asset_type_from_quote(info),
            price=price,
            currency=str(fast_info.get("currency") or info.get("currency") or "USD"),
            change_percent=_change_percent(fast_info, info),
            data_as_of=retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://finance.yahoo.com/quote/{symbol}",
            data_limitations=self.data_limitations,
            raw_payload=_safe_raw({**fast_info, **{key: info.get(key) for key in ("quoteType", "shortName", "currency")}}),
        )

    def _load_history(self, symbol: str, period: str, interval: str) -> MarketHistory:
        ticker = self._ticker(symbol)
        frame = ticker.history(period=period, interval=interval, auto_adjust=False)
        if frame is None or getattr(frame, "empty", True):
            raise ProviderMalformedResponseError(f"No historical price rows were returned for {symbol}.")

        points: list[MarketHistoryPoint] = []
        for index, row in frame.iterrows():
            close = _decimal_from_any(row.get("Close"))
            if close is None:
                continue
            points.append(
                MarketHistoryPoint(
                    observed_at=_to_utc_datetime(index),
                    open=_decimal_from_any(row.get("Open")),
                    high=_decimal_from_any(row.get("High")),
                    low=_decimal_from_any(row.get("Low")),
                    close=close,
                    volume=_decimal_from_any(row.get("Volume")),
                )
            )

        if not points:
            raise ProviderMalformedResponseError(f"Historical price rows for {symbol} did not include close prices.")

        retrieved_at = utc_now()
        return MarketHistory(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol,
            asset_type="public_market",
            period=period,
            interval=interval,
            currency="USD",
            points=points,
            data_as_of=points[-1].observed_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://finance.yahoo.com/quote/{symbol}/history",
            data_limitations=self.data_limitations,
        )

    def _load_profile(self, symbol: str) -> CompanyProfile:
        ticker = self._ticker(symbol)
        info = _as_dict(getattr(ticker, "info", {}) or {})
        retrieved_at = utc_now()
        return CompanyProfile(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol,
            company_name=info.get("longName") or info.get("shortName"),
            exchange=info.get("exchange"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            website=info.get("website"),
            data_as_of=retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="low" if not info else "medium",
            source_url=f"https://finance.yahoo.com/quote/{symbol}/profile",
            data_limitations=self.data_limitations,
            raw_payload=_safe_raw({key: info.get(key) for key in ("longName", "shortName", "exchange", "sector", "industry")}),
        )

    def _build_corporate_action(self, symbol: str, action_type: str, attr_name: str) -> CorporateAction:
        ticker = self._ticker(symbol)
        series = getattr(ticker, attr_name, None)
        events: list[CorporateActionEvent] = []
        if series is not None:
            iterable = series.items() if hasattr(series, "items") else []
            for observed_at, value in iterable:
                decimal_value = _decimal_from_any(value)
                if decimal_value is not None:
                    events.append(CorporateActionEvent(observed_at=_to_utc_datetime(observed_at), value=decimal_value))

        retrieved_at = utc_now()
        return CorporateAction(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol,
            action_type=action_type,
            events=events,
            data_as_of=events[-1].observed_at if events else retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium" if events else "low",
            source_url=f"https://finance.yahoo.com/quote/{symbol}/history",
            data_limitations=self.data_limitations,
        )


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(normalized):
        raise ProviderInvalidSymbolError("Symbol must be 1-20 characters and contain only ticker-safe characters.")
    return normalized


def _normalize_period(period: str) -> str:
    normalized = period.strip().upper()
    if normalized not in PERIOD_MAP:
        raise ProviderInvalidSymbolError(f"Unsupported history period: {period}.")
    return PERIOD_MAP[normalized]


def _normalize_interval(interval: str) -> str:
    normalized = interval.strip().lower()
    allowed = {"1d", "1wk", "1mo"}
    if normalized not in allowed:
        raise ProviderInvalidSymbolError(f"Unsupported history interval: {interval}.")
    return normalized


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        return dict(value)
    except Exception:
        return {}


def _first_decimal(*payloads: dict[str, Any], keys: list[str]) -> Decimal | None:
    for payload in payloads:
        for key in keys:
            decimal_value = _decimal_from_any(payload.get(key))
            if decimal_value is not None:
                return decimal_value
    return None


def _decimal_from_any(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, float) and value != value:
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _change_percent(fast_info: dict[str, Any], info: dict[str, Any]) -> Decimal | None:
    direct = _first_decimal(info, keys=["regularMarketChangePercent"])
    if direct is not None:
        return direct
    current = _first_decimal(fast_info, info, keys=["last_price", "lastPrice", "regularMarketPrice", "currentPrice"])
    previous = _first_decimal(fast_info, info, keys=["previous_close", "previousClose"])
    if current is None or previous in (None, Decimal("0")):
        return None
    return ((current - previous) / previous * Decimal("100")).quantize(Decimal("0.01"))


def _asset_type_from_quote(info: dict[str, Any]) -> str:
    quote_type = str(info.get("quoteType") or "").upper()
    if quote_type == "ETF":
        return "etf"
    if quote_type in {"INDEX", "MUTUALFUND"}:
        return quote_type.lower()
    return "stock"


def _to_utc_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif hasattr(value, "to_pydatetime"):
        parsed = value.to_pydatetime()
    else:
        parsed = datetime.combine(value, datetime.min.time())
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _safe_raw(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if isinstance(value, str | int | float | bool) or value is None}
