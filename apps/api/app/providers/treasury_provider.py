from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderMalformedResponseError, ProviderUnavailableError
from app.providers.models import EconomicObservation, utc_now

TREASURY_AVG_RATES_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
)


class TreasuryProvider(BaseProvider):
    name = "treasury"
    display_name = "U.S. Treasury and Fiscal Data"
    capabilities = ("treasury_rates",)

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
                "Treasury and Fiscal Data endpoints are public official data sources.",
                "Rate datasets publish on a schedule and must not be labeled real-time.",
                "This endpoint provides government rate context, not personal investment advice.",
            ],
        )
        self._client = client

    async def get_treasury_rates(self) -> list[EconomicObservation]:
        cache_key = "treasury_rates:avg_interest_rates"
        cached = self.cache.get(cache_key)
        if isinstance(cached, list) and all(isinstance(item, EconomicObservation) for item in cached):
            return cached

        self._ensure_available()
        payload = await self._get_json(
            TREASURY_AVG_RATES_URL,
            params={
                "sort": "-record_date",
                "page[size]": "1",
                "fields": "record_date,security_type_desc,avg_interest_rate_amt",
            },
        )
        records = payload.get("data")
        if not isinstance(records, list) or not records:
            raise ProviderMalformedResponseError("Treasury Fiscal Data did not return rate records.")

        retrieved_at = utc_now()
        observations = []
        for record in records:
            value = _decimal_from_any(record.get("avg_interest_rate_amt"))
            observed_on = _date_from_any(record.get("record_date"))
            if value is None or observed_on is None:
                continue
            observations.append(
                EconomicObservation(
                    provider_name=self.name,
                    provider_status="healthy",
                    series_id="TREASURY_AVG_INTEREST_RATE",
                    label=str(record.get("security_type_desc") or "Average Treasury interest rate"),
                    value=value,
                    unit="percent",
                    observation_date=observed_on,
                    data_as_of=retrieved_at,
                    retrieved_at=retrieved_at,
                    is_stale=False,
                    is_sample_data=False,
                    data_quality="delayed",
                    confidence="high",
                    source_url=TREASURY_AVG_RATES_URL,
                    data_limitations=self.data_limitations,
                    raw_payload=_safe_raw(record),
                )
            )

        if not observations:
            raise ProviderMalformedResponseError("Treasury Fiscal Data rate records were malformed.")

        self.cache.set(cache_key, observations)
        self._record_success()
        return observations

    async def _get_json(self, url: str, *, params: dict[str, str]) -> dict[str, Any]:
        try:
            if self._client is not None:
                response = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            self._record_error("provider_timeout", "Treasury request timed out.")
            raise ProviderUnavailableError("Treasury request timed out.") from exc
        except httpx.HTTPError as exc:
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError("Treasury request failed.") from exc

        if response.status_code >= 400:
            self._record_error("provider_unavailable", f"Treasury returned HTTP {response.status_code}.")
            raise ProviderUnavailableError(f"Treasury returned HTTP {response.status_code}.")
        return response.json()


def _decimal_from_any(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _date_from_any(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _safe_raw(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if isinstance(value, str | int | float | bool) or value is None}
