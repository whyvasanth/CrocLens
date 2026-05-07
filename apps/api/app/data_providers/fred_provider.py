from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
import json

from app.core.config import settings
from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.errors import ProviderConfigurationError, ProviderUnavailableError
from app.data_providers.schemas import NormalizedDataPoint


class FredProvider(BaseDataProvider):
    provider_id = "fred"
    display_name = "FRED macroeconomic data"
    source_type = "official_macro_data"
    capabilities = ["macro_series"]
    requires_api_key = True
    cost_note = "Free API key required from FRED."
    limitations = [
        "Macro data can be delayed, revised, and reported at monthly or quarterly frequency.",
        "FRED series values are context, not personalized financial advice.",
    ]

    def is_configured(self) -> bool:
        return bool(settings.fred_api_key)

    def get_macro_series(self, series_id: str) -> NormalizedDataPoint:
        if not settings.fred_api_key:
            raise ProviderConfigurationError("FRED_API_KEY is not configured.")

        params = urlencode(
            {
                "series_id": series_id.upper(),
                "api_key": settings.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": "1",
            }
        )
        url = f"https://api.stlouisfed.org/fred/series/observations?{params}"

        try:
            with urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ProviderUnavailableError(f"FRED lookup failed for {series_id}: {exc}") from exc

        observations = payload.get("observations") or []
        if not observations:
            raise ProviderUnavailableError(f"FRED returned no observations for {series_id}.")

        latest = observations[0]
        try:
            value = float(latest["value"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderUnavailableError(f"FRED latest observation is not numeric for {series_id}.") from exc

        return NormalizedDataPoint(
            provider=self.provider_id,
            source_type="macro_series",
            asset_type="macro",
            symbol_or_series_id=series_id.upper(),
            value=value,
            currency=None,
            as_of=datetime.fromisoformat(latest["date"]).replace(tzinfo=utc_now().tzinfo),
            retrieved_at=utc_now(),
            source_url=f"https://fred.stlouisfed.org/series/{series_id.upper()}",
            freshness="FRED observation frequency depends on the selected series",
            confidence="high",
            limitations=self.limitations,
            raw_payload=latest,
        )
