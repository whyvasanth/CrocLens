from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any

import httpx

from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderInvalidSymbolError, ProviderMalformedResponseError, ProviderUnavailableError
from app.providers.models import EconomicObservation, utc_now

FRED_PUBLIC_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_LABELS = {
    "CPIAUCSL": ("Consumer Price Index", "index"),
    "FEDFUNDS": ("Effective federal funds rate", "percent"),
    "DGS10": ("10-year Treasury constant maturity rate", "percent"),
    "MORTGAGE30US": ("30-year fixed mortgage average", "percent"),
    "UNRATE": ("Unemployment rate", "percent"),
}


class FredProvider(BaseProvider):
    name = "fred"
    display_name = "FRED public CSV data"
    capabilities = ("macro_series", "treasury_rates")

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
                "FRED macroeconomic observations may be delayed or revised.",
                "FRED CSV data is public, but releases follow their own publication schedules.",
                "CrocLens shows macro context for education, not real-time trading decisions.",
            ],
        )
        self._client = client

    async def get_macro_observation(self, series_id: str) -> EconomicObservation:
        normalized_series_id = _normalize_series_id(series_id)
        cache_key = f"macro:{normalized_series_id}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, EconomicObservation):
            return cached

        self._ensure_available()
        text = await self._get_text(FRED_PUBLIC_CSV_URL, params={"id": normalized_series_id})
        observation = _parse_latest_observation(text, normalized_series_id)
        label, unit = SERIES_LABELS.get(normalized_series_id, (normalized_series_id, None))
        retrieved_at = utc_now()
        result = EconomicObservation(
            provider_name=self.name,
            provider_status="healthy",
            series_id=normalized_series_id,
            label=label,
            value=observation["value"],
            unit=unit,
            observation_date=observation["observation_date"],
            data_as_of=retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="high",
            source_url=f"https://fred.stlouisfed.org/series/{normalized_series_id}",
            data_limitations=self.data_limitations,
        )
        self.cache.set(cache_key, result)
        self._record_success()
        return result

    async def get_treasury_rates(self) -> list[EconomicObservation]:
        return [await self.get_macro_observation("DGS10")]

    async def _get_text(self, url: str, *, params: dict[str, str]) -> str:
        try:
            if self._client is not None:
                response = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            self._record_error("provider_timeout", "FRED request timed out.")
            raise ProviderUnavailableError("FRED request timed out.") from exc
        except httpx.HTTPError as exc:
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError("FRED request failed.") from exc

        if response.status_code >= 400:
            self._record_error("provider_unavailable", f"FRED returned HTTP {response.status_code}.")
            raise ProviderUnavailableError(f"FRED returned HTTP {response.status_code}.")
        return response.text


def _normalize_series_id(series_id: str) -> str:
    normalized = series_id.strip().upper()
    if not normalized or len(normalized) > 32 or not normalized.replace("_", "").isalnum():
        raise ProviderInvalidSymbolError("FRED series id must be an alphanumeric public series id.")
    return normalized


def _parse_latest_observation(text: str, series_id: str) -> dict[str, Any]:
    reader = csv.DictReader(StringIO(text))
    latest_date: date | None = None
    latest_value: Decimal | None = None
    for row in reader:
        raw_date = row.get("observation_date") or row.get("DATE") or row.get("date")
        raw_value = row.get(series_id)
        if raw_value in (None, "", ".") or raw_date is None:
            continue
        try:
            parsed_date = date.fromisoformat(raw_date)
            parsed_value = Decimal(str(raw_value))
        except (ValueError, InvalidOperation):
            continue
        latest_date = parsed_date
        latest_value = parsed_value

    if latest_date is None or latest_value is None:
        raise ProviderMalformedResponseError(f"FRED did not return observations for {series_id}.")

    return {"observation_date": latest_date, "value": latest_value}
