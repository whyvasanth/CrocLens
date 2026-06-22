from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderInvalidSymbolError, ProviderMalformedResponseError, ProviderRateLimitError, ProviderUnavailableError
from app.providers.models import MarketHistory, MarketHistoryPoint, MarketQuote, utc_now

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COIN_ID_BY_ALIAS = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "sol": "solana",
    "solana": "solana",
    "ada": "cardano",
    "cardano": "cardano",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
}
HISTORY_DAYS_BY_PERIOD = {
    "1D": "1",
    "5D": "5",
    "1M": "30",
    "3M": "90",
    "6M": "180",
    "YTD": "365",
    "1Y": "365",
    "5Y": "1825",
    "ALL": "max",
}


class CoinGeckoProvider(BaseProvider):
    name = "coingecko"
    display_name = "CoinGecko public crypto API"
    capabilities = ("crypto_price", "history")

    def __init__(
        self,
        *,
        enabled: bool,
        config: ProviderRuntimeConfig,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "CoinGecko public endpoints are rate limited and may be unavailable during local testing.",
                "Crypto prices are volatile and may not be real-time.",
                "Only a small allowlisted set of common crypto identifiers is supported in the MVP.",
            ],
        )
        self._client = client

    async def get_crypto_price(self, coin_id: str) -> MarketQuote:
        normalized_coin_id = _normalize_coin_id(coin_id)
        cache_key = f"crypto_price:{normalized_coin_id}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, MarketQuote):
            return cached

        self._ensure_available()
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": normalized_coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_last_updated_at": "true",
        }
        payload = await self._get_json(url, params=params)
        coin_payload = payload.get(normalized_coin_id)
        if not isinstance(coin_payload, dict) or "usd" not in coin_payload:
            self._record_error("provider_malformed_response", f"CoinGecko did not return USD price for {normalized_coin_id}.")
            raise ProviderMalformedResponseError(f"CoinGecko did not return USD price for {normalized_coin_id}.")

        retrieved_at = utc_now()
        quote = MarketQuote(
            provider_name=self.name,
            provider_status="healthy",
            symbol=normalized_coin_id,
            asset_type="crypto",
            price=_decimal_from_any(coin_payload.get("usd")),
            currency="USD",
            change_percent=_decimal_from_any(coin_payload.get("usd_24h_change")),
            data_as_of=_epoch_to_datetime(coin_payload.get("last_updated_at")) or retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://www.coingecko.com/en/coins/{normalized_coin_id}",
            data_limitations=self.data_limitations,
            raw_payload=_safe_raw(coin_payload),
        )
        self.cache.set(cache_key, quote)
        self._record_success()
        return quote

    async def get_history(self, symbol: str, period: str, interval: str) -> MarketHistory:
        normalized_coin_id = _normalize_coin_id(symbol)
        normalized_period = period.strip().upper()
        if normalized_period not in HISTORY_DAYS_BY_PERIOD:
            raise ProviderInvalidSymbolError(f"Unsupported crypto history period: {period}.")
        cache_key = f"crypto_history:{normalized_coin_id}:{normalized_period}:{interval.lower()}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, MarketHistory):
            return cached

        self._ensure_available()
        url = f"{COINGECKO_BASE_URL}/coins/{normalized_coin_id}/market_chart"
        payload = await self._get_json(
            url,
            params={"vs_currency": "usd", "days": HISTORY_DAYS_BY_PERIOD[normalized_period], "interval": "daily"},
        )
        prices = payload.get("prices")
        if not isinstance(prices, list) or not prices:
            raise ProviderMalformedResponseError(f"CoinGecko did not return market chart prices for {normalized_coin_id}.")

        points = [
            MarketHistoryPoint(
                observed_at=_epoch_ms_to_datetime(item[0]),
                close=_decimal_from_any(item[1]) or Decimal("0"),
            )
            for item in prices
            if isinstance(item, list) and len(item) >= 2 and _decimal_from_any(item[1]) is not None
        ]
        if not points:
            raise ProviderMalformedResponseError(f"CoinGecko history for {normalized_coin_id} did not contain prices.")

        retrieved_at = utc_now()
        history = MarketHistory(
            provider_name=self.name,
            provider_status="healthy",
            symbol=normalized_coin_id,
            asset_type="crypto",
            period=normalized_period,
            interval="1d",
            currency="USD",
            points=points,
            data_as_of=points[-1].observed_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://www.coingecko.com/en/coins/{normalized_coin_id}",
            data_limitations=self.data_limitations,
        )
        self.cache.set(cache_key, history)
        self._record_success()
        return history

    async def _get_json(self, url: str, *, params: dict[str, str]) -> dict[str, Any]:
        try:
            if self._client is not None:
                response = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            self._record_error("provider_timeout", "CoinGecko request timed out.")
            raise ProviderUnavailableError("CoinGecko request timed out.") from exc
        except httpx.HTTPError as exc:
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError("CoinGecko request failed.") from exc

        if response.status_code == 429:
            self._record_error("provider_rate_limited", "CoinGecko public endpoint is rate limited.")
            raise ProviderRateLimitError("CoinGecko public endpoint is rate limited.")
        if response.status_code >= 400:
            self._record_error("provider_unavailable", f"CoinGecko returned HTTP {response.status_code}.")
            raise ProviderUnavailableError(f"CoinGecko returned HTTP {response.status_code}.")
        return response.json()


def _normalize_coin_id(value: str) -> str:
    alias = value.strip().lower()
    if alias not in COIN_ID_BY_ALIAS:
        raise ProviderInvalidSymbolError("Unsupported crypto identifier. Use an allowlisted public CoinGecko id or symbol.")
    return COIN_ID_BY_ALIAS[alias]


def _decimal_from_any(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _epoch_to_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=UTC)
    except (ValueError, TypeError, OSError):
        return None


def _epoch_ms_to_datetime(value: Any) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)


def _safe_raw(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if isinstance(value, str | int | float | bool) or value is None}
